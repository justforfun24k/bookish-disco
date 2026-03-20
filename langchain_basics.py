"""
langchain_basics.py - LangChain Step by Step
Step 1: Understanding LLMs and Prompts

LangChain Basics:
- LLM: Language Model (like Ollama, OpenAI)
- Prompt: Input text to the LLM
- PromptTemplate: Reusable prompt patterns
"""
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# =============================================
# STEP 1: Simple Prompt
# =============================================
print("=" * 50)
print("STEP 1: Simple Prompt")
print("=" * 50)

# A simple prompt is just a string
prompt = "What is Python?"
print(f"Prompt: {prompt}")
# In LangChain, you'd pass this to an LLM


# =============================================
# STEP 2: PromptTemplate
# =============================================
print("\n" + "=" * 50)
print("STEP 2: PromptTemplate")
print("=" * 50)

# PromptTemplate lets you create dynamic prompts
template = "Explain {topic} in {level} terms."

prompt_template = PromptTemplate.from_template(template)

# Format the prompt with variables
formatted_prompt = prompt_template.format(topic="Python", level="simple")
print(f"Template: {template}")
print(f"Formatted: {formatted_prompt}")


# =============================================
# STEP 3: Multiple Variables
# =============================================
print("\n" + "=" * 50)
print("STEP 3: Multiple Variables")
print("=" * 50)

template = """You are a {role}.
Answer this question: {question}
Be {tone}."""

prompt_template = PromptTemplate.from_template(template)

formatted = prompt_template.format(
    role="math teacher",
    question="What is 2 + 2?",
    tone="friendly"
)
print(formatted)


# =============================================
# STEP 4: ChatPromptTemplate (for Chat Models)
# =============================================
print("\n" + "=" * 50)
print("STEP 4: ChatPromptTemplate")
print("=" * 50)

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Chat models use messages, not plain text
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is machine learning?"),
    AIMessage(content="Machine learning is..."),
    HumanMessage(content="Tell me more about neural networks.")
]

for msg in messages:
    print(f"{msg.type.upper()}: {msg.content[:50]}...")


# =============================================
# STEP 5: Chains - Connect Prompts to LLMs
# =============================================
print("\n" + "=" * 50)
print("STEP 5: Simple Chain")
print("=" * 50)

# A chain = Prompt -> LLM -> Output
# Example structure (won't run without Ollama):
"""
chain = prompt_template | llm | output_parser
result = chain.invoke({"topic": "AI"})
"""


# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 50)
print("SUMMARY - What We Learned")
print("=" * 50)
print("""
1. Prompt - Input text to LLM
2. PromptTemplate - Reusable prompt with variables
3. ChatPromptTemplate - For chat models (messages)
4. Chain - Connect components together

Next Steps:
- Step 2: Connect to Ollama (actual LLM)
- Step 3: Chains (LCEL)
- Step 4: Tools and Agents
- Step 5: Memory
""")
