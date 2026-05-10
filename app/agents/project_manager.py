"""
Project Manager Agent
Handles project creation, coordination, and orchestration
"""

import re
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app import database

class ProjectManagerAgent(BaseAgent):
    """Manages project lifecycle and coordinates other agents"""
    
    def __init__(self):
        super().__init__("Project Manager", "Oversees projects and coordinates tasks")
        self.intents = {
            "create_project": self._handle_create_project,
            "list_projects": self._handle_list_projects,
            "project_status": self._handle_project_status,
            "update_project": self._handle_update_project,
            "help": self._handle_help
        }
    
    def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input and route to appropriate handler"""
        intent = self._detect_intent(user_input)
        handler = self.intents.get(intent, self._handle_default)
        
        return handler(user_input, context)
    
    def _detect_intent(self, user_input: str) -> str:
        """Detect user intent from input"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["create", "new project", "start project"]):
            return "create_project"
        elif any(word in user_lower for word in ["update", "edit", "change", "modify"]) and "project" in user_lower:
            return "update_project"
        elif any(word in user_lower for word in ["list", "show projects", "all projects"]):
            return "list_projects"
        elif any(word in user_lower for word in ["status", "progress", "how's the project"]):
            return "project_status"
        elif any(word in user_lower for word in ["help", "what can"]):
            return "help"
        else:
            return "default"
    
    def _handle_create_project(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle project creation"""
        
        # Extract project details using regex
        name_match = re.search(r"['\"]([^'\"]+)['\"]", user_input, re.IGNORECASE)
        if not name_match:
            name_match = re.search(r"(?:called|named)\s+([A-Za-z0-9_\- ]+?)(?:\s+with|\s+for|$)", user_input, re.IGNORECASE)
        if not name_match:
            name_match = re.search(r"project\s+([A-Za-z0-9_\- ]+?)(?:\s+with|\s+for|$)", user_input, re.IGNORECASE)

        timeline_match = re.search(r"(\d+)\s+(?:week|day|month)s?", user_input, re.IGNORECASE)
        
        if not name_match:
            return self._format_response(
                "I need a project name. Try: 'Create project called MyProject with 2 weeks timeline'"
            )
        
        project_name = name_match.group(1).strip()
        
        # Extract timeline (default: 2 weeks = 14 days)
        if timeline_match:
            timeline_value = int(timeline_match.group(1))
            timeline_unit = re.search(r"\d+\s+(\w+)", timeline_match.group(0), re.IGNORECASE).group(1).lower()
            
            if "week" in timeline_unit:
                timeline_days = timeline_value * 7
            elif "month" in timeline_unit:
                timeline_days = timeline_value * 30
            else:
                timeline_days = timeline_value
        else:
            timeline_days = 14
        
        # Create project
        result = database.create_project(
            name=project_name,
            description=user_input,
            timeline_days=timeline_days
        )
        
        if result["success"]:
            response = (f"✓ Project '{project_name}' created successfully!\n"
                       f"  Timeline: {timeline_days} days\n"
                       f"  Status: Ready for tasks\n\n"
                       f"Next: Add team members or tasks to this project.")
        else:
            response = f"❌ {result['message']}"
        
        return self._format_response(response, result)
    
    def _handle_list_projects(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle listing projects"""
        projects = database.get_all_projects()
        
        if not projects:
            response = "No projects yet. Create one with: 'Create project called MyProject with 2 weeks'"
        else:
            response = "📋 **All Projects:**\n"
            for proj in projects:
                status_icon = "✓" if proj["completion"] == 100 else "⏳"
                response += f"\n{status_icon} {proj['name']}"
                response += f"\n   Timeline: {proj['timeline_days']} days | Completion: {proj['completion']}%"
        
        return self._format_response(response, {"projects": projects})
    
    def _handle_update_project(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle project updates"""
        # Extract project name
        name_match = re.search(r"['\"]([^'\"]+)['\"]", user_input, re.IGNORECASE)
        if not name_match:
            name_match = re.search(r"project\s+([A-Za-z0-9_\- ]+?)(?:\s+(?:name|description|status|timeline)|\s*$)", user_input, re.IGNORECASE)
        
        if not name_match:
            return self._format_response(
                "Please specify a project name. Try: \"update project 'MyProject' description 'new description'\""
            )
        
        project_name = name_match.group(1).strip()
        
        # Find project by name
        projects = database.get_all_projects()
        project = next((p for p in projects if p["name"].lower() == project_name.lower()), None)
        
        if not project:
            return self._format_response(f"❌ Project '{project_name}' not found.")
        
        # Extract update fields
        updates = {}
        
        # Check for description update
        desc_match = re.search(r"description\s+['\"]?([^'\"]*?)['\"]?(?:\s+(?:status|timeline)|\s*$)", user_input, re.IGNORECASE)
        if desc_match:
            updates["description"] = desc_match.group(1).strip()
        
        # Check for status update
        status_match = re.search(r"status\s+(\w+)", user_input, re.IGNORECASE)
        if status_match:
            status_value = status_match.group(1).lower()
            if status_value in ["completed", "complete", "done"]:
                updates["status"] = "Completed"
            elif status_value in ["in progress", "active", "ongoing"]:
                updates["status"] = "In Progress"
            else:
                updates["status"] = status_value.capitalize()
        
        # Check for timeline update
        timeline_match = re.search(r"timeline\s+(\d+)\s+(\w+)", user_input, re.IGNORECASE)
        if timeline_match:
            timeline_value = int(timeline_match.group(1))
            timeline_unit = timeline_match.group(2).lower()
            
            if "week" in timeline_unit:
                updates["timeline_days"] = timeline_value * 7
            elif "month" in timeline_unit:
                updates["timeline_days"] = timeline_value * 30
            else:
                updates["timeline_days"] = timeline_value
        
        if not updates:
            return self._format_response(
                f"No updates specified for project '{project_name}'. Try: \"update project description 'new description'\""
            )
        
        # Apply updates
        result = database.update_project(project["id"], **updates)
        
        if result["success"]:
            response = f"✓ Project '{project_name}' updated successfully!\n"
            for key, value in updates.items():
                response += f"  • {key}: {value}\n"
        else:
            response = f"❌ {result['message']}"
        
        return self._format_response(response, result)
    
    def _handle_project_status(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle project status query"""
        projects = database.get_all_projects()
        
        if not projects:
            return self._format_response("No projects found.")
        
        # If only one project, show that one
        if len(projects) == 1:
            status = database.get_project_status(projects[0]["id"])
            response = self._format_status_response(status)
            return self._format_response(response, status)
        
        # Multiple projects - show summary
        response = "📊 **Project Status Summary:**\n"
        for proj in projects:
            status_icon = "✓" if proj["completion"] == 100 else "⏳"
            response += f"\n{status_icon} {proj['name']}: {proj['completion']}% complete"
        
        return self._format_response(response, {"projects": projects})
    
    def _format_status_response(self, status: Dict[str, Any]) -> str:
        """Format project status for display"""
        response = f"📊 **Project: {status['name']}**\n"
        response += f"Timeline: {status['timeline_days']} days\n"
        response += f"Overall Completion: {status['overall_completion']}%\n"
        response += f"Tasks: {status['completed_tasks']}/{status['total_tasks']} completed\n"
        response += f"Hours: {status['actual_hours']:.1f}/{status['estimated_hours']:.1f} spent\n"
        
        if status['team_members']:
            response += f"\nTeam Members: {len(status['team_members'])}\n"
            for member in status['team_members'][:3]:
                response += f"  • {member[0]} ({member[1]})\n"
        
        return response
    
    def _handle_help(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Show help"""
        help_text = """🤖 **Project Manager Agent Help**

I can help you manage projects! Try these commands:

**Projects:**
- "Create project called [name] with [2] weeks timeline"
- "Show all projects"
- "What's our project status?"

**Team:**
- "Add [Name] as [Role], capacity [40] hours"
- "List team members"

**Tasks:**
- "Add task '[task name]' for [person], [hours] hours, [priority]"
- "Update task progress: '[task]' is [50]% done, spent [4] hours"

**Reports:**
- "Show team workload"
- "Show project status"

Need help with something specific?
"""
        return self._format_response(help_text)
    
    def _handle_default(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle unrecognized input"""
        response = f"I'm not sure how to help with: '{user_input}'\n\nType 'help' for available commands."
        return self._format_response(response)
