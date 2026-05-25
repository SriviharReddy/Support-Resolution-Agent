"""
Graph definition and construction for the Support Resolution Agent workflow.
Implements structured conditional flows for urgency, context verification, and escalation.
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from my_agent.utils.state import SupportState
from my_agent.utils.nodes import (
    classify_urgency_node,
    check_context_node,
    diagnose_and_resolve_node,
    human_escalation_node,
    deliver_response_node
)

# ============================================================================
# Routing Functions for Conditional Edges
# ============================================================================

def route_after_context(state: SupportState) -> Literal["diagnose_and_resolve", "__end__"]:
    """
    Route based on whether customer context is complete.
    """
    if not state.get("context_complete", True):
        # Await customer ID submission
        return "__end__"
    return "diagnose_and_resolve"


def route_after_diagnosis(state: SupportState) -> Literal["human_escalation", "deliver_response"]:
    """
    Route based on whether the ticket requires human agent escalation review.
    """
    if state.get("requires_escalation", False):
        return "human_escalation"
    return "deliver_response"


# ============================================================================
# Graph Construction
# ============================================================================

# Initialize state graph
workflow = StateGraph(SupportState)

# Add custom reasoning and action nodes
workflow.add_node("classify_urgency", classify_urgency_node)
workflow.add_node("check_context", check_context_node)
workflow.add_node("diagnose_and_resolve", diagnose_and_resolve_node)
workflow.add_node("human_escalation", human_escalation_node)
workflow.add_node("deliver_response", deliver_response_node)

# Define edges
workflow.add_edge(START, "classify_urgency")
workflow.add_edge("classify_urgency", "check_context")

# Conditional: Ask for customer ID OR proceed to diagnostic tools
workflow.add_conditional_edges(
    "check_context",
    route_after_context,
    {
        "diagnose_and_resolve": "diagnose_and_resolve",
        "__end__": END
    }
)

# Conditional: Route to human agent review OR deliver direct response
workflow.add_conditional_edges(
    "diagnose_and_resolve",
    route_after_diagnosis,
    {
        "human_escalation": "human_escalation",
        "deliver_response": "deliver_response"
    }
)

# Transition nodes
workflow.add_edge("human_escalation", "deliver_response")
workflow.add_edge("deliver_response", END)

# Compile graph with memory saver checkpointing
checkpointer = MemorySaver()
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_escalation"]  # Pause before human agent review
)
