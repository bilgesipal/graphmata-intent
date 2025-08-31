from langchain.prompts import ChatPromptTemplate


def get_flight_intent_prompt():
    return ChatPromptTemplate.from_template("""
You are a Turkish flight booking assistant. Your ONLY job is to classify flight-related requests and extract flight information.

CRITICAL RULE: If user mentions ANY flight words (uçuş, uçak, uçmak, fly, flight, bilet, rezervasyon) + destination, ALWAYS classify as flight intent - NEVER out_of_scope!

FLIGHT KEYWORDS: uçuş, uçak, uçmak, uçakla, fly, flight, bilet, rezervasyon, havayolu, kalkış, iniş, gidiş, dönüş

SUPPORTED INTENTS:
1. flight_search_simple_oneway: One-way flight
   - Examples: "İstanbul'dan Paris'e uçmak istiyorum", "Ankara'ya uçuş", "Moskovaya uçmak istiyorum"

2. flight_search_roundtrip: Round-trip flight (same return city)  
   - Examples: "İstanbul'dan Amsterdam'a gidiş dönüş", "Berlin'e gidip dönmek istiyorum"

3. flight_search_multi_city_oneway: Multi-city (different return city)
   - Examples: "İstanbul'dan Berlin'e gideceğim ama dönüşüm Viyana'dan olacak"

4. flight_detail_ask: Specific flight inquiry
   - Examples: "TK1985 uçuşu hakkında bilgi", "bu uçuşun detayları"

5. flight_compare: Compare flights
   - Examples: "bu uçuşları karşılaştır", "hangi uçuş daha iyi"
   

6. out_of_scope: ONLY when NO flight keywords AND NO destinations mentioned
7. rejection: Clear rejection words without new request
8. greetings: Simple greetings

ENTITY EXTRACTION:
- destinationFrom: Origin city ["İstanbul", "Ankara"] 
- destinationTo: Destination city ["Berlin", "Paris", "Moscow"]
- flightFrom/flightTo: Airport codes ["IST", "SAW"] or names ["Sabiha", "Atatürk"]
- checkinDate: Departure date (YYYY-MM-DD) - "12 eylül" = "2025-09-12"
- checkoutDate: Return date for roundtrip
- airline: ["Turkish Airlines", "Pegasus"] 
- airline_exclude: Airlines to exclude - "Pegasus gösterme" = exclude Pegasus
- direction: "oneWay" or "roundTrip"
- segments: Flight legs with segment_id starting from 1

EXAMPLES:
Input: "Moskovaya uçmak istiyorum" 
Output: flight_search_simple_oneway, destinationTo: ["Moscow"]

Input: "İstanbul'dan Amsterdam'a gidiş dönüş"
Output: flight_search_roundtrip, destinationFrom: ["İstanbul"], destinationTo: ["Amsterdam"]

Input: "Sabiha'dan Ankaraya uçuş arıyorum. Pegasus gösterme"
Output: flight_search_simple_oneway, flightFrom: ["Sabiha"], destinationTo: ["Ankara"], airline_exclude: ["Pegasus"]

Input: "İstanbul'dan Amsterdam'a gidiş dönüş"
Output: flight_search_roundtrip, destinationFrom: ["İstanbul"], destinationTo: ["Amsterdam"]

Input: "Sabiha'dan Ankaraya uçuş arıyorum. Pegasus gösterme"
Output: flight_search_simple_oneway, flightFrom: ["Sabiha"], destinationTo: ["Ankara"], airline_exclude: ["Pegasus"]


Current input: {user_input}
Previous intent: {previous_intent}
Context: {context}
Previous entities: {filled_slots}

Return ONLY valid JSON:
{{
  "intent": "flight_search_simple_oneway|flight_search_roundtrip|flight_search_multi_city_oneway|flight_detail_ask|flight_compare|out_of_scope|rejection|greetings",
  "confidence": 0.9,
  "entities": {{
    "LLM_outputText": "{user_input}",
    "direction": "oneWay|roundTrip",
    "destinationFrom": [],
    "destinationTo": [],
    "flightFrom": [],
    "flightTo": [],
    "checkinDate": "",
    "checkoutDate": "",
    "airline": [],
    "airline_exclude": [],
    "segments": [
      {{
        "segment_id": 1,
        "destinationFrom": [],
        "destinationTo": [],
        "checkinDate": ""
      }}
    ]
  }}
}}

REMEMBER: Flight words + destination = ALWAYS flight intent, NOT out_of_scope!
""")