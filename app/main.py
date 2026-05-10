"""
Main Application - AI Agent System Orchestrator
Coordinates all agents and manages the application flow
"""

import os
from typing import Dict, Any, Optional
from app import database
from app.agents.project_manager import ProjectManagerAgent
from app.agents.team_manager import TeamManagerAgent
from app.agents.progress_tracker import ProgressTrackerAgent

class AIAgentTeam:
    """Orchestrates all AI agents for project management"""
    
    def __init__(self):
        # Initialize database
        database.init_db()
        
        # Initialize agents
        self.project_manager = ProjectManagerAgent()
        self.team_manager = TeamManagerAgent()
        self.progress_tracker = ProgressTrackerAgent()
        
        self.current_project_id = None
        self.context = {}
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and route to appropriate agent"""
        
        user_lower = user_input.lower()

        if "undo" in user_lower and "redo" not in user_lower:
            result = database.undo_last_action()
            return {
                "agent": "System",
                "response": result["message"],
                "result": result
            }
        elif "redo" in user_lower:
            result = database.redo_last_action()
            return {
                "agent": "System",
                "response": result["message"],
                "result": result
            }
        elif "history" in user_lower:
            history = database.get_action_history(limit=20)
            response = "Recent actions:\n"
            if not history:
                response += "No action history available."
            else:
                for item in history:
                    status = "(undone)" if item["is_undone"] else "(done)"
                    response += f"\n- {item['action_name']} {status}"
            return {
                "agent": "System",
                "response": response,
                "result": {"history": history}
            }
        
        # Route to appropriate agent based on keywords
        if any(word in user_lower for word in ["project", "timeline", "create project", "status"]):
            result = self.project_manager.process(user_input, self.context)
        elif any(word in user_lower for word in ["team", "member", "add", "workload", "capacity"]):
            result = self.team_manager.process(user_input, self.context)
        elif any(word in user_lower for word in ["task", "progress", "complete", "metric", "burndown"]):
            result = self.progress_tracker.process(user_input, self.context)
        else:
            # Default to project manager for general queries
            result = self.project_manager.process(user_input, self.context)
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        projects = database.get_all_projects()
        members = database.get_all_team_members()
        
        total_completion = 0
        if projects:
            total_completion = sum(p["completion"] for p in projects) / len(projects)
        
        return {
            "total_projects": len(projects),
            "total_team_members": len(members),
            "average_completion": int(total_completion),
            "projects": projects,
            "team_members": members
        }

# Global agent team instance
agent_team = None

def initialize_system():
    """Initialize the AI agent system"""
    global agent_team
    agent_team = AIAgentTeam()
    return agent_team

def get_agent_team() -> AIAgentTeam:
    """Get the initialized agent team"""
    global agent_team
    if agent_team is None:
        agent_team = initialize_system()
    return agent_team

def process_user_message(message: str) -> Dict[str, Any]:
    """Process a user message through the agent system"""
    team = get_agent_team()
    return team.process_input(message)

def get_system_overview() -> Dict[str, Any]:
    """Get system overview for dashboard"""
    team = get_agent_team()
    return team.get_system_status()

if __name__ == "__main__":
    # For testing
    system = initialize_system()
    
    print("🤖 AI Project Management System initialized!")
    print("Type your commands (or 'quit' to exit):\n")
    
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        result = system.process_input(user_input)
        print(f"\n{result['agent']}: {result['response']}")
