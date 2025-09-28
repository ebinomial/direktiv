# MIT License

# Copyright (c) 2025 Erdenebileg Byambadorj

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import json
import logging

from jinja2 import Template
from typing import List, Dict, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from utils.model_management import setup_client, generate_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class StdioClient:

    def __init__(self, model_name: str, api_key: str):
        self.client: Optional[MultiServerMCPClient] = None
        self.model_client = setup_client(api_key)
        self.model_name = model_name
        self.system = """
You are a legal AI agent responsible for rigorous interpretation and search for information to the user query given further down. You function according to ReAct (i.e. Reason and Act) principle, in which you first think regarding the user query, act by choosing a tool in your arsenal and observe the response resulting from the tool until you formed your final response.

Now you're strictly constrained to following the protocol detailed from here on:

Step 1. Language Constraints: Your `rationale` should be in English since you orchestrate and reason your plans in English. But your messages to display to users must be in Mongolian language assuming your target audience to be Mongolians.

Step 2. Decision Framework:

Step 2.1.   Because you're a legal agent users consult you must respond to the questions not related to law and regulations by stating you cannot help them with their request and suggest the user to ask something in legal subjects.
Step 2.2.   If user sought legal guidance and the question pertains to 'private data protection' (i.e. Хувь хүний мэдээлэл хамгаалах тухай in Mongolian) in particular, then you should inspect the vector database for better contextualization in order to form your response more precisely and accurately.
Step 2.3.   Depending on the context you have and the user query, you must choose your next step from between the following two options:
      
    (Option 2.4.a)  answer: If the response to the query is satisfied by virtue of the current context, then just respond directly. It also includes the scenario where user asked an irrelevant question as stated in Step 2.1. Assume this is the indicator that your actions are finalized.
    (Option 2.4.b)  tool: Or if you need to invoke a tool in your arsenal for additional context (vector database search or web search), you should call a tool. In case of tool calling you had better first consult your conversational context before executing a function, as it might put you in an indefinite loop. Keep this in mind because it's probably the most important step that could hinder your efficiency. For example, you might already possess weather information the user requested in your context already in your earlier tool use. But, you may get past it without inspection, resulting in a different call of the same tool.

    Regarding the complexity of user queries, it ranges from simply looking up the database for the context of text chunks to searching the web for better context for the retrieved documents. More specifically, assume an event where you have retrieved text documents from the database, in which there are references to the articles from the different law and regulations. In that case, you need to perform a web search to provide better comprehensibility to understand the text chunks from the database themselves. However, you're subject to the set of tools you're connected to, listed underneath. Hence, it's of most importance that you read the input schema descriptions of the tools forming your strategies, together with, again, paying special attention to your context that whether you may already have enough information to finally answer the query.

In case of tool invocation, the following list of tools should give enough background to contextualize you in available functions/tools you're able to carry out or request.
<tools>
{% for tool in tools %}
{{loop.index}}. Tool name: {{ tool.name }}
- Description: {{ tool.description }}
- Input Schema: {{ tool.inputSchema }}
{% endfor %}
</tools>

Step 3. Now, you must generate your final response. You are permitted to generate a JSON-only response, anything else is absolutely forbidden.
You are allowed to produce a JSON object with no code fences, explanations, or trailing commas included. Your output must be composed of the following keys:
{
    "rationale": "Brief justification for your next action in English, explicitly referring to the context and or tools used.",
    "decision": "answer" or "tool",
    "message_to_user": "If `decision` is set to `tool`, meaning you're calling a tool, then use non-technical language to describe what you're doing. For example 'Биометрик датаг хадгалах тухай өгөгдлийн сангаас хайж байна' or 'Биометрик дата хадгалалтыг Иргэний хуулийн 3.1-р зүйлээр зохицуулдаг юм байна. Иргэний хуулийн 3.1-р зүйлийг интернетээс хайж байна'. Otherwise, where `decision` is set to `answer`, it is your finalized response collecting all the context needed for answering the query. Keep it as long as you feel necessary, but do not overbloat it with unnecessary texts. Do not disclose anything private such as tool names or arguments here.",
    "tool": {
        "name": <tool_name chosen>,
        "args": {
            "<argument1>": <value1>,
            "<argument2>": <value2>
        }
    }
}
"""

    async def connect_to_servers(self, server_configs: Dict[str, Dict]) -> None:
        """
        Connect to multiple MCP servers using MultiServerMCPClient
        Args:
            server_configs: Dictionary mapping server names to their configurations
        """
        self.client = MultiServerMCPClient(server_configs)
        
        # Get all tools from all servers
        self.available_tools = await self.client.get_tools()
        logger.info(f"Available tools from all servers: {[tool.name for tool in self.available_tools]}")
        
        # Update system prompt with all available tools
        self.system = Template(self.system).render({"tools": self.available_tools})

    async def handle_request(self, context: List[Dict[str, str]]) -> None:
        """
        Multi-step (possibly) circulation to solve a single user request.
        In comparison to the single server MCP used in stdio_client.py it abstracts away
        the use of exit stack and sessions.

        Args:
            context (List[Dict[str, str]): User query currently in absence of context
        """

        is_process = True
        while is_process:
            
            raw_response_output = await generate_message(
                self.model_client,
                model=self.model_name,
                context=context
            )

            try:
                model_response = json.loads(raw_response_output)

                if model_response["decision"] == "tool":
                    if "tool" in model_response:
                        tool_name = model_response["tool"]["name"]
                        tool_args = model_response["tool"]["args"]

                        # Find and invoke the tool (works across all servers)
                        tool = next((t for t in self.available_tools if t.name == tool_name), None)
                        if tool:
                            tool_response = await tool.ainvoke(tool_args)
                            context.append({"role": "assistant", 
                                          "content": f"TOOL RESPONSE SAYS:\n{tool_response}"})
                        else:
                            context.append({"role": "assistant", 
                                          "content": f"Tool {tool_name} not found"})
                else:
                    is_process = False
                    return

            except ValueError as e:
                logging.error(f"Parsing error: {str(e)}")
                is_process=False

            except Exception as e:
                logging.error(f"Unexpected exception took place: {e}")
                is_process=False

    async def initiate_cycle(self) -> None:
        """
        Sets off the ReAct agent cycle by receiving user queries indefinitely.
        If user requests something that requires a series of actions and contemplating
        actions, the request handling method encapsulates those steps according to queries.
        In other words, the session to solve a single query is isolated in itself.
        """

        while True:
            try:
                query = input(">>> ").strip()

                if query.lower().strip() == "quit":
                    print(f"Quitting the interaction cycle...")
                    sys.exit(0)


                context = [
                    { "role" : "system" , "content" : self.system },
                    { "role" : "user", "content": query }
                ]

                response = await self.handle_request(context)
                print(f"Response: {response}\n")
            
            except Exception as e:
                print(f"Exception in the midst of interaction. {e}")