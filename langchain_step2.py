"""
langchain_step2.py - LangChain Step by Step
Step 2: Connect to Ollama LLM
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

# =============================================
# STEP 1: Connect to Ollama
# =============================================
print("=" * 50)
print("STEP 1: Connect to Ollama")
print("=" * 50)

# Create a ChatOllama instance
llm = ChatOllama(
    model="tinyllama:latest",
    temperature=0.7,
)

print(f"Connected to Ollama with model: {llm.model}")


# =============================================
# STEP 2: Simple LLM Call
# =============================================
print("\n" + "=" * 50)
print("STEP 2: Simple LLM Call")
print("=" * 50)

# Call the LLM directly
response = llm.invoke("What is Python?")
print(f"Response: {response.content}")


# =============================================
# STEP 3: Using Messages (Chat Style)
# =============================================
print("\n" + "=" * 50)
print("STEP 3: Chat with Messages")
print("=" * 50)

from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="You are a helpful coding assistant."),
    HumanMessage(content="Write a hello world in Python")
]

response = llm.invoke(messages)
print(f"Response: {response.content}")


# =============================================
# STEP 4: PromptTemplate + LLM
# =============================================
print("\n" + "=" * 50)
print("STEP 4: PromptTemplate + LLM")
print("=" * 50)

template = "Explain {concept} in one sentence."
prompt = PromptTemplate.from_template(template)

# Format the prompt
formatted_prompt = prompt.format(concept="recursion")

# Call LLM
response = llm.invoke(formatted_prompt)
print(f"Prompt: {formatted_prompt}")
print(f"Response: {response.content}")


# =============================================
# STEP 5: Simple Chain (| operator)
# =============================================
print("\n" + "=" * 50)
print("STEP 5: Chain (|)")
print("=" * 50)

# Chain = PromptTemplate | LLM
chain = prompt | llm

response = chain.invoke({"concept": "API"})
print(f"Response: {response.content}")


# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print("""
We learned:
1. Connect to Ollama with ChatOllama
2. Call LLM with invoke()
3. Use messages (SystemMessage, HumanMessage)
4. Use PromptTemplate for dynamic prompts
5. Chain components with | operator

Next Steps:
- Step 3: Output Parsers
- Step 4: Chains (LCEL)
- Step 5: Tools and Agents
""")
