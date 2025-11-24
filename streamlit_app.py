import streamlit as st
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage, SystemMessage
import json
import os
import nest_asyncio

# Load environment variables
load_dotenv()

# Allow nested event loops (fixes Streamlit asyncio issues)
nest_asyncio.apply()

# Create and store a single event loop for the entire session
if "event_loop" not in st.session_state:
    try:
        st.session_state.event_loop = asyncio.get_event_loop()
    except RuntimeError:
        st.session_state.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(st.session_state.event_loop)

def run_async(coro):
    """Helper function to run async code in Streamlit using session's event loop"""
    loop = st.session_state.event_loop
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        st.session_state.event_loop = loop
    return loop.run_until_complete(coro)

# Page configuration
st.set_page_config(
    page_title="MCP Multi-Server Chat",
    page_icon="",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Get the Gemini API key from .env file
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = gemini_key

# Server configurations
SERVERS = { 
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
    "expense": {
        "transport": "streamable_http",
        "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
    },
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

SYSTEM_PROMPT = (
    "You have access to tools. When you choose to call a tool, do not narrate status updates. "
    "After tools run, return only a concise final answer."
)

st.title("🧰 MCP Multi-Server Chat")

# One-time initialization
if "initialized" not in st.session_state:
    with st.spinner("🚀 Initializing MCP servers..."):
        try:
            # 1) LLM
            st.session_state.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

            # 2) MCP tools
            st.session_state.client = MultiServerMCPClient(SERVERS)
            tools = run_async(st.session_state.client.get_tools())
            st.session_state.tools = tools
            st.session_state.tool_by_name = {t.name: t for t in tools}

            # 3) Bind tools
            st.session_state.llm_with_tools = st.session_state.llm.bind_tools(tools)

            # 4) Conversation state
            st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
            st.session_state.initialized = True
            
            st.success("✅ Servers initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize: {str(e)}")
            st.stop()


# Sidebar
with st.sidebar:
    st.header("�️ Available Tools")
    if st.session_state.get("tool_by_name"):
        for tool_name in st.session_state.tool_by_name.keys():
            st.markdown(f"• `{tool_name}`")
    
    st.markdown("---")
    st.header("� Example Prompts")
    st.markdown("""
    **Math:**
    - Add 25 and 17
    - Calculate 15 raised to power 3
    - Divide 100 by 4
    
    **Expense:**
    - Show expense summary
    - List all expenses
    - Add expense
    
    **Manim:**
    - Create a circle animation
    - Animate a rotating square
    """)
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
        st.rerun()

# Render chat history (skip system + tool messages; hide intermediate AI with tool_calls)
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        # Skip assistant messages that contain tool_calls (intermediate "fetching…")
        if getattr(msg, "tool_calls", None):
            continue
        with st.chat_message("assistant"):
            st.markdown(msg.content)
    # ToolMessage and SystemMessage are not rendered as bubbles

# Chat input
user_text = st.chat_input("Type a message… (math, expenses, animations)")
if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)
    st.session_state.history.append(HumanMessage(content=user_text))

    with st.spinner("Thinking..."):
        try:
            # Create a new async function to handle the conversation
            async def process_conversation():
                # First pass: let the model decide whether to call tools
                first = await st.session_state.llm_with_tools.ainvoke(st.session_state.history)
                tool_calls = getattr(first, "tool_calls", None)

                if not tool_calls:
                    # No tools → return assistant reply
                    return first, None
                else:
                    # ── IMPORTANT ORDER ──
                    # 1) Append assistant message WITH tool_calls
                    st.session_state.history.append(first)

                    # 2) Execute requested tools and append ToolMessages
                    tool_msgs = []
                    for tc in tool_calls:
                        name = tc["name"]
                        args = tc.get("args") or {}
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except Exception:
                                pass
                        tool = st.session_state.tool_by_name[name]
                        res = await tool.ainvoke(args)
                        tool_msgs.append(ToolMessage(tool_call_id=tc["id"], content=json.dumps(res)))

                    st.session_state.history.extend(tool_msgs)

                    # 3) Final assistant reply using tool outputs
                    final = await st.session_state.llm.ainvoke(st.session_state.history)
                    return final, first
            
            # Run the async function
            result, intermediate = run_async(process_conversation())
            
            if intermediate is None:
                # No tools were called
                with st.chat_message("assistant"):
                    st.markdown(result.content or "")
                st.session_state.history.append(result)
            else:
                # Tools were called, show final result
                with st.chat_message("assistant"):
                    st.markdown(result.content or "")
                st.session_state.history.append(AIMessage(content=result.content or ""))
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Powered by MCP Servers • Gemini 2.0 Flash • Streamlit"
    "</div>", 
    unsafe_allow_html=True
)
