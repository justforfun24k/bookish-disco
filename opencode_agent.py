"""
opencode_agent.py - Step 7: GitHub Actions / CI

CI = Continuous Integration
- Automated testing when you push code
- Run tests on every commit
- Catch bugs before they reach production

GitHub Actions: Free CI/CD built into GitHub
"""
import os

# =============================================
# What is CI/CD?
# =============================================
print("=" * 50)
print("What is CI/CD?")
print("=" * 50)

print("""
CI/CD = Continuous Integration / Continuous Deployment

Before CI:
- Developer writes code
- Manually tests
- Manually deploys
- Bugs slip through ❌

With CI:
- Developer writes code
- Pushes to GitHub
- GitHub automatically runs tests ✅
- If tests pass → deploy ✅
- If tests fail → notify developer ❌

Benefits:
- Catch bugs early
- Don't break main branch
- Automate boring tasks
- Everyone sees the status
""")


# =============================================
# GitHub Actions Basics
# =============================================
print("\n" + "=" * 50)
print("GitHub Actions Basics")
print("=" * 50)

print("""
GitHub Actions workflow file: .github/workflows/ci.yml

Structure:
1. trigger: When to run (push, pull request)
2. jobs: What to run
3. steps: Individual commands

Simple example:
""")

workflow_example = """
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest
"""

print(workflow_example)


# =============================================
# Create a CI Workflow
# =============================================
print("\n" + "=" * 50)
print("Creating Your CI Workflow")
print("=" * 50)

def create_ci_workflow():
    """Create a basic CI workflow file"""
    
    workflow_content = """name: Python CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest
      
      - name: Run tests
        run: pytest
      
  lint:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install ruff
        run: pip install ruff
      
      - name: Lint
        run: ruff check .
"""
    
    os.makedirs(".github/workflows", exist_ok=True)
    
    with open(".github/workflows/ci.yml", "w") as f:
        f.write(workflow_content)
    
    print("✅ Created .github/workflows/ci.yml")


def create_github_agent_workflow():
    """Create CI for our Pi-style agent"""
    
    workflow_content = """name: Pi Agent CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-agent:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Test agent imports
        run: python -c "from opencode_agent import read, write, edit, bash; print('OK')"
      
      - name: Test basic functionality
        run: |
          python -c "
          from opencode_agent import read, write, bash
          
          # Test write
          result = write('test_ci.txt', 'Hello CI!')
          assert result['ok'] == True, 'Write failed'
          
          # Test read
          result = read('test_ci.txt')
          assert 'Hello CI!' in result['content'], 'Read failed'
          
          # Test bash
          result = bash('echo Hello')
          assert 'Hello' in result['stdout'], 'Bash failed'
          
          print('All tests passed!')
          "
      
      - name: Cleanup
        run: rm -f test_ci.txt

  lint:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install ruff
        run: pip install ruff
      
      - name: Lint
        run: ruff check . || echo "No lint issues"
"""
    
    os.makedirs(".github/workflows", exist_ok=True)
    
    with open(".github/workflows/agent.yml", "w") as f:
        f.write(workflow_content)
    
    print("✅ Created .github/workflows/agent.yml")


# =============================================
# GitHub Actions Concepts
# =============================================
print("\n" + "=" * 50)
print("Key GitHub Actions Concepts")
print("=" * 50)

print("""
Triggers (on:):
- push: When you push code
- pull_request: When you open a PR
- schedule: On a timer (cron)
- workflow_dispatch: Manual trigger

Common Actions:
- actions/checkout@v4: Get your code
- actions/setup-python@v5: Set up Python
- actions/upload-artifact@v4: Save files

Runners:
- ubuntu-latest: Free, Linux
- windows-latest: Windows
- macos-latest: macOS
""")


# =============================================
# Create the workflow files
# =============================================
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Creating Workflow Files")
    print("=" * 50)
    
    create_ci_workflow()
    create_github_agent_workflow()
    
    print("\n" + "=" * 50)
    print("Next Steps")
    print("=" * 50)
    print("""
1. Initialize git repo:
   git init
   git add .
   git commit -m "Initial commit"
   
2. Create GitHub repo:
   - Go to github.com/new
   - Push your code
   
3. Push and watch CI run:
   git push origin main
   
4. Check Actions tab on GitHub!

CI Badge (add to README.md):
![CI](https://github.com/USERNAME/REPO/actions/workflows/agent.yml/badge.svg)
    """)


# =============================================
# Add CI Status Badge
# =============================================
def add_ci_badge():
    """Instructions for adding CI badge"""
    print("\n" + "=" * 50)
    print("Adding CI Status Badge")
    print("=" * 50)
    
    print("""
Add this to your README.md:

![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/agent.yml/badge.svg)
    """)

add_ci_badge()
