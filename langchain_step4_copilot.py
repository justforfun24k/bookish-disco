"""
langchain_step4_copilot.py - LangChain Step by Step (Copilot Version)
Step 4: LCEL Chains (LangChain Expression Language)

LCEL allows chaining components with the | operator:
- Automatic data flow
- Async support
- Easy debugging
- Reusable chains
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# =============================================
# Connect to Ollama
# =============================================
llm = ChatOllama(model="tinyllama:latest", temperature=0.3)

# =============================================
# STEP 1: Basic LCEL Chain
# =============================================
print("=" * 50)
print("STEP 1: Basic LCEL Chain")
print("=" * 50)

# Create a simple chain: prompt -> llm -> output parser
prompt = PromptTemplate.from_template("Tell me a joke about {topic}")
chain = prompt | llm | StrOutputParser()

response = chain.invoke({"topic": "programming"})
print(f"Joke: {response}")

# =============================================
# STEP 2: Multi-step Chain
# =============================================
print("\n" + "=" * 50)
print("STEP 2: Multi-step Chain")
print("=" * 50)

# Chain: generate idea -> summarize -> format
idea_prompt = PromptTemplate.from_template("Generate a creative idea for a {project_type} project")
summary_prompt = PromptTemplate.from_template("Summarize this idea in 2 sentences: {idea}")
format_prompt = PromptTemplate.from_template("Format this as a bullet list: {summary}")

# Create the chain
multi_chain = idea_prompt | llm | StrOutputParser() | summary_prompt | llm | StrOutputParser() | format_prompt | llm | StrOutputParser()

response = multi_chain.invoke({"project_type": "AI chatbot"})
print(f"Final result:\n{response}")

# =============================================
# STEP 3: RunnablePassthrough for data flow
# =============================================
print("\n" + "=" * 50)
print("STEP 3: RunnablePassthrough")
print("=" * 50)

from langchain_core.runnables import RunnablePassthrough

# Pass data through unchanged
def add_metadata(x):
    return {"response": x, "timestamp": "2024-01-01", "source": "AI"}

# Chain with passthrough
chain_with_meta = prompt | llm | StrOutputParser() | RunnablePassthrough() | add_metadata

response = chain_with_meta.invoke({"topic": "cats"})
print(f"Response with metadata: {response}")

# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print("""
LCEL Chains:
1. Use | to chain components
2. Data flows automatically between steps
3. Supports async with .ainvoke()
4. RunnablePassthrough for data manipulation

Benefits:
- Cleaner code than manual chaining
- Better error handling
- Easier debugging with .stream() or .batch()

Next Steps:
- Step 5: Tools and Agents
- Step 6: Memory and Conversation
""")