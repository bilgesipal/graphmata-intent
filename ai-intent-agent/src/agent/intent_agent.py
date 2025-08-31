import json
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END



from src.agent.flight_nodes import FlightNodes
from src.agent.hotel_nodes import HotelNodes
from src.api.schemas.schemas import AgentState

from src.agent.shared_nodes import SharedNodes
from src.util.utilities import get_redis_client



class IntentAgent:

    def __init__(self, enable_studio: bool = False):
        self.agent = "intent_agent"
        self.redis_client = get_redis_client()
        self.enable_studio = enable_studio
        self.graph = self._build_graph()

    def _build_graph(self):
        """Create the LangGraph agent with conditional routing"""
        g = StateGraph(AgentState)

        g.add_node("initialize", self.initialize_state)
        g.add_node("check_intent_and_branch", self.route_intent)
        g.add_node("classify_intent", lambda state: SharedNodes.classify_intent(state))
        g.add_node("classify_flight_intent", FlightNodes.classify_flight_intent)
        g.add_node("classify_hotel_intent", HotelNodes.classify_hotel_intent)
        g.add_node("update_context", HotelNodes.update_context)
        g.add_node("generate_payload", SharedNodes.generate_response_payload)
        g.add_node("publish", SharedNodes.publish_to_redis)

        def route_condition(state: AgentState):
            print(' ROUTING: Current state:', state)
            flow_type = state.get("flow_type", "").upper()
            user_input = state.get("user_input", "").lower()

            print(f"ROUTING: user_input = '{user_input}'")

            if flow_type == "FLIGHT":
                print(" ROUTING TO: classify_flight_intent (from flow_type)")
                return "classify_flight_intent"
            else:
                print(" ROUTING TO: classify_hotel_intent")
                return "classify_hotel_intent"


        g.add_edge(START, "initialize")
        g.add_edge("initialize", "classify_intent")
        g.add_edge("classify_intent", "check_intent_and_branch")

        g.add_conditional_edges(
            "check_intent_and_branch",
            route_condition
        )

        g.add_edge("classify_flight_intent", "generate_payload")
        g.add_edge("classify_hotel_intent", "update_context")
        g.add_edge("update_context", "generate_payload")
        g.add_edge("generate_payload", "publish")
        g.add_edge("publish", END)



        return g.compile()

    def route_intent(self, state: AgentState) -> AgentState:
        """Determine the next node based on the flow type"""
        if state["flow_type"] == "FLIGHT":
            state["route"] = "classify_flight_intent"
        else:
            state["route"] = "classify_hotel_intent"
        print(f"ROUTER: Routing intent with state: {state}")
        return state

    def initialize_state(self, state: AgentState) -> AgentState:
        """Initialize the agent state with default values"""
        state.update({
            "intent": None,
            "entities": {},
            "confidence": 0.0,
            "response_payload": None,
            "error": None
        })
        return state

    def handle_message(self, json_str: str) -> Dict[str, Any]:
        """Alternative entry point to process a message from JSON string"""
        try:
            input_dict = json.loads(json_str)
            user_input = input_dict.get("user_input", "")
            user_id = input_dict.get("user_id", "unknown_user")
            session_id = input_dict.get("session_id", "default_session")
            message_id = input_dict.get("message_id", "")
            sequence = input_dict.get("sequence", 0)
            trace_id = input_dict.get("trace_id", 0)
            language = input_dict.get("language", "tr")
            application_id = input_dict.get("application_id", "default_app")

            return self.process_query(
                user_input=user_input,
                user_id=user_id,
                session_id=session_id,
                message_id=message_id,
                sequence=sequence,
                trace_id=trace_id,
                language=language,
                application_id=application_id
            )

        except Exception as e:
            print(f"Error in handle_message: {e}")
            return {
                "error": str(e),
                "input": json_str[:100] + "..." if len(json_str) > 100 else json_str
            }


    def process_query(self, user_input: str,
                            user_id: str,
                            session_id: str,
                            message_id: str,
                            sequence: int = 0,
                            trace_id: int = 0,
                            language: str = "tr",
                            application_id: str = "default_app",
                            ) -> Dict[str, Any]:

        try:

            initial_state: AgentState = {
                "user_input": user_input,
                "language": language,
                "application_id": application_id,
                "user_id": user_id,
                "session_id": session_id,
                "intent": None,
                "entities": {},
                "message_id": message_id,
                "sequence": sequence,
                "trace_id": trace_id,
                "confidence": 0.0,
                "hotel_context": {},
                "response_payload": None,
                "error": None,
                "flow_type": None
            }
            print(f"Initial state: {initial_state}")


            if self.enable_studio:
                # @Taskin For LangGraph Studio, use thread_id for session management
                config = {"configurable": {"thread_id": session_id}} if self.enable_studio else None
                result = self.graph.invoke(initial_state, config=config)
            else:
                result = self.graph.invoke(initial_state)

            print(f"Result: {result}")
            return result["response_payload"] if result["response_payload"] else {"error": result.get("error")}
        except Exception as e:
            print(f"Error processing  query: {e}")
            return {"error": str(e)}

    def get_graph_for_studio(self):
        """Return the compiled graph for LangGraph Studio"""
        return self.graph



