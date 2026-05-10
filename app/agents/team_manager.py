"""
Team Manager Agent
Manages team members and resource allocation
"""

import re
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app import database

class TeamManagerAgent(BaseAgent):
    """Manages team members and their assignments"""
    
    def __init__(self):
        super().__init__("Team Manager", "Manages team members and resource allocation")
        self.intents = {
            "add_member": self._handle_add_member,
            "update_member": self._handle_update_member,
            "list_members": self._handle_list_members,
            "team_workload": self._handle_team_workload,
        }
    
    def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input and route to appropriate handler"""
        intent = self._detect_intent(user_input)
        handler = self.intents.get(intent, self._handle_default)
        
        return handler(user_input, context)
    
    def _detect_intent(self, user_input: str) -> str:
        """Detect user intent"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["update", "edit", "change", "modify"]) and ("member" in user_lower or "team" in user_lower or any(keyword in user_lower for keyword in ["capacity", "role", "available", "busy"])):
            # More specific: if updating/editing with team-related keywords, it's update_member
            if not any(word in user_lower for word in ["workload", "utilization"]):
                return "update_member"
        
        if any(word in user_lower for word in ["add", "new member", "new person", "hire", "join"]):
            return "add_member"
        elif any(word in user_lower for word in ["list", "show team", "all members", "who's on"]):
            return "list_members"
        elif any(word in user_lower for word in ["workload", "capacity", "utilization", "who's busy"]):
            return "team_workload"
        else:
            return "default"
    
    def _handle_add_member(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle adding team member"""
        
        # Extract name (look for patterns like "Add John" or "John Smith as")
        name_match = re.search(r"add\s+([A-Za-z\s]+?)\s+as\s+", user_input, re.IGNORECASE)
        if not name_match:
            name_match = re.search(r"(?:add|new)\s+(?:member\s+)?([A-Za-z\s]+?)(?:\s+as|\s+,|$)", user_input, re.IGNORECASE)
        
        if not name_match:
            return self._format_response(
                "I need a name. Try: 'Add John Smith as Backend Developer, capacity 40 hours'"
            )
        
        name = name_match.group(1).strip()
        
        # Extract role (look for pattern "as [Role]")
        role_match = re.search(r"as\s+([A-Za-z\s]+?)(?:,|\s+capacity|$)", user_input, re.IGNORECASE)
        role = role_match.group(1).strip() if role_match else "Developer"
        
        # Extract capacity (default: 40 hours)
        capacity_match = re.search(r"capacity\s+(\d+)", user_input, re.IGNORECASE)
        capacity = int(capacity_match.group(1)) if capacity_match else 40
        
        # Add team member
        result = database.add_team_member(
            name=name,
            role=role,
            capacity_hours=capacity
        )
        
        if result["success"]:
            response = (f"✓ Team member added!\n"
                       f"  Name: {name}\n"
                       f"  Role: {role}\n"
                       f"  Capacity: {capacity} hours/week")
        else:
            response = f"❌ {result['message']}"
        
        return self._format_response(response, result)
    
    def _handle_update_member(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle updating team member"""
        
        # Extract member name
        name_match = re.search(r"(?:update|edit|change)\s+(?:member\s+)?([A-Za-z\s]+?)(?:\s+(?:role|capacity|available|busy)|\s+to|\s*$)", user_input, re.IGNORECASE)
        if not name_match:
            name_match = re.search(r"['\"]([^'\"]+)['\"]", user_input, re.IGNORECASE)
        
        if not name_match:
            return self._format_response(
                "Please specify a member name. Try: \"update John capacity 50 hours\""
            )
        
        member_name = name_match.group(1).strip()
        
        # Find member by name
        members = database.get_all_team_members()
        member = next((m for m in members if m["name"].lower() == member_name.lower()), None)
        
        if not member:
            return self._format_response(f"❌ Team member '{member_name}' not found.")
        
        # Extract update fields
        updates = {}
        
        # Check for role update
        role_match = re.search(r"role\s+['\"]?([^'\"]*?)['\"]?(?:\s+capacity|$)", user_input, re.IGNORECASE)
        if role_match:
            updates["role"] = role_match.group(1).strip()
        
        # Check for capacity update
        capacity_match = re.search(r"capacity\s+(\d+)", user_input, re.IGNORECASE)
        if capacity_match:
            updates["capacity_hours"] = float(capacity_match.group(1))
        
        # Check for availability update
        available_match = re.search(r"(?:available|busy)\s+(\w+)", user_input, re.IGNORECASE)
        if available_match:
            status = available_match.group(1).lower()
            if status in ["true", "yes", "available"]:
                updates["available"] = True
            elif status in ["false", "no", "busy"]:
                updates["available"] = False
        
        if not updates:
            return self._format_response(
                f"No updates specified. Try: \"update {member_name} capacity 50\""
            )
        
        # Apply updates
        result = database.update_team_member(member["id"], **updates)
        
        if result["success"]:
            response = f"✓ Team member '{member_name}' updated successfully!\n"
            for key, value in updates.items():
                response += f"  • {key}: {value}\n"
        else:
            response = f"❌ {result['message']}"
        
        return self._format_response(response, result)
    
    def _handle_list_members(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle listing team members"""
        members = database.get_all_team_members()
        
        if not members:
            response = "No team members yet. Add one with: 'Add John as Backend Developer'"
        else:
            response = "👥 **Team Members:**\n"
            for member in members:
                status = "✓ Available" if member["available"] else "⏸ Busy"
                response += f"\n• {member['name']} - {member['role']}"
                response += f"\n  Capacity: {member['capacity_hours']} hours/week | {status}"
        
        return self._format_response(response, {"members": members})
    
    def _handle_team_workload(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle team workload report"""
        
        # Check if specific project mentioned
        project_id = None
        if context and "project_id" in context:
            project_id = context["project_id"]
        
        if project_id:
            workload_data = database.get_team_workload(project_id)
            team_workload = workload_data.get("team_workload", [])
        else:
            # Show all team members
            members = database.get_all_team_members()
            team_workload = [
                {
                    "name": m["name"],
                    "role": m["role"],
                    "capacity": m["capacity_hours"],
                    "task_count": 0,
                    "remaining_hours": 0,
                    "utilization_percentage": 0
                }
                for m in members
            ]
        
        if not team_workload:
            return self._format_response("No team members assigned yet.")
        
        response = "📊 **Team Workload:**\n"
        for member in team_workload:
            utilization = member["utilization_percentage"]
            
            # Create utilization bar
            bar_length = 20
            filled = int(bar_length * utilization / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            if utilization < 50:
                status = "✓ Light"
            elif utilization < 80:
                status = "⚠ Moderate"
            else:
                status = "🔴 Heavy"
            
            response += f"\n{member['name']} ({member['role']})\n"
            response += f"  [{bar}] {utilization}% ({status})\n"
            response += f"  Tasks: {member['task_count']} | Remaining: {member['remaining_hours']:.1f}h / {member['capacity']}h\n"
        
        return self._format_response(response, {"workload": team_workload})
    
    def _handle_default(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle unrecognized input"""
        response = f"I didn't understand that. I can help with:\n"
        response += "• 'Add [Name] as [Role]'\n"
        response += "• 'Show team members'\n"
        response += "• 'Show team workload'"
        
        return self._format_response(response)
