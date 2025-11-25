from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from flask_cors import CORS  # Add this if frontend is separate (e.g., React on :3000)
import json
import numpy as np
import pandas as pd
from datetime import datetime
import os
import traceback

from models.recommendation_engine import RecommendationEngine
from models.chatbot import TourismChatbot
from models.analytics import AnalyticsEngine
from utils.data_loader import DataLoader

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Add CORS for Vercel (allows all origins in prod; restrict in dev)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize session
Session(app)

# Load data (with error handling)
try:
    print("Loading tourism data...")
    data_loader = DataLoader()
    hotels_data = data_loader.load_data()
    print(f"Loaded {len(hotels_data)} records.")
except Exception as e:
    print(f"Data load error: {e}")
    hotels_data = []  # Fallback empty list

# Initialize AI models (with try-except to prevent startup crash)
try:
    print("Initializing AI models...")
    recommendation_engine = RecommendationEngine(hotels_data)
    chatbot = TourismChatbot(hotels_data)
    analytics_engine = AnalyticsEngine(hotels_data)
    print("AI models initialized successfully!")
except Exception as e:
    print(f"Model init error: {e}")
    # Fallback dummies if needed
    class DummyEngine:
        def __getattr__(self, name): return lambda *a, **kw: {'success': False, 'error': 'Model unavailable'}
    recommendation_engine = DummyEngine()
    chatbot = DummyEngine()
    analytics_engine = DummyEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    dashboard_data = analytics_engine.get_dashboard_data()
    return render_template('dashboard.html', data=dashboard_data)

@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html')

@app.route('/chatbot')
def chatbot_interface():
    return render_template('chatbot.html')

@app.route('/analytics')
def analytics():
    analytics_data = analytics_engine.get_comprehensive_analytics()
    return render_template('analytics.html', data=analytics_data)

# API Routes (all with CORS implicitly via app-wide)
@app.route('/api/recommend/hotels', methods=['POST'])
def recommend_hotels():
    try:
        user_data = request.get_json()
        recommendations = recommendation_engine.recommend_hotels(
            budget=user_data.get('budget', 'medium'),
            interests=user_data.get('interests', []),
            facilities=user_data.get('facilities', []),
            group_size=user_data.get('group_size', 2),
            duration=user_data.get('duration', 3)
        )
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend/itinerary', methods=['POST'])
def recommend_itinerary():
    try:
        user_data = request.get_json()
        itinerary = recommendation_engine.create_itinerary(
            duration=user_data.get('duration', 5),
            budget=user_data.get('budget', 'medium'),
            interests=user_data.get('interests', []),
            pace=user_data.get('pace', 'moderate')
        )
        return jsonify({'success': True, 'itinerary': itinerary})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend/expenses', methods=['POST'])
def estimate_expenses():
    try:
        user_data = request.get_json()
        expense_estimate = recommendation_engine.estimate_expenses(
            duration=user_data.get('duration', 5),
            budget_level=user_data.get('budget', 'medium'),
            group_size=user_data.get('group_size', 2),
            activities=user_data.get('activities', [])
        )
        return jsonify({'success': True, 'expense_estimate': expense_estimate})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        chat_history = request.json.get('history', [])
        response = chatbot.get_response(user_message, chat_history)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/demographics')
def get_demographics():
    try:
        demographics = analytics_engine.get_tourist_demographics()
        return jsonify({'success': True, 'data': demographics})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/popular-places')
def get_popular_places():
    try:
        popular_places = analytics_engine.get_popular_places_analysis()
        return jsonify({'success': True, 'data': popular_places})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/facilities')
def get_facilities_analysis():
    try:
        facilities = analytics_engine.get_facilities_analysis()
        return jsonify({'success': True, 'data': facilities})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hotels/locations')
def get_hotel_locations():
    try:
        locations = []
        for hotel in hotels_data:
            locations.append({
                'name': hotel['hotelGuestHouseName'],
                'lat': hotel['location']['latitude'],
                'lng': hotel['location']['longitude'],
                'address': hotel['fullAddress'],
                'type': 'hotel' if hotel['type']['hotel'] else 'guest_house',
                'rooms': hotel['facilities']['rooms']['numberOfRooms'],
                'tourists': hotel['touristDemographics']['totalTouristsRecorded'],
                'has_wifi': hotel['facilities']['wifiInternet'],
                'has_restaurant': hotel['facilities']['restaurantDining'],
                'has_transport': hotel['facilities']['transportArrangement'] or hotel.get('hasOwnTransport', False),
                'phone_numbers': hotel.get('phoneNumbers', [])
            })
        return jsonify({'success': True, 'locations': locations})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hotels/search')
def search_hotels():
    try:
        query = request.args.get('q', '')
        budget = request.args.get('budget', 'all')
        facilities = request.args.getlist('facilities')
        
        filtered_hotels = hotels_data
        
        if query:
            filtered_hotels = [
                h for h in filtered_hotels 
                if query.lower() in h['hotelGuestHouseName'].lower() or query.lower() in h['fullAddress'].lower()
            ]
        
        if budget != 'all':
            # Implement budget logic here if needed
            pass
        
        if facilities:
            filtered_hotels = [
                h for h in filtered_hotels
                if ('wifi' not in facilities or h['facilities']['wifiInternet'])
                and ('restaurant' not in facilities or h['facilities']['restaurantDining'])
                and ('transport' not in facilities or h['facilities']['transportArrangement'] or h.get('hasOwnTransport', False))
            ]
        
        return jsonify({'success': True, 'hotels': filtered_hotels, 'total': len(filtered_hotels)})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hotels')
def get_hotels():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        
        filtered_hotels = hotels_data
        if search:
            filtered_hotels = [
                h for h in hotels_data 
                if search.lower() in h['hotelGuestHouseName'].lower() or search.lower() in h['fullAddress'].lower()
            ]
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_hotels = filtered_hotels[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'hotels': paginated_hotels,
            'total': len(filtered_hotels),
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
