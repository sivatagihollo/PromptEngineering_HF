"""
Action History and Undo/Redo System
Tracks all modifications and enables undoing/redoing actions
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum

# Database file location
DB_PATH = Path(__file__).parent.parent / "data" / "projects.db"


class ActionType(Enum):
    """Types of actions that can be tracked"""
    ADD_TEAM_MEMBER = "add_team_member"
    REMOVE_TEAM_MEMBER = "remove_team_member"
    UPDATE_TEAM_MEMBER = "update_team_member"
    CREATE_PROJECT = "create_project"
    DELETE_PROJECT = "delete_project"
    UPDATE_PROJECT = "update_project"
    ADD_TASK = "add_task"
    DELETE_TASK = "delete_task"
    UPDATE_TASK_PROGRESS = "update_task_progress"
    UPDATE_TASK = "update_task"


class ActionHistory:
    """Manages action history and undo/redo operations"""
    
    def __init__(self):
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self._init_history_table()
    
    def _init_history_table(self):
        """Initialize action_history table if it doesn't exist"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                action_name TEXT NOT NULL,
                target_type TEXT,
                target_id INTEGER,
                before_state TEXT,
                after_state TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_undone BOOLEAN DEFAULT 0,
                undone_at TIMESTAMP,
                undo_order INTEGER
            )
        ''')
        cursor.execute('PRAGMA table_info(action_history)')
        columns = [row[1] for row in cursor.fetchall()]
        if 'undone_at' not in columns:
            cursor.execute('ALTER TABLE action_history ADD COLUMN undone_at TIMESTAMP')
        if 'undo_order' not in columns:
            cursor.execute('ALTER TABLE action_history ADD COLUMN undo_order INTEGER')
        conn.commit()
        conn.close()
    
    def record_action(
        self,
        action_type: ActionType,
        action_name: str,
        target_type: str,
        target_id: Optional[int] = None,
        before_state: Optional[Dict] = None,
        after_state: Optional[Dict] = None
    ) -> int:
        """
        Record an action in history
        
        Args:
            action_type: Type of action performed
            action_name: Human-readable action name
            target_type: Type of object affected (team_member, project, task, etc.)
            target_id: ID of the affected object
            before_state: State before action
            after_state: State after action
        
        Returns:
            ID of recorded action
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO action_history
            (action_type, action_name, target_type, target_id, before_state, after_state)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            action_type.value,
            action_name,
            target_type,
            target_id,
            json.dumps(before_state) if before_state else None,
            json.dumps(after_state) if after_state else None
        ))
        
        action_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Clear redo stack and remove any undone history once a new action is recorded
        self.redo_stack.clear()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM action_history WHERE is_undone = 1')
        conn.commit()
        conn.close()
        
        return action_id
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent action history"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, action_type, action_name, target_type, target_id,
                   before_state, after_state, timestamp, is_undone
            FROM action_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'action_type': row[1],
                'action_name': row[2],
                'target_type': row[3],
                'target_id': row[4],
                'before_state': json.loads(row[5]) if row[5] else None,
                'after_state': json.loads(row[6]) if row[6] else None,
                'timestamp': row[7],
                'is_undone': bool(row[8])
            })
        
        return history
    
    def undo_last_action(self) -> Dict[str, Any]:
        """
        Undo the last action
        
        Returns:
            Dictionary with action details and undo result
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get the last non-undone action
        cursor.execute('''
            SELECT * FROM action_history
            WHERE is_undone = 0
            ORDER BY timestamp DESC, id DESC
            LIMIT 1
        ''')
        
        action = cursor.fetchone()
        
        if not action:
            conn.close()
            return {'success': False, 'message': 'No actions to undo'}
        
        action_id = action[0]
        action_type = action[1]
        before_state = json.loads(action[5]) if action[5] else None
        after_state = json.loads(action[6]) if action[6] else None
        
        result = self._execute_undo(cursor, action_type, before_state, after_state, action[4])
        
        # Mark action as undone
        cursor.execute('''
            UPDATE action_history
            SET is_undone = 1,
                undone_at = CURRENT_TIMESTAMP,
                undo_order = (SELECT IFNULL(MAX(undo_order), 0) + 1 FROM action_history)
            WHERE id = ?
        ''', (action_id,))
        conn.commit()
        conn.close()
        
        if result['success']:
            self.undo_stack.append(action)
        
        return result
    
    def redo_last_action(self) -> Dict[str, Any]:
        """
        Redo the last undone action
        
        Returns:
            Dictionary with action details and redo result
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get the last undone action in the exact undo order
        cursor.execute('''
            SELECT * FROM action_history
            WHERE is_undone = 1
            ORDER BY undo_order DESC, undone_at DESC, timestamp DESC
            LIMIT 1
        ''')
        
        action = cursor.fetchone()
        
        if not action:
            conn.close()
            return {'success': False, 'message': 'No actions to redo'}
        
        action_id = action[0]
        action_type = action[1]
        after_state = json.loads(action[6]) if action[6] else None
        
        result = self._execute_redo(cursor, action_type, after_state, action[4])
        
        # Mark action as not undone
        cursor.execute('UPDATE action_history SET is_undone = 0 WHERE id = ?', (action_id,))
        conn.commit()
        conn.close()
        
        if result['success']:
            self.redo_stack.append(action)
        
        return result
    
    def _execute_undo(self, cursor, action_type: str, before_state: Dict, after_state: Dict, target_id: int) -> Dict[str, Any]:
        """Execute the actual undo operation based on action type"""
        try:
            if action_type == ActionType.ADD_TEAM_MEMBER.value:
                member_id = target_id or (after_state and after_state.get('id'))
                cursor.execute('DELETE FROM team_members WHERE id = ?', (member_id,))
                return {'success': True, 'message': "Undone: Added team member"}
            
            elif action_type == ActionType.REMOVE_TEAM_MEMBER.value:
                source = before_state or after_state
                cursor.execute('''
                    INSERT INTO team_members (id, name, role, capacity_hours, available)
                    VALUES (?, ?, ?, ?, ?)
                ''', (source.get('id'), source.get('name'), 
                      source.get('role'), source.get('capacity_hours'), 1))
                return {'success': True, 'message': "Undone: Removed team member"}
            
            elif action_type == ActionType.CREATE_PROJECT.value:
                project_id = target_id or (after_state and after_state.get('id'))
                cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
                return {'success': True, 'message': "Undone: Created project"}
            
            elif action_type == ActionType.DELETE_PROJECT.value:
                source = before_state or after_state
                cursor.execute('''
                    INSERT INTO projects (id, name, description, timeline_days, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (source.get('id'), source.get('name'),
                      source.get('description'), source.get('timeline_days'),
                      source.get('status')))
                return {'success': True, 'message': "Undone: Deleted project"}
            
            elif action_type == ActionType.ADD_TASK.value:
                task_id = target_id or (after_state and after_state.get('id'))
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                return {'success': True, 'message': "Undone: Added task"}
            
            elif action_type == ActionType.UPDATE_TASK_PROGRESS.value:
                if not before_state:
                    return {'success': False, 'message': 'Cannot undo task progress without before-state'}
                cursor.execute('''
                    UPDATE tasks SET completion_percentage = ?, actual_hours = ?
                    WHERE id = ?
                ''', (before_state.get('completion_percent'), before_state.get('actual_hours'),
                      before_state.get('id')))
                return {'success': True, 'message': "Undone: Updated task progress"}
            
            return {'success': False, 'message': f'Unknown action type: {action_type}'}
        
        except Exception as e:
            return {'success': False, 'message': f'Undo failed: {str(e)}'}
    
    def _execute_redo(self, cursor, action_type: str, after_state: Dict, target_id: int) -> Dict[str, Any]:
        """Execute the actual redo operation based on action type"""
        try:
            if action_type == ActionType.ADD_TEAM_MEMBER.value:
                cursor.execute('''
                    INSERT INTO team_members (id, name, role, capacity_hours, available)
                    VALUES (?, ?, ?, ?, ?)
                ''', (after_state.get('id'), after_state.get('name'), 
                      after_state.get('role'), after_state.get('capacity_hours'), 1))
                return {'success': True, 'message': f"Redone: Added team member"}
            
            elif action_type == ActionType.REMOVE_TEAM_MEMBER.value:
                cursor.execute('DELETE FROM team_members WHERE id = ?', (after_state.get('id'),))
                return {'success': True, 'message': f"Redone: Removed team member"}
            
            elif action_type == ActionType.CREATE_PROJECT.value:
                cursor.execute('''
                    INSERT INTO projects (id, name, description, timeline_days, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (after_state.get('id'), after_state.get('name'),
                      after_state.get('description'), after_state.get('timeline_days'),
                      after_state.get('status')))
                return {'success': True, 'message': f"Redone: Created project"}
            
            elif action_type == ActionType.DELETE_PROJECT.value:
                cursor.execute('DELETE FROM projects WHERE id = ?', (after_state.get('id'),))
                return {'success': True, 'message': f"Redone: Deleted project"}
            
            elif action_type == ActionType.ADD_TASK.value:
                cursor.execute('''
                    INSERT INTO tasks (id, project_id, name, description, assigned_to_id, estimated_hours, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (after_state.get('id'), after_state.get('project_id'), after_state.get('name'),
                      after_state.get('description'), after_state.get('assigned_to_id'),
                      after_state.get('estimated_hours'), after_state.get('priority')))
                return {'success': True, 'message': "Redone: Added task"}
            
            elif action_type == ActionType.UPDATE_TASK_PROGRESS.value:
                cursor.execute('''
                    UPDATE tasks SET completion_percent = ?, actual_hours = ?
                    WHERE id = ?
                ''', (after_state.get('completion_percent'), after_state.get('actual_hours'),
                      after_state.get('id')))
                return {'success': True, 'message': f"Redone: Updated task progress"}
            
            return {'success': False, 'message': f'Unknown action type: {action_type}'}
        
        except Exception as e:
            return {'success': False, 'message': f'Redo failed: {str(e)}'}
    
    def can_undo(self) -> bool:
        """Check if there are actions that can be undone"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM action_history WHERE is_undone = 0')
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def can_redo(self) -> bool:
        """Check if there are actions that can be redone"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM action_history WHERE is_undone = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
