import os

# =============================================
# OPTION 1: llama-cpp-python (Direct)
# =============================================
print("=" * 50)
print("OPTION 1: llama-cpp-python")
print("=" * 50)

try:
    from llama_cpp import Llama
    print("✅ llama-cpp-python is installed!")
except ImportError:
    print("❌ llama-cpp-python not installed")
    print("Install with: pip install llama-cpp-python")

# =============================================
# OPTION 2: LM Studio
# =============================================
print("\n" + "=" * 50)
print("OPTION 2: LM Studio")
print("=" * 50)

# =============================================
# OPTION 3: Ollama (what we use now)
# =============================================
print("\n" + "=" * 50)
print("OPTION 3: Ollama (Current)")
print("=" * 50)

# =============================================
# Unified LLM Interface (Pi Philosophy)
# =============================================
print("\n" + "=" * 50)
print("Unified Interface (like pi-ai)")
print("=" * 50)

def call_llm_unified(prompt,provider="ollama",model="llama3.2:3b"):
    import requests

    if provider=="ollama":
        response=requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model":model,
                "messages": [{"role": "user","content": prompt}],
                "stream": False
            },
            timeout=60
        )
        return response.json()['message']['content']
    elif provider=="llmstudio":
        response=requests.post(
            "http://localhost:1234/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Unknown provider: {provider}"
# =============================================
# Test the unified interface
# =============================================
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Testing LLM Providers")
    print("=" * 50)
    
    # Test Ollama (current)
    print("\n1. Testing Ollama...")

    try:
        result = call_llm_unified("Say 'Hello from Ollama' in 3 words")
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Error: {e}")

# Test LM Studio (if running)
    print("\n2. Testing LM Studio...")
    print("   (Start LM Studio server first to test)")
    try:
        result=call_llm_unified("Say 'Hello from LM Studio' in 3 words", provider="llmstudio")
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Error: {e}")
