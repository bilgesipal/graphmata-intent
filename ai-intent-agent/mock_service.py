
import asyncio
import json

from src.config.config import AppConfig
from src.util.utilities import  get_redis_client



def simulate_publish_chat(channel):
    message = {
        "end": "True",
        "user_id": "prometa@bizigo.com",
        "session_id": "session_929",
        "message_id": "21",
        "trace_id": 8,
        "response": "chat",
        "chat": "Here are some hotels in Ankara (listing the first 10):\n"
                "- **Hotel Aquino Berlin**"
                "- ibis Styles Ankara\n"
                "- The Ankara Hotel\n"
                "- No:19 Boutique Hotel\n"
                "- Notte Hotel\n"
                "Would you like to see more from the list (up to 100), or would you like details about any specific hotel?\n"
                "Are you interested in certain amenities, a specific neighborhood, or a particular price range for your stay?",
        "system_message": "Lorem ipsum"
    }

    mesage2 = {"end": "True",
               "user_id": "prometa@bizigo.com",
                 "session_id": "session_926",
  "message_id": "21",
               "sequence": 5,
               "trace_id": 2,
               "response": "chat",
               "chat": "Seyahatiniz i\u00e7in hangi konumda, otelde ka\u00e7 ki\u015fi ve ka\u00e7 oda ile ne tarihlerde kalmay\u0131 d\u00fc\u015f\u00fcnd\u00fc\u011f\u00fcn\u00fcz\u00fc payla\u015fabilir misiniz?",
               "system_message": ""
               }

    message3 = {
        "end": "True",
        "user_id": "prometa@bizigo.com",
          "session_id": "session_929",
         "message_id": "21",
        "trace_id": 8,
        "response": "chat",
        "chat": (
            "Here are some hotels in Ankara (listing the first 10):\n"
            "- **Hotel Aquino Berlin** {hotel_data: {\"zone\": \"Kızılay\", \"lat\": 39.9208, \"long\": 32.8541, \"images\": [\"https://i.travelapi.com/lodging/51937381/192fa6d3_b.jpg\", \"https://i.travelapi.com/lodging/51937381/6247fa35_b.jpg\", \"https://i.travelapi.com/lodging/51937381/4647f578_b.jpg\"], \"stars\": 4, \"type\": \"Hotel\"}}: A modern hotel near the city center, known for its quiet surroundings.\n"
            "- **ibis Styles Ankara** {hotel_data: {\"zone\": \"Çankaya\", \"lat\": 39.9117, \"long\": 32.8636, \"images\": [\"https://i.travelapi.com/lodging/ibis1.jpg\", \"https://i.travelapi.com/lodging/ibis2.jpg\", \"https://i.travelapi.com/lodging/ibis3.jpg\"], \"stars\": 3, \"type\": \"Hotel\"}}: A stylish hotel offering comfort and accessibility for business travelers.\n"
            "- **The Ankara Hotel** {hotel_data: {\"zone\": \"Ulus\", \"lat\": 39.9439, \"long\": 32.8560, \"images\": [\"https://i.travelapi.com/lodging/ankara1.jpg\", \"https://i.travelapi.com/lodging/ankara2.jpg\", \"https://i.travelapi.com/lodging/ankara3.jpg\"], \"stars\": 5, \"type\": \"Hotel\"}}: Located next to the train station with elegant rooms and city views.\n"
            "- **No:19 Boutique Hotel** {hotel_data: {\"zone\": \"Gaziosmanpaşa\", \"lat\": 39.8993, \"long\": 32.8610, \"images\": [\"https://i.travelapi.com/lodging/no19_1.jpg\", \"https://i.travelapi.com/lodging/no19_2.jpg\", \"https://i.travelapi.com/lodging/no19_3.jpg\"], \"stars\": 4, \"type\": \"Boutique Hotel\"}}: A boutique stay featuring uniquely designed rooms and a cozy ambiance.\n"
            "- **Notte Hotel** {hotel_data: {\"zone\": \"Kavaklıdere\", \"lat\": 39.9095, \"long\": 32.8597, \"images\": [\"https://i.travelapi.com/lodging/notte1.jpg\", \"https://i.travelapi.com/lodging/notte2.jpg\", \"https://i.travelapi.com/lodging/notte3.jpg\"], \"stars\": 3, \"type\": \"Hotel\"}}: Centrally located with friendly service and easy access to attractions.\n\n"
            "Would you like to see more from the list (up to 100), or would you like details about any specific hotel?\n"
            "Are you interested in certain amenities, a specific neighborhood, or a particular price range for your stay?"
        ),
        "system_message": "Lorem ipsum"
    }

    redis_client = get_redis_client()

    redis_client.publish(channel, json.dumps(message3))
    print(f"Message published to Redis channel {channel}")


def simulate_publish_hotels(channel):

    message2 = {
  "end": "False",
  "response": "hotel_list",
  "URL": "/Hotel/list",
  "user_id": "prometa@bizigo.com",
        "session_id": "926",
        "message_id": "21",
  "sequence": 8,
  "trace_id": 8,
  "payload": {
    "inPolicy": 'false',
    "id": "JPD041476",
    "checkinDate": "2025-07-20",
    "checkoutDate": "2025-07-22",
    "travelUsageType": "corporate",
    "hotelCodes": [
      "JP007023",
      "JP110685",
      "JP007243",
      "JP156343",
      "JP007035",
      "JP760586",
      "JP007184",
      "JP112177",
      "JP110729",
      "JP926559",
      "JP007060",
      "JP007026",
      "JP01027Q",
      "JP137231",
      "JP058744",
      "JP816060",
      "JP982688",
      "JP146942",
      "JP148359",
      "JP361721",
      "JP317482",
      "JP02884R"
    ],
    "rooms": [
      {
        "id": 0,
        "customerIds": [
          "1BB01C081BDC1C971BBB1FDB1C1E1F4C",
          "1B8F1B6E1C601C8C"
        ],
        "passengerCount": 2
      },
      {
        "id": 1,
        "customerIds": [
          "1C6B1B6E1C601C8C1B6E1C1E1FA41F4C",
          "1C6B1B6E1A871A711B6E1BB01FA41F4C"
        ],
        "passengerCount": 2
      }
    ]
  }
}







    redis_client = get_redis_client()

    redis_client.publish(channel, json.dumps(message2))
    print(f"Message published to Redis channel {channel}")

def get_hotels():
    r= get_redis_client()
    keys = r.keys("prometa:HotelSearch:*")
    hotel_names = [key.replace("prometa:HotelSearch:", "") for key in keys]
    price_pol = [name for name in hotel_names if name.startswith("Price")]
    hotel = [name for name in hotel_names if not name.startswith("Price")]
    return hotel, price_pol

if __name__ == "__main__":
    #channel = "gateway"
    #simulate_publish_hotels(channel)
    #simulate_publish_chat(channel)
    hotels, pp = get_hotels()
    print(hotels, pp)



