from typing import Dict, Any, Optional, List, TypedDict, NotRequired
from pydantic import BaseModel


class QueryRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    trace_id: Optional[int] = None
    sequence: Optional[int] = None

class AgentState(TypedDict):
    user_input: str
    language: str
    user_id: None
    application_id: Optional[str]
    session_id: str
    trace_id: int
    intent: Optional[str]
    entities: Dict[str, Any]
    message_id: str
    flow_type: str
    sequence: int
    confidence: float
    hotel_context: Dict[str, Any]
    response_payload: Optional[Dict[str, Any]]
    redis_cache_address_general_info: NotRequired[List[str]]
    redis_cache_address_price_policy: NotRequired[List[str]]
    error: Optional[str]

class MessageResponse(TypedDict):
    text: str
    entities: Dict[str, Any]
    context: Dict[str, Any]
    raw_response: NotRequired[Dict[str, Any]]
