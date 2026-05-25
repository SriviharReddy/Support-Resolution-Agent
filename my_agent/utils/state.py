from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SupportState(TypedDict):
    """
    Structured state schema for the customer support agent.
    """
    # Conversation messages
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Customer and Urgency classification
    customer_id: Optional[str]
    priority: Optional[str]  # critical, high, medium, low
    
    # Context analysis
    context_complete: bool
    missing_context: List[str]
    
    # Diagnosis and resolution
    resolution_steps: List[str]
    draft_response: Optional[str]
    final_response: Optional[str]
    
    # Escalation
    requires_escalation: bool
    response_approved: Optional[bool]
