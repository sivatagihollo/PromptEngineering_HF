# 8-Hour Demo: Quick Start Guide

## ⏰ Timeline

- **Hours 0-1**: Environment setup & dependencies
- **Hours 1-3**: Core agent system & database
- **Hours 3-5**: Agent implementations & integration
- **Hours 5-7**: UI (Streamlit) & demo scenarios
- **Hours 7-8**: Testing & refinement

---

## 🚀 Installation (20 minutes)

### Step 1: Install Python Dependencies

```bash
# Navigate to project folder
cd e:\Tanulás\MSc\3.\ félév\Prompt\ engineering\PromptEngineering_HF

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Step 2: Download LLM (Optional - Free Alternative)

**Option A: Use Ollama (Recommended - Most local control)**
1. Download from https://ollama.ai
2. Install and run: `ollama serve`
3. In another terminal: `ollama pull mistral` (or `ollama pull neural-chat`)

**Option B: Use Hugging Face Free Inference (No download needed)**
- Sign up free at https://huggingface.co
- Get API token from settings
- Set environment variable: `HF_TOKEN=your_token`

**Option C: Use LocalAI (GGUF models, completely free)**
- Alternative to Ollama

---

## 📁 Project Structure

```
PromptEngineering_HF/
├── DEMO_QUICKSTART.md          # This file
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── database.py             # SQLite setup
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Base agent class
│   │   ├── project_manager.py  # Project Manager Agent
│   │   ├── progress_tracker.py # Progress Tracker Agent
│   │   └── team_manager.py     # Team Manager Agent
│   ├── ui/
│   │   ├── streamlit_app.py    # Streamlit interface
│   │   └── cli_interface.py    # CLI alternative
│   └── models/
│       └── schemas.py          # Data models
├── data/
│   └── projects.db             # SQLite database
└── README.md
```

---

## 🏃 Running the Demo

### Option 1: Streamlit Web UI (Recommended - Fastest)

```bash
streamlit run app/ui/streamlit_app.py
```

Opens browser at `http://localhost:8501`

### Option 2: CLI Interface

```bash
python app/main.py
```

Runs in terminal with interactive prompts.

---

## 🤖 Demo Features (MVP)

### Team Management
- **Add team member**: "Add John Smith as Backend Developer, capacity 40 hours/week"
- **List team**: "Show all team members"
- **Update availability**: "Mark Alice as 50% available next week"

### Project & Progress Tracking
- **Create project**: "Create project 'Mobile App' with 4 weeks timeline, backend and frontend tasks"
- **Add task**: "Add task 'Design database schema' for John, 8 hours, priority high"
- **Update progress**: "Mark 'Design database schema' as 50% complete, actual time 4 hours"
- **Get status**: "What's our project status?", "Show me burndown", "Who's overloaded?"

### AI Agent Responses
- Agents interpret natural language
- Extract entities (names, dates, durations)
- Calculate metrics automatically
- Suggest resource adjustments
- Predict completion dates

---

## 💡 Example Demo Scenario (Run this!)

```
User: "Create a project called 'AI Dashboard' with 2 weeks timeline, 3 team members"

AI Manager: "I'll create the project. I'll need more details about the team and tasks. 
Should I create placeholder team members or add specific ones?"

User: "Add Alice as Frontend Lead, Bob as Backend Engineer, Carol as QA"

AI: "Team added. Now let's add tasks."

User: "Add 'Setup React project' for Alice, 2 days, high priority"
User: "Add 'Build API endpoints' for Bob, 3 days, high priority"
User: "Add 'Create test plan' for Carol, 1 day"

AI: "Tasks created. Your project is now 0% complete with 6 days of work."

User: "What's the current status?"

AI: "Project: AI Dashboard
Timeline: 2 weeks (14 days)
Tasks: 3 total | 0% complete
Team: Alice (2d), Bob (3d), Carol (1d)
Burndown: 6 days remaining
Status: On track ✓"

User: "Complete 'Setup React project' and 'Create test plan', update 'Build API' to 50%"

AI: "Progress updated! Project is now 50% complete. Estimated completion: 3 days (on schedule)."

User: "Show me the team workload"

AI: "Team Utilization:
- Alice: 2/5 tasks (40%) - Available ✓
- Bob: 1/5 tasks in progress (20%) - Available ✓
- Carol: Done! (100%) - Available ✓"
```

---

## 🔧 Tech Stack Explained (Why These Tools?)

| Component | Choice | Why |
|-----------|--------|-----|
| Database | SQLite | Zero setup, file-based, perfect for local demo |
| LLM | Ollama/Mistral | Free, local, no API costs, works offline |
| Backend | Flask/FastAPI | Lightweight, easy to understand, fast development |
| UI | Streamlit | Write UI in pure Python, live reload, 10x faster than React |
| Agent Framework | LangChain | Free community edition, great for prototyping |
| Visualization | Plotly | Interactive charts, works in Streamlit |

---

## 📊 What Gets Demonstrated

### Data Persistence
- ✓ Teams stored and retrieved
- ✓ Projects and tasks saved to SQLite
- ✓ Progress tracked over time

### AI Capabilities
- ✓ Natural language understanding
- ✓ Entity extraction (names, dates, numbers)
- ✓ Intelligent suggestions
- ✓ Automatic calculations

### Useful Outputs
- ✓ Project status summary
- ✓ Team utilization report
- ✓ Simple burndown visualization
- ✓ Completion predictions

---

## 🎯 Success Criteria for Demo

- ✓ System runs locally without internet
- ✓ Can create team members via natural language
- ✓ Can create projects and track progress
- ✓ Shows team workload and project status
- ✓ Agents understand and respond intelligently
- ✓ Data persists between sessions
- ✓ Takes < 5 seconds to respond to queries

---

## ⚠️ Known Limitations (8-hour MVP)

- No scheduling/Gantt charts (Phase 2)
- No KPI calculations (Phase 2)
- No voice interface (Phase 4)
- No external integrations (Phase 5)
- Limited to 3 core agents (full version has 8)
- Simple database schema (optimized for speed)

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'langchain'"
```bash
pip install langchain huggingface-hub
```

### "Ollama connection refused"
Make sure Ollama is running: `ollama serve` in another terminal

### "streamlit command not found"
```bash
pip install streamlit --upgrade
```

### Slow responses
- Check Ollama/LLM is running
- Consider using smaller model: `ollama pull neural-chat`
- Add response caching (see code comments)

---

## 📝 Files to Create

All Python files are provided in the implementation section below. Create them in the `app/` directory.

---

## ✅ Checklist Before Demo

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] LLM ready (Ollama running OR HF_TOKEN set)
- [ ] Database initialized (first run creates it)
- [ ] Streamlit runs without errors
- [ ] Can create team member
- [ ] Can create project
- [ ] Can update progress
- [ ] Can see status report

---

## 🎬 Demo Script

**Time: 0-8 hours from now**

1. **(Hour 0-1)** Setup environment ← You are here
2. **(Hour 1-3)** Create core files
3. **(Hour 3-5)** Implement agents
4. **(Hour 5-7)** Build UI & test
5. **(Hour 7-8)** Final polishing & dry run

Proceed to "IMPLEMENTATION FILES" section below!
