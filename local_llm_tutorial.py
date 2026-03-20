"""
local_llm_tutorial.py - Running Local Large Language Models with Quantization

This tutorial shows how to:
1. Load a quantized LLM using transformers
2. Generate text responses
3. Handle memory efficiently for home computers
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

print("=" * 60)
print("LOCAL LLM TUTORIAL: Running Quantized Models")
print("=" * 60)

# =============================================
# PART 1: Setup Quantization Config
# =============================================
print("\nSetting up 4-bit quantization for efficiency...")

# Configure 4-bit quantization (reduces memory by ~75%)
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# =============================================
# PART 2: Load Model and Tokenizer
# =============================================
print("Loading model and tokenizer...")
print("Note: First run may download ~2-4GB. Subsequent runs are fast.")

# Use a small but capable model (Phi-2 is ~2.7B parameters)
model_name = "microsoft/phi-2"

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # Add padding token if missing
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map="auto",  # Automatically choose GPU/CPU
        trust_remote_code=True
    )

    print(f"Model loaded successfully on: {model.device}")
    print(f"Model size: {model.num_parameters():,} parameters")

except Exception as e:
    print(f"Error loading model: {e}")
    print("Make sure you have internet connection for first download.")
    exit()

# =============================================
# PART 3: Text Generation Function
# =============================================
def generate_response(prompt, max_length=200, temperature=0.7):
    """Generate text response from the model."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove the original prompt from response
    if response.startswith(prompt):
        response = response[len(prompt):].strip()

    return response

# =============================================
# PART 4: Interactive Chat
# =============================================
print("\n" + "=" * 40)
print("INTERACTIVE CHAT MODE")
print("=" * 40)
print("Type 'quit' to exit.")
print("The model will respond to your messages.")
print()

while True:
    user_input = input("You: ")
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Goodbye!")
        break

    # Create a conversational prompt
    prompt = f"Human: {user_input}\nAssistant:"

    print("AI: ", end="", flush=True)
    response = generate_response(prompt, max_length=150)
    print(response)

# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
Quantization Benefits:
- 4-bit reduces memory usage by ~75%
- Enables running large models on home computers
- Minimal performance loss

Key Components:
- BitsAndBytesConfig for quantization
- AutoModelForCausalLM for text generation
- device_map='auto' for optimal device placement

Next Steps:
- Try different models (Llama, Mistral, etc.)
- Experiment with parameters (temperature, max_length)
- Fine-tune for specific tasks
""")