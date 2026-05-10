"""
Progress Tracker Agent
Handles task management and progress tracking
"""

import re
from typing import Dict, Any, Optional, List
from app.agents.base_agent import BaseAgent
from app import database

class ProgressTrackerAgent(BaseAgent):
    """Tracks project progress, tasks, and metrics"""
    
    def __init__(self):
        super().__init__("Progress Tracker", "Tracks tasks and project progress")
        self.intents = {
            "add_task": self._handle_add_task,
            "update_progress": self._handle_update_progress,
            "update_task": self._handle_update_task,
            "show_tasks": self._handle_show_tasks,
            "project_metrics": self._handle_project_metrics,
        }
    
    def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input"""
        intent = self._detect_intent(user_input)
        handler = self.intents.get(intent, self._handle_default)
        
        return handler(user_input, context)
    
    def _detect_intent(self, user_input: str) -> str:
        """Detect user intent"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["add task", "new task", "create task"]):
            return "add_task"
        elif any(word in user_lower for word in ["update task", "edit task", "modify task", "change task"]) and "progress" not in user_lower:
            return "update_task"
        elif any(word in user_lower for word in ["update", "progress", "complete", "done", "spent"]):
            return "update_progress"
        elif any(word in user_lower for word in ["show task", "list task", "all task"]):
            return "show_tasks"
        elif any(word in user_lower for word in ["metric", "burndown", "velocity", "rate"]):
            return "project_metrics"
        else:
            return "default"
    
    def _handle_add_task(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle adding a task"""
        
        # For demo, we'll create task for the first/only project
        projects = database.get_all_projects()
        if not projects:
            return self._format_response(
                "No projects exist. Create one first with: 'Create project called MyProject'"
            )
        
        project_id = projects[0]["id"]
        
        # Extract task name (inside quotes or after "task")
        name_match = re.search(r"['\"]([^'\"]+)['\"]|task\s+(?:called\s+)?([A-Za-z\s]+?)(?:\s+for|\s+,|$)", user_input, re.IGNORECASE)
        if not name_match:
            return self._format_response(
                "I need a task name. Try: \"Add task 'Design UI' for John, 5 hours, high priority\""
            )
        
        task_name = name_match.group(1) or name_match.group(2)
        task_name = task_name.strip()
        
        # Extract assignee
        assignee_match = re.search(r"for\s+([A-Za-z\s]+?)(?:,|\s+\d+)", user_input, re.IGNORECASE)
        assigned_to_id = None
        if assignee_match:
            assignee_name = assignee_match.group(1).strip()
            members = database.get_all_team_members()
            for member in members:
                if member["name"].lower() == assignee_name.lower():
                    assigned_to_id = member["id"]
                    break
        
        # Extract hours
        hours_match = re.search(r"(\d+)\s+hour", user_input, re.IGNORECASE)
        hours = int(hours_match.group(1)) if hours_match else 5
        
        # Extract priority
        priority = "Medium"
        if "high" in user_input.lower():
            priority = "High"
        elif "low" in user_input.lower():
            priority = "Low"
        
        # Add task
        result = database.add_task(
            project_id=project_id,
            name=task_name,
            description=user_input,
            assigned_to_id=assigned_to_id,
            estimated_hours=hours,
            priority=priority
        )
        
        if result["success"]:
            assignee_info = ""
            if assigned_to_id:
                members = database.get_all_team_members()
                for m in members:
                    if m["id"] == assigned_to_id:
                        assignee_info = f"\n  Assigned to: {m['name']}"
                        break
            
            response = (f"✓ Task added!\n"
                       f"  Name: {task_name}\n"
                       f"  Estimated: {hours} hours\n"
                       f"  Priority: {priority}{assignee_info}")
        else:
            response = f"❌ {result['message']}"
        
        return self._format_response(response, result)
    
    def _handle_update_progress(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle progress updates"""
        
        # Get all projects and their tasks
        projects = database.get_all_projects()
        if not projects:
            return self._format_response("No projects exist yet.")
        
        project_id = projects[0]["id"]
        status = database.get_project_status(project_id)
        tasks = status.get("tasks", [])
        
        if not tasks:
            return self._format_response("No tasks in this project yet.")
        
        # Find which task to update (matching by name)
        task_id_to_update = None
        for task in tasks:
            if task["name"].lower() in user_input.lower():
                task_id_to_update = task["id"]
                break
        
        if not task_id_to_update:
            task_names = ", ".join([t["name"] for t in tasks[:3]])
            return self._format_response(
                f"Which task? Available: {task_names}"
            )
        
        # Extract completion percentage
        completion_match = re.search(r"(\d+)%", user_input)
        completion = int(completion_match.group(1)) if completion_match else 50
        completion = min(100, max(0, completion))  # Clamp 0-100
        
        # Extract actual hours spent
        hours_match = re.search(r"spent\s+(\d+)\s+hour|(\d+)\s+hour.*spent", user_input, re.IGNORECASE)
        if not hours_match:
            hours_match = re.search(r"(\d+)\s+hour", user_input, re.IGNORECASE)
        
        actual_hours = int(hours_match.group(1) or hours_match.group(2) or 0) if hours_match else 0
        
        # Update progress
        result = database.update_task_progress(
            task_id=task_id_to_update,
            completion_percentage=completion,
            actual_hours=actual_hours
        )
        
        if result["success"]:
            # Calculate new project metrics
            new_status = database.get_project_status(project_id)
            response = (f"✓ Progress updated!\n"
                       f"  Completion: {completion}%\n"
                       f"  Time spent: {actual_hours} hours\n"
                       f"\n📊 Project now: {new_status['overall_completion']}% complete")
        else:
            response = f"❌ {result['message']}"
        
        return self._format_response(response, result)
    
    def _handle_update_task(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle task updates (name, description, priority, status, etc.)"""
        
        # Get all projects and their tasks
        projects = database.get_all_projects()
        if not projects:
            return self._format_response("No projects exist yet.")
        
        project_id = projects[0]["id"]
        status = database.get_project_status(project_id)
        tasks = status.get("tasks", [])
        
        if not tasks:
            return self._format_response("No tasks in this project yet.")
        
        # Find which task to update (matching by name)
        name_match = re.search(r"['\"]([^'\"]+)['\"]|task\s+(?:called\s+)?([A-Za-z\s]+?)(?:\s+(?:name|priority|status)|\s+to|\s*$)", user_input, re.IGNORECASE)
        if not name_match:
            return self._format_response("Please specify a task name. Try: \"update task 'TaskName' priority high\"")
        
        task_name = (name_match.group(1) or name_match.group(2)).strip()
        
        task_id_to_update = None
        for task in tasks:
            if task["name"].lower() == task_name.lower():
                task_id_to_update = task["id"]
                break
        
        if not task_id_to_update:
            return self._format_response(f"Task '{task_name}' not found.")
        
        # Extract update fields
        updates = {}
        
        # Check for name update
        new_name_match = re.search(r"name\s+['\"]?([^'\"]*?)['\"]?(?:\s+(?:priority|status)|\s*$)", user_input, re.IGNORECASE)
        if new_name_match:
            updates["name"] = new_name_match.group(1).strip()
        
        # Check for priority update
        priority_match = re.search(r"priority\s+(\w+)", user_input, re.IGNORECASE)
        if priority_match:
            priority_value = priority_match.group(1).lower()
            if priority_value in ["high", "low", "medium"]:
                updates["priority"] = priority_value.capitalize()
        
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
        
        # Check for estimated hours update
        estimated_match = re.search(r"estimated\s+(\d+)\s+hour", user_input, re.IGNORECASE)
        if estimated_match:
            updates["estimated_hours"] = float(estimated_match.group(1))
        
        if not updates:
            return self._format_response(
                f"No updates specified. Try: \"update task '{task_name}' priority high\""
            )
        
        # Apply updates
        result = database.update_task(task_id_to_update, **updates)
        
        if result["success"]:
            response = f"✓ Task '{task_name}' updated successfully!\n"
            for key, value in updates.items():
                response += f"  • {key}: {value}\n"
        else:
            response = f"❌ {result['message']}"
        
        return self._format_response(response, result)
    
    def _handle_show_tasks(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Show all tasks"""
        
        projects = database.get_all_projects()
        if not projects:
            return self._format_response("No projects yet.")
        
        project_id = projects[0]["id"]
        status = database.get_project_status(project_id)
        tasks = status.get("tasks", [])
        
        if not tasks:
            response = f"No tasks in project '{status['name']}' yet."
        else:
            response = f"📋 **Tasks in {status['name']}:**\n"
            for task in tasks:
                status_icon = "✓" if task["status"] == "Completed" else "⏳"
                response += f"\n{status_icon} {task['name']}\n"
                response += f"   Status: {task['status']} | {task['completion']}% complete\n"
                response += f"   Effort: {task['actual']}/{task['estimated']} hours"
                if task["priority"] != "Medium":
                    response += f" | Priority: {task['priority']}"
                response += "\n"
        
        return self._format_response(response, {"tasks": tasks})
    
    def _handle_project_metrics(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Show project metrics"""
        
        projects = database.get_all_projects()
        if not projects:
            return self._format_response("No projects yet.")
        
        project_id = projects[0]["id"]
        status = database.get_project_status(project_id)
        
        # Calculate burndown-style metrics
        total_estimated = status["estimated_hours"]
        total_actual = status["actual_hours"]
        remaining = max(0, total_estimated - total_actual)
        
        # Estimate completion rate
        if total_actual > 0 and status["overall_completion"] > 0:
            completion_rate = total_actual / status["overall_completion"] if status["overall_completion"] > 0 else 0
            estimated_hours_to_complete = remaining / completion_rate if completion_rate > 0 else total_estimated
        else:
            estimated_hours_to_complete = total_estimated
        
        response = f"📊 **Metrics for {status['name']}:**\n"
        response += f"\nCompletion: {status['overall_completion']}%\n"
        response += f"Tasks: {status['completed_tasks']}/{status['total_tasks']} done\n"
        response += f"\nTime Budget:\n"
        response += f"  Estimated: {total_estimated:.1f}h\n"
        response += f"  Actual: {total_actual:.1f}h\n"
        response += f"  Remaining: {remaining:.1f}h\n"
        
        if total_estimated > 0:
            efficiency = (total_actual / total_estimated) * 100
            response += f"  Efficiency: {efficiency:.0f}%\n"
        
        return self._format_response(response, {
            "completion": status["overall_completion"],
            "total_estimated": total_estimated,
            "total_actual": total_actual,
            "remaining": remaining
        })
    
    def _handle_default(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Handle unrecognized input"""
        response = f"I can help with tasks:\n"
        response += "• \"Add task 'Name' for person, hours, priority\"\n"
        response += "• \"Update 'TaskName' to 50% complete, spent 3 hours\"\n"
        response += "• \"Show all tasks\"\n"
        response += "• \"Show metrics\""
        
        return self._format_response(response)
