"""
step1_basics.py - Pi-Style Agent Basics

Based on Pi coding agent by Mario Zechner
Only 4 core tools - everything else is optional

Core Tools:
1. read  - Read a file
2. write - Write to a file
3. edit  - Edit a file
4. bash  - Run a command

Philosophy: Less tools = more autonomy for AI
"""
import os
import subprocess

# =============================================
# Tool 1: Read File
# =============================================
def read(filepath, limit=100, offset=0):
    """
    Read a file.
    
    Args:
        filepath: Path to file
        limit: Number of lines to read (default 100)
        offset: Line offset to start from (default 0)
    
    Returns:
        Dict with content and info
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        selected = lines[offset:offset+limit]
        
        return {
            "ok": True,
            "content": "".join(selected),
            "total_lines": total,
            "showing": f"lines {offset+1}-{offset+len(selected)}"
        }
    except FileNotFoundError:
        return {"ok": False, "error": f"File not found: {filepath}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =============================================
# Tool 2: Write File
# =============================================
def write(filepath, content):
    """
    Write content to a file.
    
    Args:
        filepath: Path to file
        content: Content to write
    
    Returns:
        Dict with success/error
    """
    try:
        # Create directory if needed
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"ok": True, "filepath": filepath}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =============================================
# Tool 3: Edit File
# =============================================
def edit(filepath, old_string, new_string):
    """
    Edit a file by replacing old_string with new_string.
    
    Args:
        filepath: Path to file
        old_string: String to find and replace
        new_string: String to replace with
    
    Returns:
        Dict with success/error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_string not in content:
            return {"ok": False, "error": "String not found in file"}
        
        new_content = content.replace(old_string, new_string)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return {"ok": True, "filepath": filepath}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =============================================
# Tool 4: Bash/Shell Command
# =============================================
def bash(command, timeout=30):
    """
    Run a shell command.
    
    Args:
        command: Command to run
        timeout: Timeout in seconds (default 30)
    
    Returns:
        Dict with stdout, stderr, returncode
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "ok": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timeout"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =============================================
# All Tools in One Dict (like Pi)
# =============================================
tools = {
    "read": read,
    "write": write,
    "edit": edit,
    "bash": bash,
}


# =============================================
# Execute Tool by Name
# =============================================
def execute_tool(tool_name, args):
    """Execute a tool by name with args dict"""
    if tool_name == "read":
        return read(**args)
    elif tool_name == "write":
        return write(**args)
    elif tool_name == "edit":
        return edit(**args)
    elif tool_name == "bash":
        return bash(**args)
    else:
        return {"ok": False, "error": f"Unknown tool: {tool_name}"}


# =============================================
# Test the Tools
# =============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Step 1: Pi-Style Agent - 4 Basic Tools")
    print("=" * 50)
    print("""
Pi Philosophy:
- 4 tools is enough
- read, write, edit, bash
- AI can do anything with these
- Less tools = more autonomy
    """)
    
    # Test read
    print("\n1. Test read:")
    result = read("step1_basics.py", limit=5)
    print(f"   OK: {result.get('ok')}")
    print(f"   Preview: {result.get('content', '')[:50]}...")
    
    # Test write
    print("\n2. Test write:")
    result = write("test_step1.txt", "Hello from Step 1!")
    print(f"   OK: {result.get('ok')}")
    
    # Test read new file
    print("\n3. Read new file:")
    result = read("test_step1.txt")
    print(f"   Content: {result.get('content')}")
    
    # Test bash
    print("\n4. Test bash:")
    result = bash("echo Hello from bash!")
    print(f"   Output: {result.get('stdout').strip()}")
    
    # Test edit
    print("\n5. Test edit:")
    edit("test_step1.txt", "Hello", "Hi")
    result = read("test_step1.txt")
    print(f"   After edit: {result.get('content')}")
    
    # Cleanup
    bash("del test_step1.txt")
    
    print("\n" + "=" * 50)
    print("All tools work! Step 1 complete.")
    print("=" * 50)


# =============================================
# Summary
# =============================================
print("""
==================================================
Step 1 Summary: 4 Basic Tools
==================================================

What we learned:
- Pi-style agent needs only 4 tools
- read: Read files
- write: Write files
- edit: Edit files
- bash: Run commands

Why 4 tools?
- AI can do anything with these
- read learns from code/docs
- write creates anything
- bash executes anything
- edit modifies anything

Philosophy:
"Less tools = more autonomy"

Next: Step 2 - Connect to LLM
""")
