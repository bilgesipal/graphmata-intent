import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent.intent_agent import IntentAgent



# LangGraph Studio
def create_intent_agent_for_studio():
    """Factory function to create IntentAgent for LangGraph Studio"""
    return IntentAgent(enable_studio=True)

# For LangGraph Studio - this is the entry point
def get_graph():
    """Entry point for LangGraph Studio"""
    agent = create_intent_agent_for_studio()
    return agent.get_graph_for_studio()



# Export the graph at module level for LangGraph Studio
print("Creating graph for LangGraph Studio...")
graph = get_graph()
print("Graph created successfully!")
print("✅ Graph created successfully for LangGraph Studio (with LangSmith tracing)")