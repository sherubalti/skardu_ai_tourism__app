from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
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


# Initialize session
Session(app)


# Load data
print("Loading tourism data...")
data_loader = DataLoader()
hotels_data = data_loader.load_data()


# Initialize AI models
print("Initializing AI models...")
recommendation_engine = RecommendationEngine(hotels_data)
chatbot = TourismChatbot(hotels_data)
analytics_engine = AnalyticsEngine(hotels_data)


print("AI models initialized successfully!")


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Interactive dashboard"""
    dashboard_data = analytics_engine.get_dashboard_data()
    return render_template('dashboard.html', data=dashboard_data)


@app.route('/recommendations')
def recommendations():
    """Hotel and place recommendations"""
    return render_template('recommendations.html')


@app.route('/chatbot')
def chatbot_interface():
    """Chatbot interface"""
    return render_template('chatbot.html')


@app.route('/analytics')
def analytics():
    """Advanced analytics"""
    analytics_data = analytics_engine.get_comprehensive_analytics()
    return render_template('analytics.html', data=analytics_data)


# API Routes
@app.route('/api/recommend/hotels', methods=['POST'])
def recommend_hotels():
    """AI hotel recommendation endpoint"""
    try:
        user_data = request.get_json()
        
        recommendations = recommendation_engine.recommend_hotels(
            budget=user_data.get('budget', 'medium'),
            interests=user_data.get('interests', []),
            facilities=user_data.get('facilities', []),
            group_size=user_data.get('group_size', 2),
            duration=user_data.get('duration', 3)
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommend/itinerary', methods=['POST'])
def recommend_itinerary():
    """AI itinerary planning endpoint"""
    try:
        user_data = request.get_json()
        
        itinerary = recommendation_engine.create_itinerary(
            duration=user_data.get('duration', 5),
            budget=user_data.get('budget', 'medium'),
            interests=user_data.get('interests', []),
            pace=user_data.get('pace', 'moderate')
        )
        
        return jsonify({
            'success': True,
            'itinerary': itinerary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommend/expenses', methods=['POST'])
def estimate_expenses():
    """Expense estimation endpoint"""
    try:
        user_data = request.get_json()
        
        expense_estimate = recommendation_engine.estimate_expenses(
            duration=user_data.get('duration', 5),
            budget_level=user_data.get('budget', 'medium'),
            group_size=user_data.get('group_size', 2),
            activities=user_data.get('activities', [])
        )
        
        return jsonify({
            'success': True,
            'expense_estimate': expense_estimate
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        chat_history = request.json.get('history', [])
        response = chatbot.get_response(user_message, chat_history)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        app.logger.error("Exception in /api/chat:\n" + traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


# @app.route('/api/chat', methods=['POST'])
# def chat():
#     """Chatbot endpoint"""
#     try:
#         user_message = request.json.get('message', '')
#         chat_history = request.json.get('history', [])
        
#         response = chatbot.get_response(user_message, chat_history)
        
#         return jsonify({
#             'success': True,
#             'response': response
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500


@app.route('/api/analytics/demographics')
def get_demographics():
    """Tourist demographics analytics"""
    try:
        demographics = analytics_engine.get_tourist_demographics()
        return jsonify({
            'success': True,
            'data': demographics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analytics/popular-places')
def get_popular_places():
    """Popular places analytics"""
    try:
        popular_places = analytics_engine.get_popular_places_analysis()
        return jsonify({
            'success': True,
            'data': popular_places
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analytics/facilities')
def get_facilities_analysis():
    """Facilities analysis"""
    try:
        facilities = analytics_engine.get_facilities_analysis()
        return jsonify({
            'success': True,
            'data': facilities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@app.route('/api/hotels/locations')
def get_hotel_locations():
    """Get hotel locations for mapping"""
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
        return jsonify({
            'success': True,
            'locations': locations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/hotels/search')
def search_hotels():
    """Search hotels with advanced filtering"""
    try:
        query = request.args.get('q', '')
        budget = request.args.get('budget', 'all')
        facilities = request.args.getlist('facilities')
        
        filtered_hotels = hotels_data
        
        # Text search
        if query:
            filtered_hotels = [
                h for h in filtered_hotels 
                if query.lower() in h['hotelGuestHouseName'].lower()
                or query.lower() in h['fullAddress'].lower()
            ]
        
        # Budget filter (simplified implementation)
        if budget != 'all':
            # You would implement actual budget categorization here
            pass
        
        # Facilities filter
        if facilities:
            filtered_hotels = [
                h for h in filtered_hotels
                if ('wifi' not in facilities or h['facilities']['wifiInternet'])
                and ('restaurant' not in facilities or h['facilities']['restaurantDining'])
                and ('transport' not in facilities or h['facilities']['transportArrangement'] or h.get('hasOwnTransport', False))
            ]
        
        return jsonify({
            'success': True,
            'hotels': filtered_hotels,
            'total': len(filtered_hotels)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/hotels')
def get_hotels():
    """Get all hotels with filtering"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        
        filtered_hotels = hotels_data
        if search:
            filtered_hotels = [
                h for h in hotels_data 
                if search.lower() in h['hotelGuestHouseName'].lower()
                or search.lower() in h['fullAddress'].lower()
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


# from flask import Flask, render_template, request, jsonify, session
# from flask_session import Session
# from flask_cors import CORS, cross_origin  # ADD THIS IMPORT
# import json
# import numpy as np
# import pandas as pd
# from datetime import datetime
# import os
# import traceback

# from models.recommendation_engine import RecommendationEngine
# from models.chatbot import TourismChatbot
# from models.analytics import AnalyticsEngine
# from utils.data_loader import DataLoader

# app = Flask(__name__)
# app.config.from_pyfile('config.py')

# # ADD CORS CONFIGURATION HERE
# CORS(app, resources={
#     r"/api/*": {
#         "origins": ["http://localhost:8081", "http://192.168.0.101:5000", "http://localhost:5000", "http://127.0.0.1:8081"],
#         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Authorization", "Accept"]
#     }
# })

# # Initialize session
# Session(app)

# # Load data
# print("Loading tourism data...")
# data_loader = DataLoader()
# hotels_data = data_loader.load_data()

# # Initialize AI models
# print("Initializing AI models...")
# recommendation_engine = RecommendationEngine(hotels_data)
# chatbot = TourismChatbot(hotels_data)
# analytics_engine = AnalyticsEngine(hotels_data)

# print("AI models initialized successfully!")

# # Your existing routes continue below...
# @app.route('/')
# def index():
#     """Main dashboard page"""
#     return render_template('index.html')
# @app.route('/recommendations')
# @cross_origin()
# def recommendations():
#     """Recommendations page"""
#     return render_template('recommendations.html')  # Make sure this template exists

# # ... ALL YOUR EXISTING ROUTES REMAIN THE SAME ...

# # ADD @cross_origin() DECORATOR TO ALL API ROUTES:
# @app.route('/api/recommend/hotels', methods=['POST'])
# @cross_origin()
# def recommend_hotels():
#     """AI hotel recommendation endpoint"""
#     try:
#         user_data = request.get_json()
        
#         recommendations = recommendation_engine.recommend_hotels(
#             budget=user_data.get('budget', 'medium'),
#             interests=user_data.get('interests', []),
#             facilities=user_data.get('facilities', []),
#             group_size=user_data.get('group_size', 2),
#             duration=user_data.get('duration', 3)
#         )
        
#         return jsonify({
#             'success': True,
#             'recommendations': recommendations
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/recommend/itinerary', methods=['POST'])
# @cross_origin()
# def recommend_itinerary():
#     """AI itinerary planning endpoint"""
#     try:
#         user_data = request.get_json()
        
#         itinerary = recommendation_engine.create_itinerary(
#             duration=user_data.get('duration', 5),
#             budget=user_data.get('budget', 'medium'),
#             interests=user_data.get('interests', []),
#             pace=user_data.get('pace', 'moderate')
#         )
        
#         return jsonify({
#             'success': True,
#             'itinerary': itinerary
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/recommend/expenses', methods=['POST'])
# @cross_origin()
# def estimate_expenses():
#     """Expense estimation endpoint"""
#     try:
#         user_data = request.get_json()
        
#         expense_estimate = recommendation_engine.estimate_expenses(
#             duration=user_data.get('duration', 5),
#             budget_level=user_data.get('budget', 'medium'),
#             group_size=user_data.get('group_size', 2),
#             activities=user_data.get('activities', [])
#         )
        
#         return jsonify({
#             'success': True,
#             'expense_estimate': expense_estimate
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/chat', methods=['POST'])
# @cross_origin()
# def chat():
#     try:
#         user_message = request.json.get('message', '')
#         chat_history = request.json.get('history', [])
#         response = chatbot.get_response(user_message, chat_history)
#         return jsonify({'success': True, 'response': response})
#     except Exception as e:
#         app.logger.error("Exception in /api/chat:\n" + traceback.format_exc())
#         return jsonify({'success': False, 'error': str(e)}), 500

# @app.route('/api/analytics/demographics')
# @cross_origin()
# def get_demographics():
#     """Tourist demographics analytics"""
#     try:
#         demographics = analytics_engine.get_tourist_demographics()
#         return jsonify({
#             'success': True,
#             'data': demographics
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/analytics/popular-places')
# @cross_origin()
# def get_popular_places():
#     """Popular places analytics"""
#     try:
#         popular_places = analytics_engine.get_popular_places_analysis()
#         return jsonify({
#             'success': True,
#             'data': popular_places
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/analytics/facilities')
# @cross_origin()
# def get_facilities_analysis():
#     """Facilities analysis"""
#     try:
#         facilities = analytics_engine.get_facilities_analysis()
#         return jsonify({
#             'success': True,
#             'data': facilities
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/hotels/locations')
# @cross_origin()
# def get_hotel_locations():
#     """Get hotel locations for mapping"""
#     try:
#         locations = []
#         for hotel in hotels_data:
#             locations.append({
#                 'name': hotel['hotelGuestHouseName'],
#                 'lat': hotel['location']['latitude'],
#                 'lng': hotel['location']['longitude'],
#                 'address': hotel['fullAddress'],
#                 'type': 'hotel' if hotel['type']['hotel'] else 'guest_house',
#                 'rooms': hotel['facilities']['rooms']['numberOfRooms'],
#                 'tourists': hotel['touristDemographics']['totalTouristsRecorded'],
#                 'has_wifi': hotel['facilities']['wifiInternet'],
#                 'has_restaurant': hotel['facilities']['restaurantDining'],
#                 'has_transport': hotel['facilities']['transportArrangement'] or hotel.get('hasOwnTransport', False),
#                 'phone_numbers': hotel.get('phoneNumbers', [])
#             })
#         return jsonify({
#             'success': True,
#             'locations': locations
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/hotels/search')
# @cross_origin()
# def search_hotels():
#     """Search hotels with advanced filtering"""
#     try:
#         query = request.args.get('q', '')
#         budget = request.args.get('budget', 'all')
#         facilities = request.args.getlist('facilities')
        
#         filtered_hotels = hotels_data
        
#         # Text search
#         if query:
#             filtered_hotels = [
#                 h for h in filtered_hotels 
#                 if query.lower() in h['hotelGuestHouseName'].lower()
#                 or query.lower() in h['fullAddress'].lower()
#             ]
        
#         # Budget filter (simplified implementation)
#         if budget != 'all':
#             # You would implement actual budget categorization here
#             pass
        
#         # Facilities filter
#         if facilities:
#             filtered_hotels = [
#                 h for h in filtered_hotels
#                 if ('wifi' not in facilities or h['facilities']['wifiInternet'])
#                 and ('restaurant' not in facilities or h['facilities']['restaurantDining'])
#                 and ('transport' not in facilities or h['facilities']['transportArrangement'] or h.get('hasOwnTransport', False))
#             ]
        
#         return jsonify({
#             'success': True,
#             'hotels': filtered_hotels,
#             'total': len(filtered_hotels)
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/hotels')
# @cross_origin()
# def get_hotels():
#     """Get all hotels with filtering"""
#     try:
#         page = int(request.args.get('page', 1))
#         per_page = int(request.args.get('per_page', 10))
#         search = request.args.get('search', '')
        
#         filtered_hotels = hotels_data
#         if search:
#             filtered_hotels = [
#                 h for h in hotels_data 
#                 if search.lower() in h['hotelGuestHouseName'].lower()
#                 or search.lower() in h['fullAddress'].lower()
#             ]
        
#         start_idx = (page - 1) * per_page
#         end_idx = start_idx + per_page
#         paginated_hotels = filtered_hotels[start_idx:end_idx]
        
#         return jsonify({
#             'success': True,
#             'hotels': paginated_hotels,
#             'total': len(filtered_hotels),
#             'page': page,
#             'per_page': per_page
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)