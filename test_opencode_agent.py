"""
Basic tests for opencode_agent
"""
import sys
import os


sys.path.insert(0, os.path.dirname(__file__))

def test_import():
    """Test that all tools can be imported"""
    from opencode_agent import read, write, edit, bash, Agent
    assert callable(read)
    assert callable(write)
    assert callable(edit)
    assert callable(bash)
    assert callable(Agent)

def test_read_write():
    """Test basic read/write"""
    from opencode_agent import write, read
    
    # Test write
    result = write("test_ci.txt", "Hello CI!")
    assert result["ok"] == True
    
    # Test read
    result = read("test_ci.txt")
    assert "Hello CI!" in result["content"]
    
    # Cleanup
    os.remove("test_ci.txt")

def test_bash():
    """Test bash command"""
    from opencode_agent import bash
    
    result = bash("echo Hello")
    assert "Hello" in result["stdout"]

if __name__ == "__main__":
    test_import()
    test_read_write()
    test_bash()
    print("All tests passed!")
