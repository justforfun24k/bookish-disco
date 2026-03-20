import os
import json
import requests
import subprocess

def read(filepath,limit=100,offset=0):
    try:
        with open(filepath,'r',encoding='utf-8') as f:
            lines=f.readlines()
        total=len(lines)
        selected=lines[offset:offset+limit]

        return {
            "ok": True,
            "content": "".join(selected),
            "total_lines": total,
            "showing": f"lines {offset+1}-{offset+len(selected)}"
        }
    except FileNotFoundError:
        return {"ok": False,"error": f"File not found: {filepath}"}
    except Exception as e:
        return {"ok":False, "error": str(e)}
    
def write(filepath,content):
    try:
        directory=os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath,'w',encoding='utf-8') as f:
            f.write(content)
        return { "ok": True, "filepath": filepath }
    except Exception as e:
        return {"ok":False, "error": str(e)}
    
def edit(filepath,old_string,new_string):
    try:
        with open(filepath,'r',encoding='utf-8') as f:
            content=f.read()
        if old_string not in content:
            return {"ok": False, "error": "String not found in file"}
        new_content=content.replace(old_string,new_string)
        with open(filepath,'w',encoding='utf-8') as f:
            f.write(new_content)
        return {"ok":True, "filepath": filepath}
    except Exception as e:
        return {"ok":False, "error": str(e)}
    
def bash(command,timeout=30):
    try:
        result=subprocess.run(
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
    
class Session:
    def __init__(self,session_dir="sessions"):
        self.session_dir=session_dir
        self.messages_file=f"{session_dir}/messages.json"
        self.context_file=f"{session_dir}/context.md"
        self.todos_file=f"{session_dir}/todos.md"
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
        if not os.path.exists(self.messages_file):
            write(self.messages_file,"[]")
        if not os.path.exists(self.context_file):
            write(self.context_file,"# Context\n\n")
        if not os.path.exists(self.todos_file):
            write(self.todos_file,"# TODOS\n\n- [ ] \n")

    def load_messages(self):
        try:
            with open(self.messages_file,'r',encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    def save_messages(self,messages):
        with open(self.messages_file,'w',encoding='utf-8') as f:
            json.dump(messages,f,ensure_ascii=False,indent=2)
    def add_message(self,role,content):
        messages=self.load_messages()
        messages.append({"role": role,"content": content})
        self.save_messages(messages)
        return len(messages)
    def load_context(self):
        try:
            with open(self.context_file,'r',encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    def update_context(self,content):
        write(self.context_file,content)
    def load_todos(self):
        try:
            with open(self.todos_file,'r',encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    def update_todos(self,content):
        write(self.todos_file,content)
    def new_session(self):
        """Start a new session (clears messages only)."""
        self.save_messages([])
        print("New session started. Messages cleared,context and todos preserved.")

def execute_tool(tool_name,args):
    if tool_name=="read":
        return read(**args)
    elif tool_name=="write":
        return write(**args)
    elif tool_name=="edit":
        return edit(**args)
    elif tool_name=="bash":
        return bash(**args)
    else:
        return({"ok":False,"error": f"Unknown tool: {tool_name}"})
def call_llm(messages,model="llama3.2:3b"):
    try:
        response=requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model,
                  "messages": messages,
                  "stream": False},
            timeout=60
        )
        if response.status_code==200:
            return response.json()['message']['content']
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"
    
SYSTEM_PROMPT = """You are a helpful coding assistant with access to 4 tools:

1. read(filepath, limit, offset) - Read a file
2. write(filepath, content) - Write to a file  
3. edit(filepath, old_string, new_string) - Edit a file
4. bash(command) - Run a shell command

Guidelines:
- Use read before editing files
- Use edit for precise changes
- Use write for new files or complete rewrites
- Use bash for file operations (ls, grep, find)
- Be concise in responses
- Show file paths clearly

State is stored in files:
- TODOs in todos.md
- Context in context.md
- Conversation in messages.json"""

class PiAgent:
    def __init__(self,session_dir="sessions",model="llama3.2:3b"):
        self.session=Session(session_dir)
        self.model=model
        self.messages=[{"role": "system", "content":SYSTEM_PROMPT}]
        context=self.session.load_context()
        if context:
            self.messages.append({
                "role": "system",
                "content": f"Current context:\n{context}"
            })
    def chat(self,user_input):
        self.messages.append({"role": "user","content": user_input})
        self.session.add_message("user",user_input)
        response=call_llm(self.messages,self.model)
        if "<tool>" in response and "</tool>" in response:
            start=response.find("<tool>")+6
            end=response.find("</tool>")
            tool_json=response[start:end].strip()
        try:
            tool_call=json.loads(tool_json)
            tool_name=tool_call.get('tool')
            args=tool_call.get('args',{})
            result=execute_tool(tool_name,args)
            self.messages.append({"role": "assistant","content": f"{response}"})
            self.messages.append({
                "role": "user",
                "content": f"<tool_result>{result}</tool_result>"
            })
            response=call_llm(self.messages,self.model)
        except Exception as e:
            print(f"Tool error: {e}")
        self.messages.append({"role": "assistant","content": response})
        self.session.add_message("assistant",response)
        return response
    
if __name__=="__main__":
    print("=" * 50)
    print("Pi-Style Agent - Session/Memory + Pi Philosophy")
    print("=" * 50)
    print("Commands:")
    print("  - Type normally to chat")
    print("  - 'new' - start new session")
    print("  - 'todos' - show TODOs")
    print("  - 'quit' - exit\n")
    
    agent=PiAgent()
    while True:
        User_input=input("You: ")
        if User_input.lower() in ["quit","exit"]:
            print("Goodbye!")
            break

        if User_input.lower()=="new":
            agent.session.new_session()
            continue
        if User_input.lower()=="todos":
            print(agent.session.load_todos())
            continue
        result=agent.chat(User_input)
        print(f"\nAgent: {result}\n")
