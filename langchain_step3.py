"""
langchain_step3.py - LangChain Step by Step
Step 3: Output Parsers

Output Parsers force LLM output into specific formats:
- JSON
- List
- Custom structure
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, CommaSeparatedListOutputParser

# =============================================
# Connect to Ollama
# =============================================
llm = ChatOllama(model="tinyllama:latest", temperature=0.3)

# =============================================
# STEP 1: JsonOutputParser
# =============================================
print("=" * 50)
print("STEP 1: JSON Output Parser")
print("=" * 50)

# Define the structure we want
parser = JsonOutputParser()

# Create a prompt that asks for JSON
template = """Answer the question.
Format your response as JSON with this structure:
{format_instructions}

Question: {question}"""

prompt = PromptTemplate.from_template(template)

# Combine prompt + llm + parser into a chain
chain = prompt | llm | parser

# Now the output is a Python dictionary!
response = chain.invoke({
    "question": "What are 3 programming languages?",
    "format_instructions": parser.get_format_instructions()
})

print(f"Type: {type(response)}")
print(f"Response: {response}")
print(f"First language: {response.get('languages', [])[0]}")


# =============================================
# STEP 2: CommaSeparatedListOutputParser
# =============================================
print("\n" + "=" * 50)
print("STEP 2: List Output Parser")
print("=" * 50)

list_parser = CommaSeparatedListOutputParser()

template = """List {item} separated by commas.
{format_instructions}"""

prompt = PromptTemplate.from_template(template)

chain = prompt | llm | list_parser

response = chain.invoke({
    "item": "3 colors",
    "format_instructions": list_parser.get_format_instructions()
})

print(f"Type: {type(response)}")
print(f"Response: {response}")


# =============================================
# STEP 3: Custom Output Parser (Simple)
# =============================================
print("\n" + "=" * 50)
print("STEP 3: Simple Custom Parser")
print("=" * 50)

from langchain_core.output_parsers import BaseOutputParser

class NumberedListParser(BaseOutputParser):
    """Parse output like '1. item1 2. item2' into list"""
    
    def parse(self, text):
        # Split by numbers at start of line
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove the number/bullet
                cleaned = line.lstrip('0123456789.-) ').strip()
                if cleaned:
                    items.append(cleaned)
        return items

parser = NumberedListParser()

response = llm.invoke("List 3 fruits, one per line starting with number")
result = parser.parse(response.content)

print(f"Raw: {response.content}")
print(f"Parsed: {result}")


# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print("""
Output Parsers:
1. JsonOutputParser - Force JSON output
2. CommaSeparatedListOutputParser - Force list
3. Custom BaseOutputParser - Any format you want

Chain: prompt | llm | parser
- Output flows from one to next
- Parser transforms LLM text → structured data

Next Steps:
- Step 4: LCEL Chains (advanced)
- Step 5: Tools and Agents
""")
