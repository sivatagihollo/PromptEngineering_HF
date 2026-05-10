# 🚀 8-Hour Demo Setup & Launch Guide

## ⏰ Your Timeline (8 hours from now)

**Total setup time: ~1 hour | Demo ready in: ~2 hours**

---

## 📋 Prerequisites

- Windows 10/11
- Python 3.9+ installed ([Download](https://www.python.org/downloads/))
- Internet connection (for initial setup only)

---

## 🔧 Step-by-Step Setup (20-30 minutes)

### Step 1: Open Terminal

```bash
# Navigate to your project folder
cd e:\Tanulás\MSc\3.\ félév\Prompt\ engineering\PromptEngineering_HF
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt --upgrade
```

**This installs:**
- `streamlit` - Web UI (2 min)
- `langchain` - AI agent framework (1 min)  
- `plotly` - Charts (1 min)
- Other utilities (1 min)

**Total time: ~5 minutes**

---

## 🎯 Choose Your LLM Setup

Pick ONE option:

### **Option A: Ollama (BEST - Completely Local)**

1. Download from https://ollama.ai (**~2 min download**)
2. Install and run Ollama
3. In terminal, run:
```bash
ollama pull mistral
```
**Time: ~10 minutes (depends on internet)**

4. Leave this terminal window running
5. In another terminal (with venv activated), run the app

### **Option B: HuggingFace Free API (Alternative)**

1. Sign up free: https://huggingface.co (**~2 min**)
2. Get API token from: https://huggingface.co/settings/tokens
3. Copy the token and save it to `.env`:
```
HF_TOKEN=hf_your_token_here
LLM_PROVIDER=huggingface
```
4. No download needed!

### **Option C: Skip LLM for Ultra-Fast Demo**

If you're short on time, modify `app/database.py`:
- Change agents to use simple rule-based logic instead of LLM
- Still works, just less "intelligent"
- Setup time: **0 minutes**

---

## 🚀 Launch the Demo

### Start the Web Interface (Recommended)

```bash
# Make sure venv is activated!
streamlit run app/ui/streamlit_app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

Browser opens automatically. If not, go to: **http://localhost:8501**

### Alternative: CLI Interface

```bash
python -m app.main
```

Runs in terminal with text prompts.

---

## 💡 Demo Script (5-10 minutes)

Copy-paste these commands in order:

```
1. Add Alice as Frontend Developer, capacity 40 hours

2. Add Bob as Backend Engineer, capacity 40 hours

3. Create project called "AI Dashboard" with 2 weeks timeline

4. Add task "Design UI mockups" for Alice, 3 days, high priority

5. Add task "Build API endpoints" for Bob, 4 days, high priority

6. Show project status

7. Update "Design UI mockups" to 50% complete, spent 5 hours

8. Show team workload

9. What's the overall project status?

10. Show metrics
```

---

## 📊 Expected Demo Results

After running through the demo script, you should see:

✅ **Team Management**
- Alice and Bob added as team members
- Workload visualization showing their capacity

✅ **Project Management**  
- AI Dashboard project created
- Tasks auto-assigned to team
- Progress tracking from 0% to 50%

✅ **Real-time Metrics**
- Project completion percentage
- Team utilization charts
- Task burndown visualization

✅ **Natural Language Processing**
- AI understands all commands
- Extracts dates, numbers, names automatically
- Generates intelligent responses

---

## 🎯 If You're Running Short on Time

**Minimum 30-minute setup:**
1. Create venv (2 min)
2. Install packages (5 min)
3. Use HuggingFace API or skip LLM (2 min)
4. Run `streamlit run app/ui/streamlit_app.py` (1 min)
5. Demo runs (20 min)

---

## ⚠️ Troubleshooting

### "venv\Scripts\activate not found"
```bash
# Create venv again
python -m venv venv

# Then activate
venv\Scripts\activate
```

### "ModuleNotFoundError" when running
```bash
# Make sure venv is active (should see (venv) in prompt)
# Then reinstall:
pip install -r requirements.txt --upgrade
```

### Streamlit won't start
```bash
# Reinstall streamlit
pip uninstall streamlit
pip install streamlit --upgrade

# Try again
streamlit run app/ui/streamlit_app.py
```

### Ollama connection error
- Make sure Ollama is running: `ollama serve` in another terminal
- Check: http://localhost:11434/api/tags (should work)

### Slow responses
- Using CPU instead of GPU? Models run slower
- Try smaller model: `ollama pull neural-chat`
- Or use HuggingFace API

---

## 📝 File Structure

```
PromptEngineering_HF/
├── app/
│   ├── main.py                 ← Core agent orchestrator
│   ├── database.py             ← SQLite database functions
│   ├── agents/
│   │   ├── base_agent.py       ← Base class
│   │   ├── project_manager.py  ← Project management
│   │   ├── team_manager.py     ← Team management
│   │   └── progress_tracker.py ← Task & progress tracking
│   └── ui/
│       └── streamlit_app.py    ← Web interface
├── data/
│   └── projects.db            ← Auto-created SQLite database
├── requirements.txt           ← Python packages
├── .env                       ← Configuration
└── README.md
```

---

## ✅ Pre-Demo Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Packages installed (`pip install -r requirements.txt`)
- [ ] LLM ready (Ollama OR HF token set)
- [ ] Can start app without errors
- [ ] Browser opens to http://localhost:8501
- [ ] Can create a team member
- [ ] Can create a project
- [ ] Can see chat responses

---

## 🎬 Presenting the Demo

1. **Open Streamlit UI** in browser
2. **Go to "Chat Interface"** tab
3. **Paste the demo script commands** one by one
4. **Show the results** - Projects, Team, Tasks, Reports tabs
5. **Explain**: "All of this works with natural language - no clicking required!"

**Total demo time: 5-10 minutes**

---

## 🎓 What to Tell Your Professor

*"This is an 8-hour MVP of an AI-powered project management system. It demonstrates:*

1. **Multi-Agent AI Architecture** - 3 specialized agents coordinating
2. **Natural Language Processing** - Commands in plain English
3. **Project Management** - Create projects, track progress, manage teams  
4. **Real-time Metrics** - Automatic calculations and burndown charts
5. **Local-First Design** - Works completely offline, all free software

*The full system (planned in Project_plan.md) would have 8 agents, voice interface, advanced scheduling, and KPI tracking, but this MVP focuses on core functionality: team management and progress tracking.*"

---

## 🚀 Next Steps (After 8-hour demo)

1. Add voice interface (Weeks 3-4)
2. Add scheduling agent (Weeks 3-4)
3. Add KPI tracking (Weeks 5-6)
4. Add what-if scenarios (Weeks 9-10)
5. Production deployment

---

**Good luck with your demo! 🎉**

*If you get stuck, the code has lots of comments explaining each agent.*
