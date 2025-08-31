
import json
import os
from typing import Dict, Any

from langchain_core.output_parsers import JsonOutputParser
from src.api.schemas.schemas import AgentState
from src.util.utilities import get_redis_client
from src.prompt_library.hotel_prompt import get_hotel_prompt
from src.agent.shared_nodes import SharedNodes




class HotelNodes:
    """Class for handling hotel-related operations in the agent."""



    @staticmethod
    def update_context(state: AgentState) -> AgentState:

        if "flight" in state.get("intent"):
            return state
        try:
            if state["entities"]:
                redis_client = get_redis_client()
                user_id = os.getenv("USER_ID", "user123")
                context_key = f"context:{user_id}"
                session_id = state.get("session_id", "default_session")
                conversation_key = f"prometa_ai:conversation:{session_id}_{user_id}"
                print(f"Converation key: {conversation_key}")
                existing_conversation = {}
                conversation_data = redis_client.get(conversation_key)

                if conversation_data:
                    existing_conversation = json.loads(conversation_data)

                previous_entities = {}

                if "chat_data" in existing_conversation and "filled_slots" in existing_conversation["chat_data"]:
                    previous_entities = existing_conversation["chat_data"]["filled_slots"]

                existing_hotel_context = state.get("hotel_context", {})

                new_entities = {k: v for k, v in state["entities"].items() if v}
                if "location" not in new_entities and "location" in previous_entities and previous_entities["location"]:
                    new_entities["location"] = previous_entities["location"]

                updated = {**existing_hotel_context, **previous_entities, **new_entities}
                redis_client.set(context_key, json.dumps(updated), ex=86400)
                state["hotel_context"] = updated
                if "chat_data" not in existing_conversation:
                    existing_conversation["chat_data"] = {}
                existing_conversation["chat_data"]["filled_slots"] = updated
                redis_client.set(conversation_key, json.dumps(existing_conversation), ex=86400)
                redis_cache_adress = []
                redis_cache_adress_pp = []

                hotels, price_pol = HotelNodes.get_hotels()
                if  state["intent"] in ["hotel_ask", "hotel_comparison", "hotel_list_followup", "hotel_ask_followup", "hotel_comparison_followup"]:
                    hotel_names = [state["entities"].get("hotelNameQuery", [])[i] for i in range(len(state["entities"].get("hotelNameQuery", [])))]  if state["entities"].get(
                        "hotelNameQuery") else ""
                    print('hotel_name:', hotel_names)

                    for hotel_name in hotel_names:
                        if hotel_name in hotels:
                            redis_cache_adress.append("prometa:HotelSearch:" + hotel_name)
                            print("Redis cache address for general info:", redis_cache_adress)
                            print(f"prometa:HotelSearch:Price:{user_id}:{session_id}:" + hotel_name)
                            print("Price policy found in redis", price_pol)
                            if f"Price:{user_id}:{session_id}:" + hotel_name in price_pol:
                                redis_cache_adress_pp.append(f"prometa:HotelSearch:Price:{user_id}:{session_id}:" + hotel_name)
                                print("Redis cache address for price policy:", redis_cache_adress_pp)

                state["redis_cache_address_general_info"] = redis_cache_adress
                state["redis_cache_address_price_policy"] = redis_cache_adress_pp

                print(f"Updated context with merged entities: {updated}")
        except Exception as e:
            print(f"Failed to update context: {e}")
            state["error"] = str(e)
        print("STAE", state)
        return state

    @staticmethod
    def get_hotels():
        r= get_redis_client()
        keys = r.keys("prometa:HotelSearch:*")
        hotel_names = [key.replace("prometa:HotelSearch:", "") for key in keys]
        price_pol = [name for name in hotel_names if name.startswith("Price")]
        hotel = [name for name in hotel_names if not name.startswith("Price")]
        return hotel, price_pol


    @staticmethod
    def get_hotel_feat(hotel_name: str):
        print("DEBUG: Retrieving hotel features for:", hotel_name)
        r = get_redis_client()
        keys = r.keys("prometa:HotelSearch:*")
        hotel_names = [key.replace("prometa:HotelSearch:", "") for key in keys]
        matching_hotels = [name for name in hotel_names if name == hotel_name]
        print(f"DEBUG: Matching hotels for {hotel_name}: {matching_hotels}")
        if not matching_hotels:
            print(f"DEBUG: No matching hotels found for {hotel_name}")
            return {
                "name": hotel_name,
                "latitude": None,
                "longitude": None,
                "review_rate": None,
                "hotel_star": None,
                "price": "N/A",
                "features": [],
                "location_description": "",
                "error": f"Hotel '{hotel_name}' not found."
            }

        else:
            hotel_key = f"prometa:HotelSearch:{matching_hotels[0]}"

            hotel_data = r.get(hotel_key)
            print(f"DEBUG: Hotel data retrieved from Redis for {hotel_name}: {hotel_data}")
            hotel_data = json.loads(hotel_data)
            extracted_info = {
                "latitude": hotel_data["latitude"],
                "longitude": hotel_data["longitude"],
                "review_rate": hotel_data["review_rate"],
                "hotel_star": hotel_data["star"]
            }

            return extracted_info

    @staticmethod
    def classify_hotel_intent(state: AgentState) -> AgentState:
            """Classifies the user's intent based on the provided input and context."""
            try:
                llm = SharedNodes.get_llm()
                supported_intents = [
                    "hotel_detail",
                    "hotel_list",
                    "hotel_ask",
                    "hotel_comparison",
                    "hotel_list_followup",
                    "hotel_detail_followup",
                    "hotel_ask_followup",
                    "hotel_comparison_followup",
                    "hotel_similar",
                    "hotel_room_comparison",
                    "rejection",
                    "greetings",
                    "out_of_scope"
                ]

                feature_query = ["kablosuz internet", "otopark", "24 saat açık resepsiyon", "restoran", "havuz", "spa",
                                 "spor salonu", "toplantı odası", "sigara içilmeyen odalar", "asansör",
                                 "evcil hayvan dostu"]

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

                hotels, price_pol = HotelNodes.get_hotels()
                print("hotels:", hotels)

                intent_prompt = get_hotel_prompt()
                json_parser = JsonOutputParser()
                chain = intent_prompt | llm | json_parser

                result = chain.invoke({
                    "user_input": state.get("user_input", ""),
                    "language": state.get("language", "tr"),
                    "context": context,
                    "previous_intent": previous_intent,
                    "filled_slots": filled_slots,
                    "hotels": hotels
                })
                print(f"Intent classification result: {result}")
                state["intent"] = result.get("intent", "")
                state["confidence"] = result.get("confidence", 0.7)

                new_entities = result.get("entities", {})
                state["entities"] = {**state.get("entities", {}), **new_entities}

                if state["intent"] == "hotel_similar":
                    hotel = state["entities"].get("hotelNameQuery", "")
                    hotel_name = hotel[0]
                    print("DEBUG: Hotel similar intent detected with hotel name:", hotel)
                    print("DEBUG: hotels:", hotels)
                    print("DEBUG: ", hotel_name in hotels)
                    if hotel_name in hotels:
                        print(f"DEBUG: Fetching hotel features for {hotel}...")
                        hotel_info = HotelNodes.get_hotel_feat(hotel_name)
                        print(f"Hotel info for {hotel}: {hotel_info}")
                        state["entities"]["hotelStarQuery"] = hotel_info.get("star_rating", "")
                        state["entities"]["reviewRate"] = hotel_info.get("review_rate", "")
                        state["entities"]["latitude"] = hotel_info.get("latitude", "")
                        state["entities"]["longitude"] = hotel_info.get("longitude", "")

                if state["intent"] == "rejection":
                    state["entities"] = {k: "" for k, v in state["entities"].items()}
                    print(f"Entities after rejection: {state['entities']}")

                feat = state['entities'].get('featureQuery', [])
                if feat and isinstance(feat, list):
                    featureQuery = [f for f in feat if f in feature_query]
                    state['entities']['featureQuery'] = featureQuery


            except Exception as e:
                print(f"Intent classification failed: {e}")
                import traceback
                traceback.print_exc()
            print('STATE:', state)
            return state

