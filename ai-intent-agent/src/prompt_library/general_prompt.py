from langchain_core.prompts import ChatPromptTemplate

def classify_prompt():
    return ChatPromptTemplate.from_template("""
You are a travel intent classifier. Classify the following Turkish input as either FLIGHT or HOTEL.

CRITICAL: If you see ANY flight-related words, respond with FLIGHT!

FLIGHT keywords: uçuş, uçak, uçmak, uçacağım, havayolu, bilet, kalkış, gitmek, seyahat, fly, flight, uçuş rezervasyon, uçuş bilgisi, uçuş arama, uçuş detayları, uçakla gitmek, uçakla seyahat

HOTEL keywords: otel, konaklama, oda, rezervasyon, etrafında, çevresinde, otel arama, otel rezervasyon, otel bilgisi, otel detayları, konaklama bilgisi, konaklama arama

**Examples:**
- "Moskovaya uçmak istiyorum" → FLIGHT
- "İstanbul'dan Berlin'e uçuş" → FLIGHT  
- "Ankara'ya uçak bileti" → FLIGHT
- "Tokyo'da otel" → HOTEL
- "Berlin otelleri" → HOTEL

**Context Information:**
Previous intent: {previous_intent}  
Previous entities: {filled_slots}  
Conversation history: {context} 

User Input: {user_input}

IMPORTANT: Look for the word "uçmak" - this means "to fly" and should ALWAYS be classified as FLIGHT!

Based on the input, respond with exactly one word: FLIGHT or HOTEL
""")