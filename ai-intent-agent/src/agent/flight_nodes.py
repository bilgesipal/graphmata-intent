from typing import Dict, Any
import json
from langchain_core.output_parsers import JsonOutputParser


from src.agent.hotel_nodes import HotelNodes
from src.api.schemas.schemas import AgentState
from src.agent.shared_nodes import SharedNodes
from src.util.utilities import get_redis_client
from src.prompt_library.flight_prompt import get_flight_intent_prompt


class FlightNodes:

    @staticmethod
    def classify_flight_intent(state: AgentState) -> AgentState:
        """Classifies the user's intent based on the provided input and context."""
        try:
            llm = SharedNodes.get_llm()
            supported_intents = [
                "flight_search_simple_oneway",
                "flight_search_roundtrip",
                "flight_search_multi_city_oneway",
                "flight_detail_ask",
                "flight_compare",
                "greetings",
                "out_of_scope",
                "rejection"
            ]

            session_id = state.get("session_id", "default_session")
            user_id = state.get("user_id", "unknown_user")
            key = f"prometa_ai:conversation:{session_id}_{user_id}"
            print(f"Retrieving conversation context for session ID: {key}")

            previous_intent = ""
            filled_slots = {}
            context = ""
            redis_client = get_redis_client()
            try:
                context_data = redis_client.get(key)

                if context_data:
                    conversation_context = json.loads(context_data)
                    context = conversation_context.get("chat_history", "")
                    print(f"Conversation context: {conversation_context['chat_history']}")
                    filled_slots = conversation_context.get("latest_entity", {})

                    print(f"filled_slots: {filled_slots}")
                    previous_intent = filled_slots.get("intent")
                    print(f"previous_intent: {previous_intent}")

            except Exception as e:
                print(f"ERROR retrieving conversation context: {e}")

            if not context:
                context = "first time user no previous input"
                print("No previous conversation context found, using default context.")


            user_input = state.get("user_input", "")
            language = state.get("language", "tr")
            print(f" DEBUG - PROMPT INPUTS:")
            print(f"  user_input: '{user_input}'")
            print(f"  language: '{language}'")
            print(f"  context: '{context}'")
            print(f"  previous_intent: '{previous_intent}'")
            print(f"  filled_slots: {filled_slots}")

            intent_prompt = get_flight_intent_prompt()
            json_parser = JsonOutputParser()
            chain = intent_prompt | llm | json_parser

            prompt_inputs = {
                "user_input": user_input,
                "language": language,
                "context": context,
                "previous_intent": previous_intent,
                "filled_slots": filled_slots,
            }
            print(f"DEBUG - SENDING TO LLM: {prompt_inputs}")

            result = chain.invoke(prompt_inputs)

            print(f" DEBUG - RAW LLM RESULT:")
            print(f"  Type: {type(result)}")
            print(f"  Content: {result}")
            print(f"  Keys (if dict): {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

            intent_value = result.get("intent", "") if isinstance(result, dict) else ""
            confidence_value = result.get("confidence", 0.7) if isinstance(result, dict) else 0.7
            entities_value = result.get("entities", {}) if isinstance(result, dict) else {}

            print(f" DEBUG - EXTRACTED VALUES:")
            print(f"  intent: '{intent_value}' (type: {type(intent_value)})")
            print(f"  confidence: {confidence_value} (type: {type(confidence_value)})")
            print(f"  entities: {entities_value} (type: {type(entities_value)})")

            if intent_value not in supported_intents:
                print(f" WARNING: Intent '{intent_value}' not in supported intents: {supported_intents}")

            if isinstance(entities_value, dict):
                print(f" DEBUG - ENTITIES BREAKDOWN:")
                for key, value in entities_value.items():
                    print(f"  {key}: {value} (type: {type(value)})")

                dest_to = entities_value.get("destinationTo", [])
                dest_from = entities_value.get("destinationFrom", [])
                print(f" DEBUG - DESTINATIONS:")
                print(
                    f"  destinationTo: {dest_to} (length: {len(dest_to) if isinstance(dest_to, list) else 'not a list'})")
                print(
                    f"  destinationFrom: {dest_from} (length: {len(dest_from) if isinstance(dest_from, list) else 'not a list'})")

            state["intent"] = intent_value
            state["confidence"] = confidence_value
            print(f" DEBUG - STATE BEFORE ENTITY MERGE:")
            print(f"  existing entities: {state.get('entities', {})}")

            new_entities = entities_value
            state["entities"] = {**state.get("entities", {}), **new_entities}

            print(f"DEBUG - STATE AFTER ENTITY MERGE:")
            print(f"  merged entities: {state.get('entities', {})}")

            if state["intent"] == "rejection":
                state["entities"] = {k: "" for k, v in state["entities"].items()}
                print(f"Entities after rejection: {state['entities']}")

            # FINAL DEBUG: Check complete state
            print(f" DEBUG - FINAL STATE:")
            print(f"  intent: {state.get('intent')}")
            print(f"  confidence: {state.get('confidence')}")
            print(f"  entities keys: {list(state.get('entities', {}).keys())}")

        except Exception as e:
            print(f"Intent classification failed: {e}")
            import traceback
            traceback.print_exc()

        print(' FINAL STATE:', state)
        return state