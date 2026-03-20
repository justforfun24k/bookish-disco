"""
opencode_agent_original.py - Step 3: Search and Find (with notes)

This is the original version with search tools and the dirs[:] note.

NOTE: dirs[:] vs dirs = ...
- dirs = ... creates a NEW list (original dirs unchanged)
- dirs[:] = ... MODIFIES the ORIGINAL list
- os.walk() uses the original dirs list, so use dirs[:] to control which dirs it descends into
"""
import os
import re

# =============================================
# Tool 1: Grep - Search in Files
# =============================================
def grep(pattern, path=".", file_pattern="*", case_sensitive=False):
    """Search for pattern in files"""
    results = []
    
    # Set regex flags
    if not case_sensitive:
        pattern = pattern.lower()
    
    for root, dirs, files in os.walk(path):
        # NOTE: dirs creates a NEW list
        # while dirs[:] modifies the ORIGINAL list (used by os.walk)
        # Use dirs[:] not dirs = ... to prevent os.walk entering '.git','.venv' etc dirs
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'node_modules'}]
        
        for filename in files:
            # Check file pattern
            if file_pattern != "*":
                if not re.match(file_pattern.replace("*", ".*"), filename):
                    continue
            
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        search_line = line if case_sensitive else line.lower()
                        
                        if pattern in search_line:
                            results.append({
                                "file": filepath,
                                "line": line_num,
                                "content": line.rstrip()
                            })
            except:
                continue
    
    return results


# =============================================
# Tool 2: Find Files by Name
# =============================================
def find_files(name_pattern, path=".", case_sensitive=False):
    """Find files by name pattern"""
    results = []
    
    # Convert to regex
    pattern = name_pattern.replace("*", ".*").replace("?", ".")
    if not case_sensitive:
        pattern = pattern.lower()
    
    regex = re.compile(pattern)
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv'}]  # [:] modifies original list
        
        for filename in files:
            search_name = filename if case_sensitive else filename.lower()
            
            if regex.match(search_name):
                results.append(os.path.join(root, filename))
    
    return results


# =============================================
# Tool 3: Find Functions/Classes
# =============================================
def find_definitions(path=".", language="python"):
    """Find function and class definitions"""
    results = []
    
    patterns = {
        "python": [
            (r'^def\s+(\w+)', 'function'),
            (r'^class\s+(\w+)', 'class'),
            (r'^async\s+def\s+(\w+)', 'async function'),
        ],
        "javascript": [
            (r'function\s+(\w+)', 'function'),
            (r'const\s+(\w+)\s*=', 'const'),
            (r'let\s+(\w+)\s*=', 'let'),
            (r'class\s+(\w+)', 'class'),
        ],
    }
    
    lang_patterns = patterns.get(language, patterns["python"])
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv'}]  # [:] modifies original list
        
        for filename in files:
            if language == "python" and not filename.endswith('.py'):
                continue
            if language == "javascript" and not filename.endswith('.js'):
                continue
            
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, def_type in lang_patterns:
                            if re.match(pattern, line.strip()):
                                results.append({
                                    "file": filepath,
                                    "line": line_num,
                                    "type": def_type,
                                    "name": re.match(pattern, line.strip()).group(1)
                                })
            except:
                continue
    
    return results


# =============================================
# Tool 4: Get Project Structure
# =============================================
def get_project_structure(path=".", max_depth=3):
    """Get a summary of the project structure"""
    structure = {
        "root": path,
        "languages": {},
        "total_files": 0,
        "total_dirs": 0,
    }
    
    # Language extensions
    lang_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.go': 'Go',
        '.rs': 'Rust',
        '.html': 'HTML',
        '.css': 'CSS',
        '.json': 'JSON',
        '.md': 'Markdown',
    }
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'node_modules'}]  # [:] modifies original list
        structure["total_dirs"] += len(dirs)
        
        for filename in files:
            structure["total_files"] += 1
            
            ext = os.path.splitext(filename)[1]
            lang = lang_map.get(ext, 'Other')
            structure["languages"][lang] = structure["languages"].get(lang, 0) + 1
    
    return structure


# =============================================
# Test the tools
# =============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Testing Search Tools")
    print("=" * 50)
    
    # Test grep
    print("\n1. Search for 'def' in files:")
    results = grep("def", path=".", file_pattern="*.py")[:3]
    for r in results:
        print(f"   {r['file']}:{r['line']} - {r['content'][:50]}")
    
    # Test find_files
    print("\n2. Find Python files:")
    files = find_files("*.py", path=".")[:5]
    for f in files:
        print(f"   {f}")
    
    # Test find_definitions
    print("\n3. Find functions/classes:")
    results = find_definitions(path=".", language="python")[:5]
    for r in results:
        print(f"   {r['file']}:{r['line']} - {r['type']}: {r['name']}")
    
    # Test project structure
    print("\n4. Project structure:")
    struct = get_project_structure(path=".")
    print(f"   Total files: {struct['total_files']}")
    print(f"   Languages: {struct['languages']}")
