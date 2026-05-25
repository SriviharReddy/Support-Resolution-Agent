"""
Tools for the Support Resolution Agent.
"""

from typing import Dict, Any
from langchain_core.tools import tool

@tool("lookup_customer")
def lookup_customer(customer_id: str) -> str:
    """
    Look up customer details from the database by customer ID.
    Always use this tool if you need to know about the customer's account status, tier, or name.
    """
    customers_db = {
        "CUST001": "Alice Johnson (Tier: Premium, Email: alice.j@example.com, Status: Active)",
        "CUST002": "Bob Smith (Tier: Enterprise, Email: bob.s@company.com, Status: Active)",
        "CUST003": "Carol Davis (Tier: Standard, Email: carol.d@email.com, Status: Active)"
    }
    
    return customers_db.get(customer_id, f"Customer ID {customer_id} not found in database.")


@tool("search_knowledge_base")
def search_knowledge_base(query: str) -> str:
    """
    Search the customer support knowledge base for relevant resolution articles.
    Use this tool to find step-by-step guides for user technical issues.
    """
    kb = {
        "password": "How to Reset Password: 1. Go to login page, 2. Click 'Forgot Password', 3. Enter email, 4. Check inbox for reset link, 5. Choose a strong new password.",
        "billing": "Billing and Payment Cycle: Invoices are generated monthly. We support Credit/Debit cards, PayPal, and Bank Transfers. Payments process immediately.",
        "refund": "Refund Policy: Refund requests are accepted within 30 days of purchase. Refunds are processed back to the original payment method in 5-7 business days.",
        "connection": "Troubleshooting Connection Issues: 1. Clear browser cache and cookies, 2. Turn off active VPNs, 3. Try using an Incognito window or alternate browser."
    }
    
    # Quick simple keyword match
    query_lower = query.lower()
    matches = []
    for keyword, info in kb.items():
        if keyword in query_lower:
            matches.append(info)
            
    if matches:
        return "\n\n".join(matches)
    return "No exact matches found in the knowledge base. Please suggest basic troubleshooting or explain that you will seek human agent assistance."
