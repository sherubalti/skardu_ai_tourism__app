import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import re
from geopy.distance import geodesic
from datetime import datetime, timedelta
import json

class RecommendationEngine:
    def __init__(self, hotels_data):
        self.hotels_data = hotels_data
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self._build_models()
        self._precompute_features()
        
        # Price ranges for different budget levels (PKR)
        self.budget_levels = {
            'low': {'hotel_per_night': (1000, 3000), 'food_per_day': (500, 1500), 'transport_per_day': (500, 1500)},
            'medium': {'hotel_per_night': (3000, 7000), 'food_per_day': (1500, 3000), 'transport_per_day': (1500, 3000)},
            'high': {'hotel_per_night': (7000, 20000), 'food_per_day': (3000, 8000), 'transport_per_day': (3000, 8000)}
        }
        
        # Popular places with coordinates and characteristics
        self.popular_places = {
            'deosai_plains': {'name': 'Deosai Plains', 'type': 'nature', 'duration_hours': 6, 'cost': 2000, 'best_time': 'day'},
            'kachura_lake': {'name': 'Kachura Lake', 'type': 'lake', 'duration_hours': 4, 'cost': 1500, 'best_time': 'day'},
            'shangrila_lake': {'name': 'Shangrila Lake', 'type': 'lake', 'duration_hours': 3, 'cost': 1000, 'best_time': 'day'},
            'manthoka_waterfall': {'name': 'Manthoka Waterfall', 'type': 'waterfall', 'duration_hours': 5, 'cost': 1200, 'best_time': 'day'},
            'kharpocho_fort': {'name': 'Kharpocho Fort', 'type': 'historical', 'duration_hours': 2, 'cost': 500, 'best_time': 'day'},
            'basho_valley': {'name': 'Basho Valley', 'type': 'valley', 'duration_hours': 5, 'cost': 1800, 'best_time': 'day'},
            'shigar_valley': {'name': 'Shigar Valley', 'type': 'valley', 'duration_hours': 6, 'cost': 2200, 'best_time': 'day'},
            'khaplu_valley': {'name': 'Khaplu Valley', 'type': 'valley', 'duration_hours': 8, 'cost': 2500, 'best_time': 'day'},
            'katpana_desert': {'name': 'Katpana Desert', 'type': 'desert', 'duration_hours': 3, 'cost': 800, 'best_time': 'sunset'},
            'italian_k2_museum': {'name': 'Italian K2 Museum', 'type': 'museum', 'duration_hours': 2, 'cost': 300, 'best_time': 'day'}
        }

    def _build_models(self):
        """Build AI models for recommendations"""
        # Prepare features for content-based filtering
        features = []
        for hotel in self.hotels_data:
            feature_text = self._extract_hotel_features(hotel)
            features.append(feature_text)
        
        # Train TF-IDF vectorizer
        self.feature_matrix = self.vectorizer.fit_transform(features)
        
        # Build KNN model for similar hotels
        self.knn_model = NearestNeighbors(n_neighbors=10, metric='cosine')
        self.knn_model.fit(self.feature_matrix)

    def _precompute_features(self):
        """Precompute hotel features for faster recommendations"""
        self.hotel_features = {}
        for i, hotel in enumerate(self.hotels_data):
            self.hotel_features[i] = {
                'budget_category': self._categorize_budget(hotel),
                'facilities': self._extract_facilities(hotel),
                'interests': self._extract_interests(hotel),
                'location': (hotel['location']['latitude'], hotel['location']['longitude']),
                'rating_score': self._calculate_rating_score(hotel)
            }

    def _extract_hotel_features(self, hotel):
        """Extract text features from hotel data"""
        features = []
        
        # Hotel type
        hotel_type = []
        if hotel.get('type', {}).get('hotel'):
            hotel_type.append('hotel')
        if hotel.get('type', {}).get('guestHouse'):
            hotel_type.append('guesthouse')
        features.extend(hotel_type)
        
        # Facilities
        facilities = hotel.get('facilities', {})
        if facilities.get('wifiInternet'):
            features.append('wifi')
        if facilities.get('guideServices'):
            features.append('guide')
        if facilities.get('transportArrangement'):
            features.append('transport')
        if facilities.get('restaurantDining'):
            features.append('restaurant')
        if facilities.get('laundryServices'):
            features.append('laundry')
        if hotel.get('hasOwnTransport'):
            features.append('own_transport')
        
        # Construction materials
        materials = hotel.get('constructionMaterials', {})
        if materials.get('organic'):
            features.append('organic')
        if materials.get('wood'):
            features.append('wooden')
        
        # Tourist interests
        interests = hotel.get('mostlyTouristInterests', {})
        for interest, value in interests.items():
            if value:
                features.append(interest)
        
        # Popular places
        for place in hotel.get('mostPopularPlaces', []):
            features.append(place.lower().replace(' ', '_'))
        
        # Meals
        for meal in hotel.get('interestingMeals', []):
            if isinstance(meal, str) and meal.lower() != 'true':
                features.append(meal.lower())
        
        return ' '.join(features)

    def _categorize_budget(self, hotel):
        """Categorize hotel budget level based on features"""
        score = 0
        
        # Room-based scoring
        rooms = hotel.get('facilities', {}).get('rooms', {})
        num_rooms = rooms.get('numberOfRooms', 0)
        if num_rooms > 20:
            score += 2
        elif num_rooms > 10:
            score += 1
        
        # Facilities scoring
        facilities = hotel.get('facilities', {})
        if facilities.get('wifiInternet'):
            score += 1
        if facilities.get('restaurantDining'):
            score += 1
        if facilities.get('laundryServices'):
            score += 1
        if hotel.get('hasOwnTransport'):
            score += 2
        
        # Determine budget category
        if score >= 5:
            return 'high'
        elif score >= 3:
            return 'medium'
        else:
            return 'low'

    def recommend_hotels(self, budget='medium', interests=None, facilities=None, group_size=2, duration=3):
        """AI-powered hotel recommendations"""
        if interests is None:
            interests = []
        if facilities is None:
            facilities = []
        
        # Prepare user preference vector
        user_features = ' '.join(interests + facilities + [budget])
        user_vector = self.vectorizer.transform([user_features])
        
        # Find similar hotels
        distances, indices = self.knn_model.kneighbors(user_vector)
        
        recommendations = []
        for idx, distance in zip(indices[0], distances[0]):
            hotel = self.hotels_data[idx]
            similarity_score = 1 - distance
            
            # Filter by budget
            hotel_budget = self._categorize_budget(hotel)
            if budget != 'any' and hotel_budget != budget:
                continue
            
            # Calculate suitability score
            suitability_score = self._calculate_suitability_score(
                hotel, interests, facilities, group_size
            )
            
            # Combined score
            final_score = (similarity_score * 0.6) + (suitability_score * 0.4)
            
            # Estimate cost
            cost_estimate = self._estimate_hotel_cost(hotel, duration, group_size)
            
            recommendations.append({
                'hotel': hotel,
                'score': round(final_score, 3),
                'similarity_score': round(similarity_score, 3),
                'suitability_score': round(suitability_score, 3),
                'budget_category': hotel_budget,
                'cost_estimate': cost_estimate,
                'match_reasons': self._get_match_reasons(hotel, interests, facilities)
            })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:8]

    def _calculate_suitability_score(self, hotel, interests, facilities, group_size):
        """Calculate how suitable a hotel is for the user"""
        score = 0.5  # Base score
        
        # Interest matching
        hotel_interests = hotel.get('mostlyTouristInterests', {})
        matched_interests = sum(1 for interest in interests if hotel_interests.get(interest, False))
        if interests:
            score += (matched_interests / len(interests)) * 0.3
        
        # Facility matching
        hotel_facilities = self._extract_facilities(hotel)
        matched_facilities = sum(1 for facility in facilities if facility in hotel_facilities)
        if facilities:
            score += (matched_facilities / len(facilities)) * 0.2
        
        # Group size suitability
        rooms = hotel.get('facilities', {}).get('rooms', {})
        num_rooms = rooms.get('numberOfRooms', 0)
        if num_rooms >= group_size:
            score += 0.1
        
        return min(score, 1.0)

    def _estimate_hotel_cost(self, hotel, duration, group_size):
        """Estimate total cost for stay"""
        budget_level = self._categorize_budget(hotel)
        price_range = self.budget_levels[budget_level]
        
        # Base hotel cost
        avg_price = sum(price_range['hotel_per_night']) / 2
        hotel_cost = avg_price * duration
        
        # Additional costs estimation
        food_cost = (sum(price_range['food_per_day']) / 2) * duration * group_size
        transport_cost = (sum(price_range['transport_per_day']) / 2) * duration
        
        total_cost = hotel_cost + food_cost + transport_cost
        
        return {
            'hotel': round(hotel_cost),
            'food': round(food_cost),
            'transport': round(transport_cost),
            'total': round(total_cost),
            'per_person': round(total_cost / group_size) if group_size > 0 else 0
        }

    def create_itinerary(self, duration=5, budget='medium', interests=None, pace='moderate'):
        """Create AI-powered travel itinerary"""
        if interests is None:
            interests = []
        
        # Filter places by interests
        suitable_places = []
        for place_id, place_info in self.popular_places.items():
            if not interests or place_info['type'] in interests:
                suitable_places.append((place_id, place_info))
        
        # Sort by popularity/cost
        suitable_places.sort(key=lambda x: x[1]['cost'])
        
        # Create daily itinerary
        itinerary = []
        current_day = 1
        available_hours = 8 if pace == 'moderate' else 6 if pace == 'relaxed' else 10
        
        while current_day <= duration and suitable_places:
            day_activities = []
            day_hours_used = 0
            day_cost = 0
            
            # Morning activity
            if suitable_places:
                place_id, place_info = suitable_places.pop(0)
                if day_hours_used + place_info['duration_hours'] <= available_hours:
                    day_activities.append({
                        'time': 'Morning',
                        'activity': place_info['name'],
                        'duration': f"{place_info['duration_hours']} hours",
                        'cost': place_info['cost'],
                        'type': place_info['type'],
                        'best_time': place_info['best_time']
                    })
                    day_hours_used += place_info['duration_hours']
                    day_cost += place_info['cost']
            
            # Afternoon activity
            if suitable_places and day_hours_used < available_hours - 2:
                place_id, place_info = suitable_places.pop(0)
                if day_hours_used + place_info['duration_hours'] <= available_hours:
                    day_activities.append({
                        'time': 'Afternoon',
                        'activity': place_info['name'],
                        'duration': f"{place_info['duration_hours']} hours",
                        'cost': place_info['cost'],
                        'type': place_info['type'],
                        'best_time': place_info['best_time']
                    })
                    day_hours_used += place_info['duration_hours']
                    day_cost += place_info['cost']
            
            if day_activities:
                itinerary.append({
                    'day': current_day,
                    'activities': day_activities,
                    'total_hours': day_hours_used,
                    'total_cost': day_cost,
                    'pace': 'Moderate' if day_hours_used <= 6 else 'Busy'
                })
                current_day += 1
        
        # Calculate total costs
        total_itinerary_cost = sum(day['total_cost'] for day in itinerary)
        hotel_recommendations = self.recommend_hotels(budget=budget, interests=interests, duration=duration)
        
        return {
            'duration_days': duration,
            'budget_level': budget,
            'total_estimated_cost': total_itinerary_cost,
            'daily_itinerary': itinerary,
            'hotel_recommendations': hotel_recommendations[:3],
            'packing_suggestions': self._get_packing_suggestions(interests, duration)
        }

    def estimate_expenses(self, duration=5, budget_level='medium', group_size=2, activities=None):
        """Comprehensive expense estimation"""
        if activities is None:
            activities = []
        
        budget = self.budget_levels[budget_level]
        
        # Accommodation cost
        avg_hotel_price = sum(budget['hotel_per_night']) / 2
        accommodation_cost = avg_hotel_price * duration
        
        # Food cost
        avg_food_cost = sum(budget['food_per_day']) / 2
        food_cost = avg_food_cost * duration * group_size
        
        # Transportation cost
        avg_transport_cost = sum(budget['transport_per_day']) / 2
        transport_cost = avg_transport_cost * duration
        
        # Activity costs
        activity_cost = 0
        for activity in activities:
            if activity in self.popular_places:
                activity_cost += self.popular_places[activity]['cost']
        
        # Miscellaneous (20% of total)
        base_total = accommodation_cost + food_cost + transport_cost + activity_cost
        miscellaneous = base_total * 0.2
        
        total_cost = base_total + miscellaneous
        
        return {
            'breakdown': {
                'accommodation': round(accommodation_cost),
                'food': round(food_cost),
                'transportation': round(transport_cost),
                'activities': round(activity_cost),
                'miscellaneous': round(miscellaneous)
            },
            'total': round(total_cost),
            'per_person': round(total_cost / group_size) if group_size > 0 else 0,
            'per_day': round(total_cost / duration),
            'budget_level': budget_level
        }

    def _get_match_reasons(self, hotel, interests, facilities):
        """Generate reasons why hotel matches user preferences"""
        reasons = []
        
        # Interest matches
        hotel_interests = hotel.get('mostlyTouristInterests', {})
        matched_interests = [interest for interest in interests if hotel_interests.get(interest, False)]
        if matched_interests:
            reasons.append(f"Matches your interests: {', '.join(matched_interests)}")
        
        # Facility matches
        hotel_facilities = self._extract_facilities(hotel)
        matched_facilities = [facility for facility in facilities if facility in hotel_facilities]
        if matched_facilities:
            reasons.append(f"Offers facilities: {', '.join(matched_facilities)}")
        
        # Popular places nearby
        popular_places = hotel.get('mostPopularPlaces', [])
        if popular_places:
            reasons.append(f"Near popular places: {', '.join(popular_places[:2])}")
        
        return reasons

    def _extract_facilities(self, hotel):
        """Extract facility list from hotel data"""
        facilities = []
        hotel_facilities = hotel.get('facilities', {})
        
        if hotel_facilities.get('wifiInternet'):
            facilities.append('wifi')
        if hotel_facilities.get('guideServices'):
            facilities.append('guide')
        if hotel_facilities.get('transportArrangement'):
            facilities.append('transport')
        if hotel_facilities.get('restaurantDining'):
            facilities.append('restaurant')
        if hotel_facilities.get('laundryServices'):
            facilities.append('laundry')
        if hotel.get('hasOwnTransport'):
            facilities.append('own_transport')
        
        return facilities

    def _extract_interests(self, hotel):
        """Extract interests from hotel data"""
        interests = hotel.get('mostlyTouristInterests', {})
        return [interest for interest, value in interests.items() if value]

    def _calculate_rating_score(self, hotel):
        """Calculate a rating score based on hotel features"""
        score = 5.0  # Base score
        
        # Adjust based on facilities
        facilities = hotel.get('facilities', {})
        if facilities.get('wifiInternet'):
            score += 0.5
        if facilities.get('guideServices'):
            score += 0.3
        if facilities.get('restaurantDining'):
            score += 0.4
        if hotel.get('hasOwnTransport'):
            score += 0.6
        
        # Adjust based on tourist numbers (popularity)
        tourists = hotel.get('touristDemographics', {}).get('totalTouristsRecorded', 0)
        if tourists > 5000:
            score += 1.0
        elif tourists > 2000:
            score += 0.5
        
        return min(score, 10.0)

    def _get_packing_suggestions(self, interests, duration):
        """Generate packing suggestions based on interests and duration"""
        suggestions = {
            'essentials': ['Warm clothes', 'Comfortable shoes', 'Sunglasses', 'Sunscreen', 'Water bottle'],
            'electronics': ['Power bank', 'Camera', 'Phone charger'],
            'documents': ['ID card/Passport', 'Cash (PKR)', 'Hotel bookings']
        }
        
        # Activity-specific suggestions
        if 'lake' in interests or 'waterfall' in interests:
            suggestions['essentials'].extend(['Swimwear', 'Quick-dry towel'])
        if 'trekking' in interests or 'hiking' in interests:
            suggestions['essentials'].extend(['Hiking boots', 'Backpack', 'Walking sticks'])
        if 'historical' in interests:
            suggestions['essentials'].append('Guide book')
        
        # Duration-based suggestions
        if duration > 7:
            suggestions['essentials'].extend(['Extra clothing', 'Toiletries'])
        
        return suggestions