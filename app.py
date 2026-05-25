"""
Support Resolution Agent - Streamlit Frontend
A simplified, premium user interface to interact with the new structured support agent.
"""

import streamlit as st
import uuid
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

# Load environment variables
load_dotenv()

# Import compiled graph
from my_agent.agent import graph

# ============================================================================
# Page Configuration & Styling
# ============================================================================

st.set_page_config(
    page_title="Support Resolution Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background-color: #0f172a;
        background-image: radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.1) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(124, 58, 237, 0.1) 0, transparent 50%);
        font-family: 'Inter', sans-serif;
        color: #f8fafc;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #bae6fd !important;
    }
    
    .main-header {
        background: linear-gradient(90deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
    }
    
    .sub-header {
        color: #94a3b8 !important;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .user-message {
        background: #4f46e5;
        color: #ffffff !important;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.75rem 0;
        margin-left: 20%;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #6366f1;
    }
    
    .agent-message {
        background: #334155;
        color: #f8fafc !important;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.75rem 0;
        margin-right: 20%;
        border: 1px solid #475569;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .info-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Initialization
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "customer_id" not in st.session_state:
    st.session_state.customer_id = ""
if "priority" not in st.session_state:
    st.session_state.priority = "None"
if "workflow_steps" not in st.session_state:
    st.session_state.workflow_steps = []
if "pending_escalation" not in st.session_state:
    st.session_state.pending_escalation = False
if "escalation_context" not in st.session_state:
    st.session_state.escalation_context = None

def reset_conversation():
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.customer_id = ""
    st.session_state.priority = "None"
    st.session_state.workflow_steps = []
    st.session_state.pending_escalation = False
    st.session_state.escalation_context = None

# ============================================================================
# Sidebar Configuration
# ============================================================================

with st.sidebar:
    st.markdown("## 🎯 Support Workspace")
    st.markdown("---")
    
    # Live Customer context inputs
    customer_id_input = st.text_input(
        "CRM Customer ID",
        value=st.session_state.customer_id,
        placeholder="e.g. CUST001"
    )
    if customer_id_input:
        st.session_state.customer_id = customer_id_input
        
    st.markdown("---")
    st.markdown("### 📊 Ticket State")
    st.write(f"**Urgency Priority:** `{st.session_state.priority.upper()}`")
    
    st.markdown("---")
    st.markdown("### 🔄 Workflow Steps")
    workflow_nodes = [
        ("classify_urgency", "⚡ Urgency Classification"),
        ("check_context", "🔍 Context Validation"),
        ("diagnose_and_resolve", "🔧 Diagnostic Tools"),
        ("human_escalation", "👤 Human Escalation"),
        ("deliver_response", "📤 Deliver Response"),
    ]
    
    for node_id, node_label in workflow_nodes:
        if node_id in st.session_state.workflow_steps:
            st.markdown(f"✅ {node_label}")
        elif st.session_state.pending_escalation and node_id == "human_escalation":
            st.markdown(f"⏳ {node_label} *(waiting)*")
        else:
            st.markdown(f"⬜ {node_label}")
            
    st.markdown("---")
    if st.button("🔄 New Conversation", use_container_width=True):
        reset_conversation()
        st.rerun()
        
    st.markdown("### ℹ️ Debug Info")
    st.json({
        "thread_id": st.session_state.thread_id,
        "customer_id": st.session_state.customer_id,
        "pending_escalation": st.session_state.pending_escalation,
    })

# ============================================================================
# Main UI Area
# ============================================================================

st.markdown('<h1 class="main-header">🎯 Support Resolution Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Autonomous customer support resolution agent with Human-in-the-Loop escalation</p>', unsafe_allow_html=True)

# Human Escalation Review Panel
if st.session_state.pending_escalation:
    st.markdown("### 👤 Human Agent Review Required")
    st.warning("This ticket has been auto-escalated for human agent review. Please inspect details below and take action.")
    
    ctx = st.session_state.escalation_context
    if ctx:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Diagnostic Information:**")
            st.info(f"**Customer ID:** {ctx.get('customer_id')}\n\n**Priority:** {ctx.get('priority')}\n\n**Steps Taken:** {ctx.get('resolution_steps')}")
        with col2:
            st.markdown("**Proposed AI Draft:**")
            st.success(ctx.get("draft_response"))
            
    st.markdown("**Action Decision:**")
    action = st.radio("Choose Action", ["Approve Draft", "Modify Response"], horizontal=True)
    
    modified_text = None
    if action == "Modify Response" and ctx:
        modified_text = st.text_area("Edit Draft Response", value=ctx.get("draft_response", ""), height=150)
        
    if st.button("Submit Decision", type="primary"):
        # Resume the paused LangGraph workflow by feeding human decision payload
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        
        decision_val = "approve" if action == "Approve Draft" else "modify"
        decision_payload = {
            "action": decision_val,
            "response": modified_text if decision_val == "modify" else None
        }
        
        try:
            # Resume graph execution with the human input using Command(resume=...)
            for event in graph.stream(Command(resume=decision_payload), config, stream_mode="updates"):
                for node_name, node_output in event.items():
                    if node_name not in st.session_state.workflow_steps:
                        st.session_state.workflow_steps.append(node_name)
            
            # Fetch final state to append response
            final_state = graph.get_state(config)
            final_msg = final_state.values["messages"][-1]
            if isinstance(final_msg, AIMessage):
                st.session_state.messages.append({"role": "assistant", "content": final_msg.content})
                
            st.session_state.pending_escalation = False
            st.session_state.escalation_context = None
            st.rerun()
        except Exception as e:
            st.error(f"Error resuming graph: {str(e)}")

# Display chat history
if not st.session_state.messages:
    st.markdown("""
    <div class="info-card" style="text-align: center; padding: 2rem;">
        <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">👋 Welcome to Support Resolution Workspace</p>
        <p style="color: #94a3b8;">Describe your issue below. The autonomous graph will verify CRM credentials, consult our knowledge base, classify urgency, and resolve your issue or escalate to a human.</p>
        <p style="font-size: 0.9rem; color: #a5b4fc; margin-top: 1rem;">
            💡 Try: <strong>"Can you check my double bill? CUST001"</strong> (will run diagnostics) or <strong>"URGENT: Server Down CUST001"</strong> (will trigger critical human escalation review!)
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="agent-message">{content}</div>', unsafe_allow_html=True)

# Chat Input
user_input = st.chat_input("Explain your support issue...")

if user_input:
    # Instantly render user message
    st.markdown(f'<div class="user-message">{user_input}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # LangGraph Thread Configuration
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    # Load input variables
    inputs = {
        "messages": [HumanMessage(content=user_input)],
        "customer_id": st.session_state.customer_id if st.session_state.customer_id else None
    }
    
    with st.spinner("Processing ticket..."):
        try:
            # Stream the events from graph
            for event in graph.stream(inputs, config, stream_mode="updates"):
                for node_name, node_output in event.items():
                    if node_name not in st.session_state.workflow_steps:
                        st.session_state.workflow_steps.append(node_name)
                    if node_name == "classify_urgency":
                        st.session_state.priority = node_output.get("priority", "medium")
                    if node_name == "check_context":
                        st.session_state.customer_id = node_output.get("customer_id", st.session_state.customer_id)
            
            # Check if graph execution paused at an interrupt node (human review)
            graph_state = graph.get_state(config)
            if graph_state.next and "human_escalation" in graph_state.next:
                st.session_state.pending_escalation = True
                # Retrieve the interrupt context
                if hasattr(graph_state, 'tasks') and graph_state.tasks:
                    for task in graph_state.tasks:
                        if hasattr(task, 'interrupts') and task.interrupts:
                            st.session_state.escalation_context = task.interrupts[0].value
                st.rerun()
            else:
                # Flow completed directly without human intervention needed
                final_msg = graph_state.values["messages"][-1]
                if isinstance(final_msg, AIMessage):
                    st.session_state.messages.append({"role": "assistant", "content": final_msg.content})
                    st.rerun()
        except Exception as e:
            st.error(f"Error executing agent workflow: {str(e)}")
