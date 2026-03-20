from langsmith import Client
client = Client()
public_prompt = client.pull_prompt("rlm/rag-prompt")  # Example