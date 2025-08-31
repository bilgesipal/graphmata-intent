import os
import json
import datetime
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from src.api.schemas.schemas import AgentState
from src.util.utilities import get_redis_client
from src.config.config import AppConfig
from src.prompt_library.general_prompt import classify_prompt


class SharedNodes:

    @staticmethod
    def get_context(state: AgentState) -> AgentState:
        try:
            redis_client = get_redis_client()
            user_id = os.getenv("USER_ID", "user123")
            context = redis_client.get(f"hotel_context:{user_id}")
            state["hotel_context"] = json.loads(context) if context else {}
        except Exception as e:
            print(f"Failed to get context: {e}")
            state["hotel_context"] = {}
            state["error"] = str(e)
        return state

    @staticmethod
    def get_llm(model_name: str = "gpt-4-turbo", temperature: float = 0.1):
        api_key = AppConfig.open_ai_key
        if not api_key:
            raise ValueError("Missing OpenAI API key in AppConfig")

        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature
        )


    @staticmethod
    def classify_intent(state: AgentState) -> AgentState:
        """First classification to determine flow type (HOTEL/FLIGHT/CAR)"""
        try:
            llm = SharedNodes.get_llm()
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

            intent_prompt = classify_prompt()
            chain = intent_prompt | llm

            result = chain.invoke({
                "user_input": state.get("user_input", ""),
                "language": state.get("language", "tr"),
                "context": context,
                "previous_intent": previous_intent,
                "filled_slots": filled_slots,
            })
            print(f"Flow classification result: {result}")

            if hasattr(result, 'content'):
                flow_type = result.content.strip().upper()
            else:
                flow_type = str(result).strip().upper()

            print(f"Extracted flow_type: '{flow_type}'")

            if flow_type in ["HOTEL", "FLIGHT"]:
                state["flow_type"] = flow_type
                print(f"CLASSIFY DEBUG: Valid flow_type set: {state['flow_type']}")
            print(f"CLASSIFY DEBUG: Final flow type determined: {state['flow_type']}")
            return state

        except Exception as e:
            print(f"Flow classification failed: {e}")
            return state

    @staticmethod
    def generate_response_payload(state: AgentState) -> AgentState:
            """Generates the response payload based on the classified intent and context."""
            print("Generating response payload...", state)
            try:
                state["response_payload"] = {
                    "session_id": state["session_id"],
                    "message_id": state["message_id"],
                    "timestamp": datetime.datetime.now().isoformat(timespec='milliseconds'),
                    "version": "1.0.3",
                    "trace_info": {
                        "trace_id": 0 if state["trace_id"] is None else state["trace_id"],
                        "flow": state["intent"],
                        "sequence": state["sequence"] + 1,
                        "retry_count": 0
                    },
                    "metadata": {
                        "user_id": state["user_id"],
                        "application_id": state["application_id"],
                        "language": state["language"],
                        "source_service": "intent-agent",
                        "event_type": "state_update",
                        "customerid_ui": [],
                        "travelUsageType": "corporate",
                        "redis_cache_address_general_info": state.get("redis_cache_address_general_info", []),
                        "redis_cache_address_price_policy": state.get("redis_cache_address_price_policy", [])
                    },
                    "state": {
                        "current": {
                            "user_input": {
                                "text": state["user_input"],
                                "language": state["language"]
                            },
                            "intent_phase": {
                                "status": "classified",
                                "intent": state["intent"],
                                "confidence": state["confidence"],
                                "entities": state.get("entities", {})
                            }
                        },
                        "previous_transition": "system_message_created",
                        "transition": "intent_classified"
                    }
                }
                print('output', json.dumps(state, default=str))
            except Exception as e:
                print(f"Failed to generate payload: {e}")
                state["error"] = str(e)
            return state

    @staticmethod
    def publish_to_redis(state: AgentState) -> AgentState:
            """Publish the response payload to Redis channel"""
            print("DEBUG:Publishing response payload to Redis...", state)
            try:
                payload = state["response_payload"]
                if not payload:
                    raise ValueError("No response payload")

                channel = AppConfig.REDIS_PUBLISH
                json_payload = json.dumps(payload, default=str, ensure_ascii=False)
                redis_client = get_redis_client()
                redis_client.publish(channel, json_payload)
                print(f"Successfully published to Redis channel: {channel}")
            except Exception as e:
                error_msg = f"Redis publish error: {str(e)}"
                print(error_msg)
                state["error"] = error_msg

            return state



