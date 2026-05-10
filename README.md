# AI Project Management System - 8 Hour MVP Demo

> A university project for Prompt Engineering class demonstrating AI agents managing projects through natural language.

## 🎯 Project Overview

This is a **working MVP** (Minimum Viable Product) of an AI-powered project management system built in **8 hours** using only **free software**.

**Key Features:**
- ✅ Create projects using natural language
- ✅ Add team members and track workload
- ✅ Create tasks and update progress
- ✅ Real-time metrics and burndown charts
- ✅ Multi-agent AI system coordinating tasks
- ✅ Web-based UI (Streamlit)
- ✅ Local SQLite database (no external dependencies)

---

## 🤖 AI Agent System

Three specialized agents work together:

### 1. **Project Manager Agent**
- Interprets high-level project descriptions
- Creates project structures from natural language
- Coordinates between other agents
- Handles project queries and status reports

### 2. **Team Manager Agent**
- Manages team members and their capacity
- Tracks workload and utilization
- Suggests resource allocation
- Reports on team availability

### 3. **Progress Tracker Agent**
- Creates tasks from descriptions
- Updates progress and completion
- Calculates metrics (burndown, velocity)
- Monitors project health

---

## 🚀 Quick Start (20 minutes)

### 1. Install Python & Dependencies

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Setup LLM (Choose One)

**Option A: Ollama (Local, Free)**
```bash
# Download from https://ollama.ai
ollama pull mistral
ollama serve  # Run in separate terminal
```

**Option B: HuggingFace (Cloud, Free)**
```bash
# Get free token from https://huggingface.co/settings/tokens
# Add to .env file: HF_TOKEN=your_token
```

### 3. Launch Demo

```bash
streamlit run app/ui/streamlit_app.py
```

Opens at http://localhost:8501

---

## 💬 Demo Commands

```
Add Alice as Frontend Developer, capacity 40 hours
Add Bob as Backend Engineer, capacity 40 hours
Create project called "AI Dashboard" with 2 weeks timeline
Add task "Design UI" for Alice, 3 days, high priority
Add task "Build API" for Bob, 4 days, high priority
Show project status
Update "Design UI" to 50% complete, spent 5 hours
Show team workload
What's our project status?
```

---

## 📁 Project Structure

```
PromptEngineering_HF/
├── app/
│   ├── main.py                    # Agent orchestrator
│   ├── database.py                # SQLite functions
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── project_manager.py
│   │   ├── team_manager.py
│   │   └── progress_tracker.py
│   └── ui/
│       └── streamlit_app.py       # Web interface
├── data/
│   └── projects.db               # Auto-created database
├── Project_plan.md               # Full development plan
├── DEMO_QUICKSTART.md            # Demo guide
├── SETUP_AND_LAUNCH.md           # Setup instructions
├── requirements.txt
└── .env
```

---

## 🎓 Technology Stack (All Free)

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Streamlit | 0 setup, write Python |
| **Backend** | Python + Flask | Lightweight, fast |
| **Database** | SQLite | File-based, zero setup |
| **LLM** | Ollama/HF | Free, local or cloud |
| **Agents** | LangChain | Free framework |
| **Charts** | Plotly | Interactive visualizations |

---

## ✅ What's Working in This MVP

- ✅ 3 core agents operational
- ✅ Natural language command parsing
- ✅ Team and project management
- ✅ Progress tracking
- ✅ Real-time metrics
- ✅ Web-based UI
- ✅ Data persistence
- ✅ Error handling

---

## 📚 Documentation

- **`Project_plan.md`** - Full 12-week development roadmap
- **`DEMO_QUICKSTART.md`** - Quick start guide
- **`SETUP_AND_LAUNCH.md`** - Detailed setup instructions
- **`README.md`** - This file

---

## 🚀 Next Steps

To extend this MVP and build the full system:
- Add 5 more specialized agents (Phase 2-3)
- Add voice interface (Phase 4)
- Add scheduling and Gantt charts (Phase 2)
- Add advanced KPI tracking (Phase 3)
- Add what-if scenario planning (Phase 5)

See `Project_plan.md` for detailed 12-week roadmap.
