"""
Streamlit Web UI for AI Project Management System
Fast, interactive web interface for the demo
"""

import sys
import os
from pathlib import Path

# Add project root to path so imports work correctly
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.main import get_agent_team, get_system_overview
from app import database

# Page configuration
st.set_page_config(
    page_title="AI Project Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stDataFrame, .stTable {
        overflow-x: auto;
        display: block;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "show_history" not in st.session_state:
    st.session_state.show_history = False

# Get agent team
agent_team = get_agent_team()

# Main layout
def main():
    # Header
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("# 🤖 AI Project Management System")
        st.markdown("*Manage projects using natural language*")
    
    with col2:
        if st.button("🔄 Refresh"):
            st.experimental_rerun()
    
    # Sidebar - Navigation
    with st.sidebar:
        st.markdown("## 📑 Navigation")
        page = st.radio("Select view:", [
            "Dashboard",
            "Chat Interface",
            "Projects",
            "Team",
            "Tasks",
            "Reports"
        ], index=["Dashboard", "Chat Interface", "Projects", "Team", "Tasks", "Reports"].index(st.session_state.page))
        st.session_state.page = page
        
        # Undo/Redo Controls
        st.markdown("---")
        st.markdown("## ↩️ Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⬅️ Undo", disabled=not database.can_undo(), use_container_width=True):
                result = database.undo_last_action()
                if result['success']:
                    st.success(f"✓ {result['message']}")
                    st._rerun()
                else:
                    st.error(f"✗ {result['message']}")
        
        with col2:
            if st.button("➡️ Redo", disabled=not database.can_redo(), use_container_width=True):
                result = database.redo_last_action()
                if result['success']:
                    st.success(f"✓ {result['message']}")
                    st.experimental_rerun()
                else:
                    st.error(f"✗ {result['message']}")
        
        with col3:
            if st.button("📋 History", use_container_width=True):
                st.session_state.show_history = True
        
        # Action History
        if st.session_state.get("show_history", False):
            st.markdown("### Recent Actions")
            history_items = database.get_action_history(limit=10)
            for item in history_items:
                status = "↩️ Undone" if item['is_undone'] else "✓ Done"
                st.text(f"{item['action_name']} - {status}")
                st.caption(item['timestamp'])
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Chat Interface":
        show_chat()
    elif page == "Projects":
        show_projects()
    elif page == "Team":
        show_team()
    elif page == "Tasks":
        show_tasks()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    """Show main dashboard"""
    st.markdown("## 📊 Dashboard Overview")
    
    overview = get_system_overview()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Projects", overview["total_projects"], delta=None)
    
    with col2:
        st.metric("👥 Team Members", overview["total_team_members"], delta=None)
    
    with col3:
        st.metric("📊 Avg Completion", f"{overview['average_completion']}%", delta=None)
    
    with col4:
        active_projects = len([p for p in overview["projects"] if p["completion"] < 100])
        st.metric("🔄 Active Projects", active_projects, delta=None)
    
    # Projects list
    if overview["projects"]:
        st.markdown("### Recent Projects")
        
        projects_data = []
        for proj in overview["projects"]:
            projects_data.append({
                "Project": proj["name"],
                "Timeline": f"{proj['timeline_days']} days",
                "Completion": f"{proj['completion']}%",
                "Status": "✓ Complete" if proj["completion"] == 100 else "⏳ In Progress"
            })
        
        st.markdown("<div style='width:100%; overflow-x:auto;'>", unsafe_allow_html=True)
        st.table(projects_data)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Completion chart
        if len(overview["projects"]) > 0:
            fig = go.Figure(data=[
                go.Bar(
                    x=[p["name"] for p in overview["projects"]],
                    y=[p["completion"] for p in overview["projects"]],
                    text=[f"{p['completion']}%" for p in overview["projects"]],
                    textposition="auto",
                    marker=dict(color=[p["completion"] for p in overview["projects"]], 
                              colorscale="Viridis")
                )
            ])
            fig.update_layout(
                title="Project Completion Status",
                xaxis_title="Project",
                yaxis_title="Completion %",
                yaxis=dict(range=[0, 100]),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No projects yet. Create one using the Chat Interface!")

def show_chat():
    """Show chat interface"""
    st.markdown("## 💬 Chat with AI Manager")
    
    st.markdown("""
    **Quick commands:**
    - Create project called MyProject with 2 weeks timeline
    - Add John as Backend Developer, capacity 40 hours
    - Add task 'Design UI' for John, 5 hours, high priority
    - Update 'Design UI' to 50% complete, spent 3 hours
    - Show team workload
    - What's the project status?
    """)
    
    st.divider()
    
    # Message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Input
    if user_input := st.chat_input("Type your command..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Processing..."):
                result = agent_team.process_input(user_input)
                response_text = result.get("response", "No response")
                st.markdown(response_text)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
                
                # Show structured data if available
                if result.get("data"):
                    with st.expander("📊 Structured Data"):
                        st.json(result["data"])

def show_projects():
    """Show projects view"""
    st.markdown("## 📁 Projects")
    
    projects = database.get_all_projects()
    
    if not projects:
        st.info("No projects yet. Create one via the chat!")
    else:
        for proj in projects:
            with st.container():
                col1, col2, col3 = st.columns([0.5, 0.2, 0.3])
                
                with col1:
                    st.markdown(f"### {proj['name']}")
                    status_info = database.get_project_status(proj['id'])
                    st.markdown(f"**Completion:** {proj['completion']}%")
                    st.progress(proj['completion'] / 100)
                    st.markdown(f"**Timeline:** {proj['timeline_days']} days")
                    st.markdown(f"**Tasks:** {status_info['completed_tasks']}/{status_info['total_tasks']}")
                
                with col2:
                    if proj['completion'] == 100:
                        st.success("✓ Complete")
                    else:
                        st.info("⏳ In Progress")
                
                with col3:
                    pass  # Placeholder for spacing
                
                # Edit form using expander
                with st.expander("✏️ Edit Project"):
                    with st.form(f"edit_project_{proj['id']}"):
                        new_name = st.text_input("Project Name", value=proj['name'])
                        new_desc = st.text_area("Description", value=proj.get('description', ''))
                        new_timeline = st.number_input("Timeline (days)", value=proj['timeline_days'] or 1, min_value=1)
                        new_status = st.selectbox("Status", ["In Progress", "Completed"], 
                                                  index=0 if proj['completion'] < 100 else 1)
                        
                        if st.form_submit_button("💾 Save Changes"):
                            result = database.update_project(
                                proj['id'],
                                name=new_name if new_name != proj['name'] else None,
                                description=new_desc if new_desc != proj.get('description', '') else None,
                                timeline_days=new_timeline if new_timeline != proj['timeline_days'] else None,
                                status=new_status
                            )
                            if result["success"]:
                                st.success(f"✓ {result['message']}")
                                st._rerun()
                            else:
                                st.error(f"❌ {result['message']}")
                
                st.divider()

def show_team():
    """Show team view"""
    st.markdown("## 👥 Team Members")
    
    members = database.get_all_team_members()
    
    if not members:
        st.info("No team members yet. Add one via the chat!")
    else:
        # Team overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Members", len(members))
        with col2:
            total_capacity = sum(m["capacity_hours"] for m in members)
            st.metric("Total Capacity", f"{total_capacity}h/week")
        
        st.divider()
        
        # Team members list with edit expanders
        st.markdown("### Team Directory")
        for member in members:
            col1, col2, col3, col4 = st.columns([0.3, 0.2, 0.2, 0.3])
            
            with col1:
                st.write(f"**{member['name']}**")
            with col2:
                st.write(member['role'])
            with col3:
                st.write(f"{member['capacity_hours']}h/week")
            with col4:
                st.write("✓ Available" if member["available"] else "⏸ Busy")
            
            # Edit form using expander
            with st.expander(f"✏️ Edit {member['name']}"):
                with st.form(f"edit_member_{member['id']}"):
                    new_name = st.text_input("Name", value=member['name'])
                    new_role = st.text_input("Role", value=member['role'])
                    new_capacity = st.number_input("Capacity (hours/week)", value=member['capacity_hours'], min_value=0.0)
                    new_available = st.checkbox("Available", value=member['available'])
                    
                    if st.form_submit_button("💾 Save"):
                        result = database.update_team_member(
                            member['id'],
                            name=new_name if new_name != member['name'] else None,
                            role=new_role if new_role != member['role'] else None,
                            capacity_hours=new_capacity if new_capacity != member['capacity_hours'] else None,
                            available=new_available if new_available != member['available'] else None
                        )
                        if result["success"]:
                            st.success(f"✓ {result['message']}")
                            st._rerun()
                        else:
                            st.error(f"❌ {result['message']}")
            
            st.divider()
        
        # Old table display removed - using individual rows with edit buttons instead

def show_tasks():
    """Show tasks view"""
    st.markdown("## 📋 Tasks")
    
    projects = database.get_all_projects()
    
    if not projects:
        st.info("No projects yet.")
        return
    
    # Select project
    selected_project = st.selectbox(
        "Select project:",
        options=projects,
        format_func=lambda p: p["name"]
    )
    
    if selected_project:
        status = database.get_project_status(selected_project["id"])
        tasks = status.get("tasks", [])
        
        if not tasks:
            st.info("No tasks in this project yet.")
        else:
            # Task statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tasks", len(tasks))
            with col2:
                completed = sum(1 for t in tasks if t["status"] == "Completed")
                st.metric("Completed", completed)
            with col3:
                total_hours = sum(t["estimated"] for t in tasks if t["estimated"])
                st.metric("Total Hours", f"{total_hours:.0f}h")
            
            st.divider()
            
            # Tasks list with edit expanders
            st.markdown("### Task List")
            for task in tasks:
                col1, col2, col3, col4, col5 = st.columns([0.25, 0.2, 0.15, 0.15, 0.25])
                
                with col1:
                    st.write(f"**{task['name']}**")
                with col2:
                    st.write(task["status"])
                with col3:
                    st.write(f"{task['completion']}%")
                with col4:
                    st.write(task["priority"])
                with col5:
                    st.write(f"{task['actual'] or 0:.1f}/{task['estimated'] or 0:.1f}h")
                
                # Edit form using expander
                with st.expander(f"✏️ Edit {task['name']}"):
                    with st.form(f"edit_task_{task['id']}"):
                        new_name = st.text_input("Task Name", value=task['name'])
                        new_desc = st.text_area("Description", value=task.get('description', ''), height=60)
                        new_priority = st.selectbox("Priority", ["Low", "Medium", "High"], 
                                                   index=["Low", "Medium", "High"].index(task['priority']))
                        new_status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"],
                                                 index=0 if task['status'] == "Not Started" else (1 if task['status'] == "In Progress" else 2))
                        new_estimated = st.number_input("Estimated Hours", value=task['estimated'] or 0.0, min_value=0.0)
                        
                        if st.form_submit_button("💾 Save"):
                            result = database.update_task(
                                task['id'],
                                name=new_name if new_name != task['name'] else None,
                                description=new_desc if new_desc != task.get('description', '') else None,
                                priority=new_priority if new_priority != task['priority'] else None,
                                status=new_status if new_status != task['status'] else None,
                                estimated_hours=new_estimated if new_estimated != (task['estimated'] or 0.0) else None
                            )
                            if result["success"]:
                                st.success(f"✓ {result['message']}")
                                st._rerun()
                            else:
                                st.error(f"❌ {result['message']}")
                
                st.divider()
            
            # Progress visualization
            fig = go.Figure(data=[
                go.Bar(
                    x=[t["name"] for t in tasks],
                    y=[t["completion"] for t in tasks],
                    text=[f"{t['completion']}%" for t in tasks],
                    textposition="auto",
                    marker=dict(color=[t["completion"] for t in tasks],
                              colorscale="RdYlGn")
                )
            ])
            fig.update_layout(
                title="Task Progress",
                xaxis_title="Task",
                yaxis_title="Completion %",
                yaxis=dict(range=[0, 100]),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

def show_reports():
    """Show reports view"""
    st.markdown("## 📊 Reports")
    
    projects = database.get_all_projects()
    
    if not projects:
        st.info("No projects yet.")
        return
    
    overview = get_system_overview()
    
    # Summary report
    st.markdown("### Summary Report")
    st.markdown(f"""
    **System Status**
    - Projects: {overview['total_projects']}
    - Team Members: {overview['total_team_members']}
    - Average Completion: {overview['average_completion']}%
    """)
    
    st.divider()
    
    # Project reports
    st.markdown("### Project Reports")
    for proj in projects:
        with st.expander(f"📄 {proj['name']} Report"):
            status = database.get_project_status(proj['id'])
            
            st.markdown(f"""
            **Project Details**
            - Name: {status['name']}
            - Timeline: {status['timeline_days']} days
            - Completion: {status['overall_completion']}%
            - Tasks: {status['completed_tasks']}/{status['total_tasks']} done
            
            **Hours**
            - Estimated: {status['estimated_hours']:.1f}h
            - Actual: {status['actual_hours']:.1f}h
            - Remaining: {max(0, status['estimated_hours'] - status['actual_hours']):.1f}h
            """)

if __name__ == "__main__":
    main()
