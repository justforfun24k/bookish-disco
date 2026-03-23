import sys

original_import = __builtins__.__import__

def tracing_import(name, *args, **kwargs):
    if 'copy' in name.lower() and 'copy.py' not in name.lower():
        import traceback
        print(f">>> IMPORT: {name}")
        traceback.print_stack(limit=5)
    return original_import(name, *args, **kwargs)

__builtins__.__import__ = tracing_import

print("START")
import requests
print("AFTER REQUESTS")
