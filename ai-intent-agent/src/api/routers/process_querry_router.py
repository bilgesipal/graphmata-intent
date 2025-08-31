import os
import uuid

from fastapi import HTTPException, Response, APIRouter, Depends
from src.agent.intent_agent import IntentAgent
from src.api.dependency.bizigo_headers import bizigo_headers
from src.api.schemas.schemas import QueryRequest
from src.util.utilities import cache_bizigo_headers, get_cached_headers
router = APIRouter(tags=["Process Query"])

@router.post("/process_query",
             summary="BizigoBFF Querry Processing for Entities and Intent"
             )
async def process_query(
        payload: QueryRequest,
        response: Response,
        bzg_headers:dict= Depends(bizigo_headers)
                        ):
    """
    Trigger intent processing with user input. Results will be published
    to Redis PubSub, not returned in the response.
    """
    request_id = str(uuid.uuid4())
    response.headers["X-Request-ID"] = request_id
    print(payload)

    application_id = bzg_headers["ApplicationId"]
    user_id = bzg_headers["UserId"]
    language_code = bzg_headers["LanguageCode"]
    print('cache sending')
    cache_bizigo_headers(headers=bzg_headers)

    user_input = payload.user_input
    session_id = payload.session_id
    message_id = payload.message_id
    sequence = payload.sequence
    trace_id = payload.trace_id

    print(f"Received intent trigger - Request ID: {request_id}")
    print(f"User ID: {user_id}, Query: {user_input}")
    print('GERI AL', get_cached_headers(user_id=user_id,
                             application_id=application_id,
                                        session_id=session_id))

    if not user_input:
        print("Missing user_input in request")
        raise HTTPException(status_code=400, detail="user_input is required")
    if user_id:
        os.environ["USER_ID"] = user_id

    try:

        intent_agent = IntentAgent()
        print('input', user_input)
        result = intent_agent.process_query(
            user_input=user_input,
            user_id=user_id,
            application_id=application_id,
            language=language_code,
            session_id=session_id,
            message_id=message_id,
            sequence=sequence,
            trace_id=trace_id
        )



        print(f"Intent processing triggered successfully - Request ID: {request_id}, {result}")
    except Exception as e:
        print(f"Error in background processing: {str(e)}")

    return {
        "message": "Intent processing triggered",
        "request_id": request_id
    }




