"""
langchain_step5.py - LangChain Step by Step
Step 5: Tools and Agents (Simplified & Stable)

Tools: Functions an LLM can call
Agents: LLM decides WHICH tool to use
"""
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

# =============================================
# Connect to Ollama
# =============================================
llm = ChatOllama(model="llama3.2:3b", temperature=0.3)

# =============================================
# STEP 1: Define Tools
# =============================================
print("=" * 50)
print("STEP 1: Define Tools")
print("=" * 50)

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool  
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query} (simulated)"

tools = [multiply, add, search_web]

print(f"Defined {len(tools)} tools:")
for t in tools:
    print(f"  - {t.name}: {t.description}")


# =============================================
# STEP 2: Bind Tools to LLM
# =============================================
print("\n" + "=" * 50)
print("STEP 2: Bind Tools to LLM")
print("=" * 50)

# Key method: bind_tools() gives LLM tool knowledge
llm_with_tools = llm.bind_tools(tools)

# Test - ask a math question
response = llm_with_tools.invoke("What is 5 times 3?")
print(f"Question: What is 5 times 3?")
print(f"Response: {response.content}")
print(f"Tool calls: {response.tool_calls}")


# =============================================
# STEP 3: Simple Tool Executor
# =============================================
print("\n" + "=" * 50)
print("STEP 3: Execute Tool Calls")
print("=" * 50)

def execute_tool(tool_call):
    """Execute a single tool call"""
    tool_name = tool_call['name']
    args = tool_call['args']
    
    for t in tools:
        if t.name == tool_name:
            return t.invoke(args)
    return "Tool not found"

def agent(question):
    """Simple agent: get LLM response, execute tools if needed"""
    # Get LLM response
    response = llm_with_tools.invoke(question)
    
    # Check for tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        results = []
        for tc in response.tool_calls:
            result = execute_tool(tc)
            results.append(f"{tc['name']}: {result}")
        return "\n".join(results)
    
    # No tool, just return response
    return response.content

# Test
print("\nTesting agent:")
print(f"Q: What is 12 + 8?")
print(f"A: {agent('What is 12 plus 8?')}")

print(f"\nQ: What is 5 times 7?")
print(f"A: {agent('What is 5 times 7?')}")


# =============================================
# STEP 4: Compare with Your Agent
# =============================================
print("\n" + "=" * 50)
print("STEP 4: Compare with Your Agent")
print("=" * 50)

print("""
LangChain vs Your agent_v9:

LangChain:
- @tool decorator
- llm.bind_tools(tools)
- Check response.tool_calls

Your agent_v9:
- tools = {"name": method}
- plan() decides tool
- act() executes tool

SAME CONCEPT, different style!
""")


# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)

print("""
Key LangChain Concepts:

1. @tool → creates tool from function
2. bind_tools() → LLM knows available tools
3. response.tool_calls → LLM wants to use a tool
4. tool.invoke(args) → execute the tool

Your agent_v9 does all this already!
""")
