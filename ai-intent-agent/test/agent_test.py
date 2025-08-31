#!/usr/bin/env python3
"""
Demo script for testing IntentAgent
"""

from src.agent.intent_agent import get_graph
import uuid


def test_intent_agent():
    """Test the intent agent with sample inputs"""

    graph = get_graph()


    test_cases = [
        {
            "user_input": "Ankaraya uçmak istiyorum",
            "language": "tr",
            "description": "Turkish flight request to Ankara"
        },
        {
            "user_input": "Istanbul'dan Paris'e gidiş dönüş bilet",
            "language": "tr",
            "description": "Round trip flight Istanbul to Paris"
        },
        {
            "user_input": "Hilton oteli rezervasyon yapmak istiyorum",
            "language": "tr",
            "description": "Hotel reservation request"
        }
    ]

    for i, test_case in enumerate(test_cases):
        print(f"\n{'=' * 60}")
        print(f"TEST {i + 1}: {test_case['description']}")
        print(f"Input: '{test_case['user_input']}'")
        print(f"{'=' * 60}")

        initial_state = {
            "user_input": test_case["user_input"],
            "language": test_case["language"],
            "application_id": "test_app",
            "user_id": "test_user",
            "session_id": f"test_session_{i}",
            "intent": None,
            "entities": {},
            "message_id": str(uuid.uuid4()),
            "sequence": 0,
            "trace_id": i,
            "confidence": 0.0,
            "hotel_context": {},
            "response_payload": None,
            "error": None,
            "flow_type": None
        }

        try:
            config = {"configurable": {"thread_id": f"test_thread_{i}"}}
            result = graph.invoke(initial_state, config=config)

            print(f"SUCCESS")
            print(f"Intent: {result.get('intent')}")
            print(f"Confidence: {result.get('confidence')}")
            print(f"Entities: {result.get('entities')}")
            print(f"Flow Type: {result.get('flow_type')}")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("Testing IntentAgent for LangGraph Studio")
    test_intent_agent()
    print("\n Testing complete!")

