"""
Node functions for the Support Resolution Agent.
Implements urgency classification, context validation, tool diagnosis, and human escalation.
"""

import os
import json
from typing import Dict, Any, Literal
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.types import interrupt

from my_agent.utils.state import SupportState
from my_agent.utils.tools import lookup_customer, search_knowledge_base

# ============================================================================
# LLM Configuration
# ============================================================================

def get_llm():
    """
    Initialize the Amazon Bedrock LLM.
    """
    return ChatBedrockConverse(
        model=os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
        region_name=os.getenv("BEDROCK_REGION", "us-east-1"),
        temperature=0.3,
        max_tokens=2048,
    )


# ============================================================================
# Structured Node Functions
# ============================================================================

def classify_urgency_node(state: SupportState):
    """
    Node 1: Classifies issue urgency (critical, high, medium, low) using Bedrock.
    """
    print("---STEP 1: CLASSIFY URGENCY---")
    llm = get_llm()
    
    # Get the latest user message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    query = user_messages[-1].content if user_messages else "general inquiry"
    
    prompt = (
        "Classify the urgency of the following customer support request.\n"
        "Respond in exact JSON format: {\"priority\": \"critical|high|medium|low\"}\n\n"
        "Guidelines:\n"
        "- critical: System outages, billing issues, security concerns.\n"
        "- high: Key feature broken, very frustrated tone.\n"
        "- medium: Standard product questions.\n"
        "- low: Feature suggestions, feedback.\n\n"
        f"Request: {query}"
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        result = json.loads(content.strip())
        priority = result.get("priority", "medium")
    except Exception:
        priority = "medium"
        
    return {"priority": priority}


def check_context_node(state: SupportState):
    """
    Node 2: Validates if we have enough customer information to proceed.
    Fills in missing info or requests customer ID directly.
    """
    print("---STEP 2: CHECK & FILL CONTEXT---")
    messages = state["messages"]
    
    # Check if a customer_id was passed in initial state
    cust_id = state.get("customer_id")
    
    # If not in state, look through conversation history
    if not cust_id:
        for m in reversed(messages):
            if isinstance(m, HumanMessage) and "CUST" in m.content:
                # Extract simple mock customer ID (e.g. CUST001)
                import re
                match = re.search(r"CUST\d+", m.content)
                if match:
                    cust_id = match.group(0)
                    break

    if not cust_id:
        # Request customer ID from the user and pause graph
        ask_message = AIMessage(
            content="To better assist you, could you please provide your Customer ID (e.g., CUST001)?"
        )
        return {
            "messages": [ask_message],
            "context_complete": False,
            "missing_context": ["customer_id"]
        }
        
    return {
        "customer_id": cust_id,
        "context_complete": True,
        "missing_context": []
    }


def diagnose_and_resolve_node(state: SupportState):
    """
    Node 3: Selects resolution steps using tool-based searches (lookup CRM and KB).
    """
    print("---STEP 3: DIAGNOSE & SELECT RESOLUTION---")
    llm = get_llm()
    cust_id = state.get("customer_id")
    
    # Latest customer question
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    query = user_messages[-1].content if user_messages else ""
    
    # Execute tools
    crm_info = lookup_customer.invoke({"customer_id": cust_id})
    kb_info = search_knowledge_base.invoke({"query": query})
    
    resolution_steps = [
        f"Verified customer tier from CRM: {crm_info}",
        f"Consulted tech knowledge base: {kb_info}"
    ]
    
    # Generate draft response based on tools context
    prompt = (
        "Draft a warm, professional customer support response addressing the query "
        "using the verified CRM and KB details below.\n\n"
        f"Query: {query}\n"
        f"CRM: {crm_info}\n"
        f"KB Details: {kb_info}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Auto-escalation trigger: critical priority is automatically sent to human review
    requires_escalation = state.get("priority") == "critical"
    
    return {
        "resolution_steps": resolution_steps,
        "draft_response": response.content,
        "requires_escalation": requires_escalation
    }


def human_escalation_node(state: SupportState):
    """
    Node 4: Pauses workflow for human agent review using LangGraph interrupts.
    """
    print("---STEP 4: HUMAN ESCALATION INTERRUPT---")
    
    escalation_context = {
        "customer_id": state.get("customer_id"),
        "priority": state.get("priority"),
        "draft_response": state.get("draft_response"),
        "resolution_steps": state.get("resolution_steps")
    }
    
    # Pause graph execution and wait for human command input
    human_decision = interrupt(escalation_context)
    
    if isinstance(human_decision, dict):
        action = human_decision.get("action", "approve")
        if action == "approve":
            return {
                "final_response": state.get("draft_response"),
                "response_approved": True
            }
        elif action == "modify":
            return {
                "final_response": human_decision.get("response", state.get("draft_response")),
                "response_approved": True
            }
            
    # Default: Use human decision text directly
    return {
        "final_response": str(human_decision) if human_decision else state.get("draft_response"),
        "response_approved": True
    }


def deliver_response_node(state: SupportState):
    """
    Node 5: Finalizes response and appends it to conversation history.
    """
    print("---STEP 5: DELIVER RESPONSE---")
    response_text = state.get("final_response") or state.get("draft_response")
    ai_msg = AIMessage(content=response_text)
    
    return {
        "messages": [ai_msg]
    }
