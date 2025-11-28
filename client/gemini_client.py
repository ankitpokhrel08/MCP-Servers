import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
import json
import os

load_dotenv()


# Note: langchain-google-genai looks for GEMINI_API_KEY or GOOGLE_API_KEY
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = gemini_key

SERVERS = { 
    # This is the local math server configuration
    "math": {
        "transport": "stdio",
        "command": "/Library/Frameworks/Python.framework/Versions/3.13/bin/uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "/Users/ankitpokhrel/Downloads/All_projects/ML_Projects/MCP_server/math_server.py"
       ]
    },
    # This is the deployed expense server configuration
    "expense": {
        "transport": "streamable_http",  # if this fails, try "sse"
        "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
    },
    # This is the local manim server configuration
    "manim-server": {
      "transport": "stdio",
      "command": "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
      "args": [
        "/Users/ankitpokhrel/Desktop/manim-mcp-server/src/manim_server.py"
      ],
      "env": {
        "MANIM_EXECUTABLE": "/Library/Frameworks/Python.framework/Versions/3.13/bin/manim"
      }
    },
}


#Declaring the main function as async; this is main step
async def main():
    
    #Creating instance of MultiServerMCPClient with SERVERS dictionary
    client = MultiServerMCPClient(SERVERS)

    #Fetching the available tools from the MCP servers
    tools = await client.get_tools()

    #print(tools) # Uncomment this line to see the fetched tools

    # Creating a dictionary to map tool names to tool instances
    named_tools = {}
    for tool in tools:
        named_tools[tool.name] = tool

    print("Available tools:", named_tools.keys())


    # Creating an instance of ChatGoogleGenerativeAI to use Gemini
    # Using gemini-2.0-flash which is free and stable (NOT the experimental version)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    prompt = "Give me all details of the expense summary. "
    response = await llm_with_tools.ainvoke(prompt)

    if not getattr(response, "tool_calls", None):
        print("\nLLM Reply:", response.content)
        return

    tool_messages = []
    for tc in response.tool_calls:
        selected_tool = tc["name"]
        selected_tool_args = tc.get("args") or {}
        selected_tool_id = tc["id"]

        result = await named_tools[selected_tool].ainvoke(selected_tool_args)
        tool_messages.append(ToolMessage(tool_call_id=selected_tool_id, content=json.dumps(result)))
        

    final_response = await llm_with_tools.ainvoke([prompt, response, *tool_messages])
    print(f"Final response: {final_response.content}")

# Run the main function
if __name__ == '__main__':
    asyncio.run(main())