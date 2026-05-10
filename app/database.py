"""
Database models and initialization
Handles SQLite database for projects, tasks, and team members
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import history tracking
from app.history import ActionHistory, ActionType

# Database file location
DB_PATH = Path(__file__).parent.parent / "data" / "projects.db"

# Global history instance
history = ActionHistory()

def init_db():
    """Initialize database with all required tables"""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Team Members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            capacity_hours REAL DEFAULT 40,
            available BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            timeline_days INTEGER,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            assigned_to_id INTEGER,
            estimated_hours REAL,
            actual_hours REAL DEFAULT 0,
            completion_percentage INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Not Started',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assigned_to_id) REFERENCES team_members(id)
        )
    ''')
    
    # Project Progress table (for tracking history)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            overall_completion INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Data access functions

def add_team_member(name: str, role: str, capacity_hours: float = 40) -> Dict[str, Any]:
    """Add a new team member"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO team_members (name, role, capacity_hours)
            VALUES (?, ?, ?)
        ''', (name, role, capacity_hours))
        
        conn.commit()
        member_id = cursor.lastrowid
        
        # Record action in history
        after_state = {
            "id": member_id,
            "name": name,
            "role": role,
            "capacity_hours": capacity_hours
        }
        history.record_action(
            ActionType.ADD_TEAM_MEMBER,
            f"Added team member: {name}",
            "team_member",
            member_id,
            None,
            after_state
        )
        
        return {
            "success": True,
            "id": member_id,
            "name": name,
            "role": role,
            "message": f"Team member '{name}' added successfully"
        }
    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": f"Team member '{name}' already exists"
        }
    finally:
        conn.close()

def get_all_team_members() -> List[Dict[str, Any]]:
    """Get all team members"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, role, capacity_hours, available FROM team_members')
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "name": row[1],
            "role": row[2],
            "capacity_hours": row[3],
            "available": row[4]
        }
        for row in rows
    ]

def get_team_member(member_id: int) -> Optional[Dict[str, Any]]:
    """Get a team member by ID"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, role, capacity_hours, available FROM team_members WHERE id = ?', (member_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "role": row[2],
        "capacity_hours": row[3],
        "available": row[4]
    }


def get_team_member_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a team member by name"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, role, capacity_hours, available FROM team_members WHERE LOWER(name) = LOWER(?)', (name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "role": row[2],
        "capacity_hours": row[3],
        "available": row[4]
    }


def create_project(name: str, description: str, timeline_days: int) -> Dict[str, Any]:
    """Create a new project"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO projects (name, description, timeline_days)
            VALUES (?, ?, ?)
        ''', (name, description, timeline_days))
        
        conn.commit()
        project_id = cursor.lastrowid
        
        # Record action in history
        after_state = {
            "id": project_id,
            "name": name,
            "description": description,
            "timeline_days": timeline_days,
            "status": "Active"
        }
        history.record_action(
            ActionType.CREATE_PROJECT,
            f"Created project: {name}",
            "project",
            project_id,
            None,
            after_state
        )
        
        return {
            "success": True,
            "id": project_id,
            "name": name,
            "message": f"Project '{name}' created successfully"
        }
    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": f"Project '{name}' already exists"
        }
    finally:
        conn.close()

def add_task(project_id: int, name: str, description: str, assigned_to_id: Optional[int], 
             estimated_hours: float, priority: str = "Medium") -> Dict[str, Any]:
    """Add a task to a project"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO tasks (project_id, name, description, assigned_to_id, estimated_hours, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_id, name, description, assigned_to_id, estimated_hours, priority))
        
        conn.commit()
        task_id = cursor.lastrowid
        
        # Record action in history
        after_state = {
            "id": task_id,
            "project_id": project_id,
            "name": name,
            "description": description,
            "assigned_to_id": assigned_to_id,
            "estimated_hours": estimated_hours,
            "priority": priority
        }
        history.record_action(
            ActionType.ADD_TASK,
            f"Added task: {name}",
            "task",
            task_id,
            None,
            after_state
        )
        
        return {
            "success": True,
            "id": task_id,
            "name": name,
            "message": f"Task '{name}' added successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding task: {str(e)}"
        }
    finally:
        conn.close()

def update_task_progress(task_id: int, completion_percentage: int, actual_hours: float) -> Dict[str, Any]:
    """Update task progress"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Get before state
        cursor.execute('''
            SELECT completion_percentage, actual_hours FROM tasks WHERE id = ?
        ''', (task_id,))
        before_result = cursor.fetchone()
        before_state = {
            "id": task_id,
            "completion_percent": before_result[0],
            "actual_hours": before_result[1]
        } if before_result else None
        
        cursor.execute('''
            UPDATE tasks 
            SET completion_percentage = ?, actual_hours = ?, 
                status = CASE WHEN ? = 100 THEN 'Completed' ELSE 'In Progress' END
            WHERE id = ?
        ''', (completion_percentage, actual_hours, completion_percentage, task_id))
        
        conn.commit()
        
        # Record action in history
        after_state = {
            "id": task_id,
            "completion_percent": completion_percentage,
            "actual_hours": actual_hours
        }
        history.record_action(
            ActionType.UPDATE_TASK_PROGRESS,
            f"Updated task progress to {completion_percentage}%",
            "task",
            task_id,
            before_state,
            after_state
        )
        
        return {
            "success": True,
            "message": f"Task updated to {completion_percentage}% complete"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating task: {str(e)}"
        }
    finally:
        conn.close()

def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    """Get a project by ID"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, timeline_days, status FROM projects WHERE id = ?', (project_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "timeline_days": row[3],
        "status": row[4]
    }


def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    """Get task details by ID"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, project_id, name, description, assigned_to_id, estimated_hours, actual_hours, completion_percentage, priority, status
        FROM tasks WHERE id = ?
    ''', (task_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "project_id": row[1],
        "name": row[2],
        "description": row[3],
        "assigned_to_id": row[4],
        "estimated_hours": row[5],
        "actual_hours": row[6],
        "completion_percentage": row[7],
        "priority": row[8],
        "status": row[9]
    }


def update_project(project_id: int, name: Optional[str] = None, description: Optional[str] = None,
                   timeline_days: Optional[int] = None, status: Optional[str] = None) -> Dict[str, Any]:
    """Update project properties"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, description, timeline_days, status FROM projects WHERE id = ?', (project_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"success": False, "message": "Project not found"}

    before_state = {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "timeline_days": row[3],
        "status": row[4]
    }

    updates = []
    params = []
    if name is not None and name != row[1]:
        updates.append('name = ?')
        params.append(name)
    if description is not None and description != row[2]:
        updates.append('description = ?')
        params.append(description)
    if timeline_days is not None and timeline_days != row[3]:
        updates.append('timeline_days = ?')
        params.append(timeline_days)
    if status is not None and status != row[4]:
        updates.append('status = ?')
        params.append(status)

    if not updates:
        conn.close()
        return {"success": False, "message": "No changes detected for project"}

    params.append(project_id)
    try:
        cursor.execute(f'UPDATE projects SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()

        after_state = {
            "id": project_id,
            "name": name if name is not None else row[1],
            "description": description if description is not None else row[2],
            "timeline_days": timeline_days if timeline_days is not None else row[3],
            "status": status if status is not None else row[4]
        }
        history.record_action(
            ActionType.UPDATE_PROJECT,
            f"Updated project: {after_state['name']}",
            "project",
            project_id,
            before_state,
            after_state
        )

        conn.close()
        return {"success": True, "message": f"Project '{after_state['name']}' updated successfully"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "Project name already exists"}


def update_team_member(member_id: int, name: Optional[str] = None, role: Optional[str] = None,
                       capacity_hours: Optional[float] = None, available: Optional[bool] = None) -> Dict[str, Any]:
    """Update team member properties"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, role, capacity_hours, available FROM team_members WHERE id = ?', (member_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"success": False, "message": "Team member not found"}

    before_state = {
        "id": row[0],
        "name": row[1],
        "role": row[2],
        "capacity_hours": row[3],
        "available": bool(row[4])
    }

    updates = []
    params = []
    if name is not None and name != row[1]:
        updates.append('name = ?')
        params.append(name)
    if role is not None and role != row[2]:
        updates.append('role = ?')
        params.append(role)
    if capacity_hours is not None and capacity_hours != row[3]:
        updates.append('capacity_hours = ?')
        params.append(capacity_hours)
    if available is not None and available != bool(row[4]):
        updates.append('available = ?')
        params.append(1 if available else 0)

    if not updates:
        conn.close()
        return {"success": False, "message": "No changes detected for team member"}

    params.append(member_id)
    try:
        cursor.execute(f'UPDATE team_members SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()

        after_state = {
            "id": member_id,
            "name": name if name is not None else row[1],
            "role": role if role is not None else row[2],
            "capacity_hours": capacity_hours if capacity_hours is not None else row[3],
            "available": available if available is not None else bool(row[4])
        }
        history.record_action(
            ActionType.UPDATE_TEAM_MEMBER,
            f"Updated team member: {after_state['name']}",
            "team_member",
            member_id,
            before_state,
            after_state
        )

        conn.close()
        return {"success": True, "message": f"Team member '{after_state['name']}' updated successfully"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "Team member name already exists"}


def update_task(task_id: int, name: Optional[str] = None, description: Optional[str] = None,
                assigned_to_id: Optional[int] = None, estimated_hours: Optional[float] = None,
                priority: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
    """Update task properties"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, project_id, name, description, assigned_to_id, estimated_hours, actual_hours, completion_percentage, priority, status
        FROM tasks WHERE id = ?
    ''', (task_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"success": False, "message": "Task not found"}

    before_state = {
        "id": row[0],
        "project_id": row[1],
        "name": row[2],
        "description": row[3],
        "assigned_to_id": row[4],
        "estimated_hours": row[5],
        "actual_hours": row[6],
        "completion_percent": row[7],
        "priority": row[8],
        "status": row[9]
    }

    updates = []
    params = []
    if name is not None and name != row[2]:
        updates.append('name = ?')
        params.append(name)
    if description is not None and description != row[3]:
        updates.append('description = ?')
        params.append(description)
    if assigned_to_id is not None and assigned_to_id != row[4]:
        updates.append('assigned_to_id = ?')
        params.append(assigned_to_id)
    if estimated_hours is not None and estimated_hours != row[5]:
        updates.append('estimated_hours = ?')
        params.append(estimated_hours)
    if priority is not None and priority != row[8]:
        updates.append('priority = ?')
        params.append(priority)
    if status is not None and status != row[9]:
        updates.append('status = ?')
        params.append(status)

    if not updates:
        conn.close()
        return {"success": False, "message": "No changes detected for task"}

    params.append(task_id)
    cursor.execute(f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?', params)
    conn.commit()

    after_state = {
        "id": task_id,
        "project_id": row[1],
        "name": name if name is not None else row[2],
        "description": description if description is not None else row[3],
        "assigned_to_id": assigned_to_id if assigned_to_id is not None else row[4],
        "estimated_hours": estimated_hours if estimated_hours is not None else row[5],
        "actual_hours": row[6],
        "completion_percent": row[7],
        "priority": priority if priority is not None else row[8],
        "status": status if status is not None else row[9]
    }
    history.record_action(
        ActionType.UPDATE_TASK,
        f"Updated task: {after_state['name']}",
        "task",
        task_id,
        before_state,
        after_state
    )
    conn.close()
    return {"success": True, "message": f"Task '{after_state['name']}' updated successfully"}


def get_project_status(project_id: int) -> Dict[str, Any]:
    """Get comprehensive project status"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get project info
    cursor.execute('SELECT name, description, timeline_days FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    
    if not project:
        return {"error": "Project not found"}
    
    # Get all tasks
    cursor.execute('''
        SELECT id, name, assigned_to_id, estimated_hours, actual_hours, completion_percentage, status, priority
        FROM tasks WHERE project_id = ?
    ''', (project_id,))
    tasks = cursor.fetchall()
    
    conn.close()
    
    # Calculate metrics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t[6] == 'Completed')
    total_estimated = sum(t[3] for t in tasks if t[3])
    total_actual = sum(t[4] for t in tasks if t[4])
    avg_completion = sum(t[5] for t in tasks) / total_tasks if total_tasks > 0 else 0
    
    # Get team info
    cursor = sqlite3.connect(str(DB_PATH)).cursor()
    assigned_team = set()
    for task in tasks:
        if task[2]:  # assigned_to_id
            cursor.execute('SELECT name, role FROM team_members WHERE id = ?', (task[2],))
            member = cursor.fetchone()
            if member:
                assigned_team.add(member)
    
    return {
        "project_id": project_id,
        "name": project[0],
        "description": project[1],
        "timeline_days": project[2],
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overall_completion": int(avg_completion),
        "estimated_hours": total_estimated,
        "actual_hours": total_actual,
        "team_members": list(assigned_team),
        "tasks": [
            {
                "id": t[0],
                "name": t[1],
                "completion": t[5],
                "status": t[6],
                "priority": t[7],
                "estimated": t[3],
                "actual": t[4]
            }
            for t in tasks
        ]
    }

def get_team_workload(project_id: int) -> Dict[str, Any]:
    """Get team member workload for a project"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tm.id, tm.name, tm.role, tm.capacity_hours,
               COUNT(t.id) as task_count,
               SUM(CASE WHEN t.status != 'Completed' THEN t.estimated_hours ELSE 0 END) as remaining_hours
        FROM team_members tm
        LEFT JOIN tasks t ON tm.id = t.assigned_to_id AND t.project_id = ?
        GROUP BY tm.id
    ''', (project_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    workload = []
    for row in rows:
        utilization = (row[5] or 0) / row[3] * 100 if row[3] > 0 else 0
        workload.append({
            "name": row[1],
            "role": row[2],
            "capacity": row[3],
            "task_count": row[4] or 0,
            "remaining_hours": row[5] or 0,
            "utilization_percentage": min(100, int(utilization))
        })
    
    return {"project_id": project_id, "team_workload": workload}

def get_all_projects() -> List[Dict[str, Any]]:
    """Get all projects"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, description, timeline_days, status FROM projects')
    rows = cursor.fetchall()
    conn.close()
    
    projects = []
    for row in rows:
        status = get_project_status(row[0])
        projects.append({
            "id": row[0],
            "name": row[1],
            "completion": status.get("overall_completion", 0),
            "timeline_days": row[3],
            "status": row[4]
        })
    
    return projects

# Undo/Redo operations

def get_action_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent action history"""
    return history.get_history(limit)

def undo_last_action() -> Dict[str, Any]:
    """Undo the last action"""
    return history.undo_last_action()

def redo_last_action() -> Dict[str, Any]:
    """Redo the last undone action"""
    return history.redo_last_action()

def can_undo() -> bool:
    """Check if undo is available"""
    return history.can_undo()

def can_redo() -> bool:
    """Check if redo is available"""
    return history.can_redo()
