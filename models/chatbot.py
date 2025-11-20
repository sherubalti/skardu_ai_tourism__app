# import re
# import random
# from datetime import datetime
# import json

# class TourismChatbot:
#     def __init__(self, hotels_data):
#         self.hotels_data = hotels_data
#         self.context = {}
        
#         # Response templates
#         self.greetings = [
#             "Hello! I'm your Skardu tourism assistant. How can I help you today?",
#             "Hi there! Ready to explore Skardu? What would you like to know?",
#             "Welcome to Skardu Explorer AI! How can I assist with your travel plans?"
#         ]
        
#         self.farewells = [
#             "Happy travels! Enjoy your time in Skardu!",
#             "Have a wonderful journey in Skardu!",
#             "Safe travels! Don't forget to visit Deosai Plains!"
#         ]
        
#         # Knowledge base
#         self.knowledge_base = self._build_knowledge_base()

#     def _build_knowledge_base(self):
#         """Build chatbot knowledge base from hotel data"""
#         knowledge = {
#             'places': set(),
#             'facilities': set(),
#             'activities': set(),
#             'hotel_names': [],
#             'locations': set()
#         }
        
#         for hotel in self.hotels_data:
#             # Hotel names
#             knowledge['hotel_names'].append(hotel['hotelGuestHouseName'])
            
#             # Locations
#             knowledge['locations'].add(hotel['fullAddress'].split(',')[-1].strip())
            
#             # Popular places
#             for place in hotel.get('mostPopularPlaces', []):
#                 knowledge['places'].add(place.lower())
            
#             # Facilities
#             facilities = hotel.get('facilities', {})
#             if facilities.get('wifiInternet'):
#                 knowledge['facilities'].add('wifi')
#             if facilities.get('guideServices'):
#                 knowledge['facilities'].add('guide services')
#             if facilities.get('restaurantDining'):
#                 knowledge['facilities'].add('restaurant')
            
#             # Activities from interests
#             interests = hotel.get('mostlyTouristInterests', {})
#             for activity, available in interests.items():
#                 if available:
#                     knowledge['activities'].add(activity)
        
#         return knowledge

#     def get_response(self, user_message, chat_history=None):
#         """Generate response to user message"""
#         if chat_history is None:
#             chat_history = []
        
#         user_message = user_message.lower().strip()
        
#         # Update context from chat history
#         self._update_context(chat_history)
        
#         # Classify intent and generate response
#         intent = self._classify_intent(user_message)
#         response = self._generate_response(intent, user_message)
        
#         return response

#     def _classify_intent(self, message):
#         """Classify user intent"""
#         message_lower = message.lower()
        
#         # Greeting detection
#         if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
#             return 'greeting'
        
#         # Farewell detection
#         if any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'thanks']):
#             return 'farewell'
        
#         # Hotel inquiries
#         if any(word in message_lower for word in ['hotel', 'stay', 'accommodation', 'room', 'guesthouse']):
#             return 'hotel_inquiry'
        
#         # Place recommendations
#         if any(word in message_lower for word in ['place', 'visit', 'see', 'attraction', 'destination']):
#             return 'place_recommendation'
        
#         # Budget inquiries
#         if any(word in message_lower for word in ['cost', 'price', 'budget', 'expensive', 'cheap']):
#             return 'budget_inquiry'
        
#         # Facility inquiries
#         if any(word in message_lower for word in ['wifi', 'internet', 'restaurant', 'food', 'transport']):
#             return 'facility_inquiry'
        
#         # Weather and season
#         if any(word in message_lower for word in ['weather', 'season', 'cold', 'warm', 'snow']):
#             return 'weather_inquiry'
        
#         # General information
#         if any(word in message_lower for word in ['what', 'when', 'where', 'how', 'why']):
#             return 'general_inquiry'
        
#         return 'general_response'

#     def _generate_response(self, intent, message):
#         """Generate response based on intent"""
#         if intent == 'greeting':
#             return random.choice(self.greetings)
        
#         elif intent == 'farewell':
#             return random.choice(self.farewells)
        
#         elif intent == 'hotel_inquiry':
#             return self._handle_hotel_inquiry(message)
        
#         elif intent == 'place_recommendation':
#             return self._handle_place_recommendation(message)
        
#         elif intent == 'budget_inquiry':
#             return self._handle_budget_inquiry(message)
        
#         elif intent == 'facility_inquiry':
#             return self._handle_facility_inquiry(message)
        
#         elif intent == 'weather_inquiry':
#             return self._handle_weather_inquiry()
        
#         elif intent == 'general_inquiry':
#             return self._handle_general_inquiry(message)
        
#         else:
#             return self._handle_general_response()

#     def _handle_hotel_inquiry(self, message):
#         """Handle hotel-related inquiries"""
#         # Extract budget level if mentioned
#         budget_keywords = {
#             'low': ['cheap', 'budget', 'economy', 'low cost', 'affordable'],
#             'high': ['luxury', 'expensive', 'premium', 'high end', 'deluxe'],
#             'medium': ['moderate', 'medium', 'standard', 'normal']
#         }
        
#         budget_level = 'medium'
#         for level, keywords in budget_keywords.items():
#             if any(keyword in message for keyword in keywords):
#                 budget_level = level
#                 break
        
#         # Extract facilities if mentioned
#         facilities = []
#         facility_keywords = {
#             'wifi': ['wifi', 'internet'],
#             'restaurant': ['restaurant', 'food', 'dining'],
#             'transport': ['transport', 'vehicle', 'car'],
#             'guide': ['guide', 'tour guide']
#         }
        
#         for facility, keywords in facility_keywords.items():
#             if any(keyword in message for keyword in keywords):
#                 facilities.append(facility)
        
#         # Find matching hotels
#         matching_hotels = []
#         for hotel in self.hotels_data:
#             hotel_budget = self._categorize_hotel_budget(hotel)
#             if hotel_budget == budget_level:
#                 matching_hotels.append(hotel)
        
#         if matching_hotels:
#             # Select a few representative hotels
#             sample_hotels = random.sample(matching_hotels, min(3, len(matching_hotels)))
#             response = f"For {budget_level} budget accommodations in Skardu, I recommend:\n\n"
            
#             for i, hotel in enumerate(sample_hotels, 1):
#                 facilities_list = self._get_hotel_facilities(hotel)
#                 response += f"{i}. {hotel['hotelGuestHouseName']}\n"
#                 response += f"   📍 {hotel['fullAddress']}\n"
#                 response += f"   🏠 {hotel['facilities']['rooms']['numberOfRooms']} rooms\n"
#                 response += f"   ⭐ Facilities: {', '.join(facilities_list[:3])}\n\n"
            
#             response += "Would you like more details about any of these hotels?"
#             return response
#         else:
#             return "I couldn't find hotels matching your criteria. Could you please specify your budget range (low/medium/high)?"

#     def _handle_place_recommendation(self, message):
#         """Handle place recommendation requests"""
#         popular_places = [
#             "Deosai Plains - The world's second highest plateau with breathtaking views",
#             "Shangrila Resort - Beautiful lake resort with stunning scenery",
#             "Kachura Lake - Crystal clear lake surrounded by mountains",
#             "Manthoka Waterfall - Majestic waterfall in the heart of nature",
#             "Kharpocho Fort - Historical fort overlooking Skardu town",
#             "Basho Valley - Picturesque valley with traditional villages",
#             "Shigar Valley - Gateway to some of the world's highest peaks",
#             "Katpana Desert - Cold desert with unique landscape"
#         ]
        
#         response = "Here are some must-visit places in Skardu:\n\n"
#         for i, place in enumerate(popular_places[:5], 1):
#             response += f"{i}. {place}\n"
        
#         response += "\nWhich type of places interest you most? (Lakes, Mountains, Historical sites, etc.)"
#         return response

#     def _handle_budget_inquiry(self, message):
#         """Handle budget-related questions"""
#         budget_estimates = {
#             'low': "💰 Budget travel: 3,000-5,000 PKR per day (basic accommodation + food + local transport)",
#             'medium': "💰 Moderate travel: 5,000-10,000 PKR per day (comfortable hotel + good food + guided tours)",
#             'high': "💰 Luxury travel: 10,000-20,000+ PKR per day (premium hotels + fine dining + private transport)"
#         }
        
#         response = "Here are approximate daily costs for Skardu tourism:\n\n"
#         for estimate in budget_estimates.values():
#             response += f"• {estimate}\n"
        
#         response += "\nThe cost includes accommodation, food, transportation, and basic activities. "
#         response += "Would you like a detailed cost breakdown for your specific travel plans?"
#         return response

#     def _handle_facility_inquiry(self, message):
#         """Handle facility-related questions"""
#         facilities_info = {
#             'wifi': "Many hotels in Skardu offer WiFi, but speed may vary. Major hotels and guesthouses in Skardu town have reliable internet.",
#             'transport': "Most hotels can arrange transportation. You can also hire local taxis or use hotel shuttle services.",
#             'guide': "Professional guide services are available through hotels or local tour operators. Recommended for trekking and remote areas.",
#             'restaurant': "Hotels typically have restaurants serving local and continental cuisine. Local eateries offer authentic Balti food."
#         }
        
#         for facility, info in facilities_info.items():
#             if facility in message:
#                 return info
        
#         return "Most hotels in Skardu offer basic facilities like WiFi, restaurant, and transport arrangement. Luxury hotels provide additional amenities like laundry, conference rooms, and guided tours."

#     def _handle_weather_inquiry(self):
#         """Handle weather-related questions"""
#         current_month = datetime.now().month
        
#         if 11 <= current_month <= 2:
#             season = "Winter ❄️"
#             weather = "Very cold with snow. Temperature: -10°C to 5°C"
#             advice = "Pack heavy woolens, thermal wear, and waterproof boots"
#         elif 3 <= current_month <= 5:
#             season = "Spring 🌸"
#             weather = "Pleasant with blooming flowers. Temperature: 5°C to 15°C"
#             advice = "Light woolens and jackets recommended"
#         elif 6 <= current_month <= 8:
#             season = "Summer ☀️"
#             weather = "Warm days, cool nights. Temperature: 10°C to 25°C"
#             advice = "Light clothing for day, jacket for evening"
#         else:
#             season = "Autumn 🍂"
#             weather = "Mild with beautiful foliage. Temperature: 5°C to 18°C"
#             advice = "Layered clothing recommended"
        
#         response = f"Current season in Skardu: {season}\n"
#         response += f"Weather: {weather}\n"
#         response += f"Travel advice: {advice}\n\n"
#         response += "Best time to visit: May to October for pleasant weather and accessible roads."
        
#         return response

#     def _handle_general_inquiry(self, message):
#         """Handle general information requests"""
#         general_responses = {
#             'best time': "The best time to visit Skardu is from May to October when the weather is pleasant and all attractions are accessible.",
#             'how to reach': "You can reach Skardu by flight from Islamabad or by road via Karakoram Highway. The journey by road takes about 20-24 hours.",
#             'local food': "Must-try local foods: Chapshuro (meat pie), Balti soups, Apricot juice, and various dried fruits.",
#             'culture': "Skardu has rich Balti culture with Tibetan influences. People are known for their hospitality and traditional music.",
#             'safety': "Skardu is generally safe for tourists. However, always follow local guidelines and travel with registered guides for remote areas."
#         }
        
#         for keyword, response in general_responses.items():
#             if keyword in message:
#                 return response
        
#         return "Skardu is a beautiful region in Gilgit-Baltistan, Pakistan, known for its stunning landscapes, lakes, and mountains. It's the gateway to some of the world's highest peaks including K2. How can I help you plan your visit?"

#     def _handle_general_response(self):
#         """Handle when no specific intent is detected"""
#         general_responses = [
#             "I'm here to help you plan your Skardu adventure! You can ask me about hotels, places to visit, costs, or travel tips.",
#             "I specialize in Skardu tourism information. Feel free to ask about accommodations, attractions, budgets, or anything else!",
#             "As your Skardu travel assistant, I can help with hotel recommendations, itinerary planning, cost estimates, and local information."
#         ]
#         return random.choice(general_responses)

#     def _categorize_hotel_budget(self, hotel):
#         """Categorize hotel budget level"""
#         facilities = hotel.get('facilities', {})
#         score = 0
        
#         if facilities.get('wifiInternet'):
#             score += 1
#         if facilities.get('restaurantDining'):
#             score += 1
#         if hotel.get('hasOwnTransport'):
#             score += 2
        
#         if score >= 3:
#             return 'high'
#         elif score >= 1:
#             return 'medium'
#         else:
#             return 'low'

#     def _get_hotel_facilities(self, hotel):
#         """Extract hotel facilities as list"""
#         facilities = []
#         hotel_facilities = hotel.get('facilities', {})
        
#         if hotel_facilities.get('wifiInternet'):
#             facilities.append('WiFi')
#         if hotel_facilities.get('restaurantDining'):
#             facilities.append('Restaurant')
#         if hotel_facilities.get('guideServices'):
#             facilities.append('Guide')
#         if hotel_facilities.get('transportArrangement'):
#             facilities.append('Transport')
#         if hotel.get('hasOwnTransport'):
#             facilities.append('Own Transport')
        
#         return facilities

#     def _update_context(self, chat_history):
#         """Update chatbot context from chat history"""
#         # Extract recent user preferences from history
#         recent_messages = chat_history[-5:]  # Last 5 messages
        
#         for msg in recent_messages:
#             if msg.get('type') == 'user':
#                 message = msg.get('content', '').lower()
                
#                 # Extract budget preferences
#                 if 'budget' in message or 'cheap' in message or 'expensive' in message:
#                     if 'cheap' in message or 'low' in message:
#                         self.context['budget'] = 'low'
#                     elif 'expensive' in message or 'luxury' in message:
#                         self.context['budget'] = 'high'
#                     else:
#                         self.context['budget'] = 'medium'
                
#                 # Extract interest preferences
#                 interests = ['lake', 'mountain', 'historical', 'trekking', 'culture']
#                 for interest in interests:
#                     if interest in message:
#                         self.context['interests'] = self.context.get('interests', [])
#                         if interest not in self.context['interests']:
#                             self.context['interests'].append(interest)


import re
import random
from datetime import datetime

from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import torch


class TourismChatbot:
    def __init__(self, hotels_data):
        self.hotels_data = hotels_data
        self.context = {}

        # DialoGPT-small for dialog generation
        self.dialogpt_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        self.dialogpt_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

        # all-MiniLM-L6-v2 for semantic embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        self.chat_history_ids = None

        # Existing conversational templates
        self.greetings = [
            "Hello! I'm your Skardu tourism assistant. How can I help you today?",
            "Hi there! Ready to explore Skardu? What would you like to know?",
            "Welcome to Skardu Explorer AI! How can I assist with your travel plans?"
        ]
        self.farewells = [
            "Happy travels! Enjoy your time in Skardu!",
            "Have a wonderful journey in Skardu!",
            "Safe travels! Don't forget to visit Deosai Plains!"
        ]

        self.knowledge_base = self._build_knowledge_base()


    def _build_knowledge_base(self):
        knowledge = {
            'places': set(),
            'facilities': set(),
            'activities': set(),
            'hotel_names': [],
            'locations': set()
        }

        for hotel in self.hotels_data:
            hotel_name = hotel.get('hotelGuestHouseName')
            if hotel_name:
                knowledge['hotel_names'].append(hotel_name)
            full_address = hotel.get('fullAddress', '')
            if full_address:
                location = full_address.split(',')[-1].strip()
                knowledge['locations'].add(location)
            for place in hotel.get('mostPopularPlaces', []):
                if isinstance(place, str):
                    knowledge['places'].add(place.lower())
            facilities = hotel.get('facilities', {})
            if facilities.get('wifiInternet'):
                knowledge['facilities'].add('wifi')
            if facilities.get('guideServices'):
                knowledge['facilities'].add('guide services')
            if facilities.get('restaurantDining'):
                knowledge['facilities'].add('restaurant')
            interests = hotel.get('mostlyTouristInterests', {})
            for activity, available in interests.items():
                if available:
                    knowledge['activities'].add(activity)
        return knowledge


    def get_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []

        # Update context with recent chat history
        self._update_context(chat_history)

        # Use semantic embeddings to enrich understanding (optional extension)
        query_embedding = self.embedding_model.encode(user_message)

        # Use DialoGPT-small to generate response
        new_input_ids = self.dialogpt_tokenizer.encode(user_message + self.dialogpt_tokenizer.eos_token, return_tensors='pt')

        if self.chat_history_ids is not None:
            bot_input_ids = torch.cat([self.chat_history_ids, new_input_ids], dim=-1)
        else:
            bot_input_ids = new_input_ids

        self.chat_history_ids = self.dialogpt_model.generate(
            bot_input_ids, max_length=1000, pad_token_id=self.dialogpt_tokenizer.eos_token_id
        )

        bot_response = self.dialogpt_tokenizer.decode(
            self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True
        )

        # Optionally mix with intent based canned replies or override

        # Your existing fallback intent classification for specific queries
        intent = self._classify_intent(user_message)
        if intent != 'general_response':
            intent_response = self._generate_response(intent, user_message)
            # You can choose to combine or prioritize either response here
            # For example:
            return intent_response

        return bot_response


    def _classify_intent(self, message):
        message_lower = message.lower()
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'thanks']):
            return 'farewell'
        elif any(word in message_lower for word in ['hotel', 'stay', 'accommodation', 'room', 'guesthouse']):
            return 'hotel_inquiry'
        elif any(word in message_lower for word in ['place', 'visit', 'see', 'attraction', 'destination']):
            return 'place_recommendation'
        elif any(word in message_lower for word in ['cost', 'price', 'budget', 'expensive', 'cheap']):
            return 'budget_inquiry'
        elif any(word in message_lower for word in ['wifi', 'internet', 'restaurant', 'food', 'transport']):
            return 'facility_inquiry'
        elif any(word in message_lower for word in ['weather', 'season', 'cold', 'warm', 'snow']):
            return 'weather_inquiry'
        elif any(word in message_lower for word in ['what', 'when', 'where', 'how', 'why']):
            return 'general_inquiry'
        else:
            return 'general_response'


    def _generate_response(self, intent, message):
        if intent == 'greeting':
            return random.choice(self.greetings)
        elif intent == 'farewell':
            return random.choice(self.farewells)
        elif intent == 'hotel_inquiry':
            return self._handle_hotel_inquiry(message)
        elif intent == 'place_recommendation':
            return self._handle_place_recommendation(message)
        elif intent == 'budget_inquiry':
            return self._handle_budget_inquiry(message)
        elif intent == 'facility_inquiry':
            return self._handle_facility_inquiry(message)
        elif intent == 'weather_inquiry':
            return self._handle_weather_inquiry()
        elif intent == 'general_inquiry':
            return self._handle_general_inquiry(message)
        else:
            return self._handle_general_response()


    def _handle_budget_inquiry(self, message):
        budget_estimates = {
            'low': "💰 Budget travel: 3,000-5,000 PKR per day (basic accommodation + food + local transport)",
            'medium': "💰 Moderate travel: 5,000-10,000 PKR per day (comfortable hotel + good food + guided tours)",
            'high': "💰 Luxury travel: 10,000-20,000+ PKR per day (premium hotels + fine dining + private transport)"
        }
        response = "Here are approximate daily costs for Skardu tourism:\n\n"
        for estimate in budget_estimates.values():
            response += f"• {estimate}\n"
        response += "\nThe cost includes accommodation, food, transportation, and basic activities. "
        response += "Would you like a detailed cost breakdown for your specific travel plans?"
        return response


    def _handle_hotel_inquiry(self, message):
        # Your hotel inquiry logic from before
        return "Here are some hotels matching your criteria..."


    def _handle_place_recommendation(self, message):
        popular_places = [
            "Deosai Plains - The world's second highest plateau",
            "Shangrila Resort - Stunning lake resort",
            "Kachura Lake - Crystal clear lake",
            "Manthoka Waterfall - Majestic waterfall",
            "Kharpocho Fort - Historical fort overlooking Skardu"
        ]
        response = "Here are some must-visit places in Skardu:\n\n"
        for i, place in enumerate(popular_places, 1):
            response += f"{i}. {place}\n"
        response += "\nWhat type of attractions interest you most? (Lakes, Mountains, History, etc.)"
        return response


    def _handle_facility_inquiry(self, message):
        return "Most hotels offer WiFi, restaurant, and transport services. Is there a specific facility you want to know about?"


    def _handle_weather_inquiry(self):
        current_month = datetime.now().month
        if 11 <= current_month or current_month <= 2:
            return "It's winter in Skardu with cold weather and snow. Dress warmly!"
        elif 3 <= current_month <= 5:
            return "Spring in Skardu is pleasant with blooming flowers."
        elif 6 <= current_month <= 8:
            return "Summers are warm and perfect for sightseeing."
        else:
            return "Autumn offers mild weather and beautiful foliage."


    def _handle_general_inquiry(self, message):
        general_facts = {
            'culture': "Skardu has rich Balti culture with Tibetan influences and warm hospitality.",
            'safety': "Skardu is generally safe but always take precautions in remote areas.",
            'food': "Local specialties include Chapshuro, Balti soups, and dried fruits.",
            'how to reach': "You can reach Skardu by flights from Islamabad or by road via the Karakoram Highway."
        }
        for key, answer in general_facts.items():
            if key in message:
                return answer
        return "That's an interesting question about Skardu. Could you please specify further?"


    def _handle_general_response(self):
        responses = [
            "I can help you plan your Skardu trip with hotel, places, and budget info.",
            "Ask me anything about Skardu tourism and travel!",
            "Feel free to inquire about attractions, costs, or travel tips."
        ]
        return random.choice(responses)


    def _update_context(self, chat_history):
        recent_messages = chat_history[-5:]
        for msg in recent_messages:
            if msg.get('type') == 'user':
                message = msg.get('content', '').lower()
                if 'budget' in message or 'cheap' in message or 'expensive' in message:
                    if 'cheap' in message or 'low' in message:
                        self.context['budget'] = 'low'
                    elif 'expensive' in message or 'luxury' in message:
                        self.context['budget'] = 'high'
                    else:
                        self.context['budget'] = 'medium'
                interests = ['lake', 'mountain', 'historical', 'trekking', 'culture']
                for interest in interests:
                    if interest in message:
                        self.context.setdefault('interests', [])
                        if interest not in self.context['interests']:
                            self.context['interests'].append(interest)
