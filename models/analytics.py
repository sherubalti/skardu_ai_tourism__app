import numpy as np
import pandas as pd
from collections import Counter
import json

class AnalyticsEngine:
    def __init__(self, hotels_data):
        self.hotels_data = hotels_data
        self._precompute_analytics()

    def _precompute_analytics(self):
        """Precompute analytics data for fast retrieval"""
        self.analytics_cache = {
            'demographics': self._compute_demographics(),
            'facilities': self._compute_facilities_stats(),
            'popular_places': self._compute_popular_places(),
            'geographic': self._compute_geographic_stats(),
            'temporal': self._compute_temporal_stats()
        }

    def get_dashboard_data(self):
        """Get comprehensive dashboard data"""
        return {
            'summary_stats': self._get_summary_stats(),
            'demographics': self.analytics_cache['demographics'],
            'facilities': self.analytics_cache['facilities'],
            'popular_places': self.analytics_cache['popular_places'],
            'geographic_distribution': self.analytics_cache['geographic'],
            'revenue_estimates': self._estimate_revenue()
        }

    def get_comprehensive_analytics(self):
        """Get detailed analytics for advanced dashboard"""
        return {
            **self.get_dashboard_data(),
            'seasonal_trends': self._analyze_seasonal_trends(),
            'competitor_analysis': self._competitor_analysis(),
            'market_gaps': self._identify_market_gaps(),
            'growth_opportunities': self._identify_growth_opportunities()
        }

    def get_tourist_demographics(self):
        """Get tourist demographics analysis"""
        return self.analytics_cache['demographics']

    def get_popular_places_analysis(self):
        """Get popular places analysis"""
        return self.analytics_cache['popular_places']

    def get_facilities_analysis(self):
        """Get facilities analysis"""
        return self.analytics_cache['facilities']

    def _compute_demographics(self):
        """Compute tourist demographics"""
        demographics = {
            'total_tourists': 0,
            'pakistani_tourists': 0,
            'foreign_tourists': 0,
            'breakdown_by_origin': {},
            'breakdown_by_foreign_country': {},
            'local_vs_nonlocal': {'local': 0, 'non_local': 0}
        }

        for hotel in self.hotels_data:
            demo = hotel.get('touristDemographics', {})
            
            # Total tourists
            total = demo.get('totalTouristsRecorded', 0)
            demographics['total_tourists'] += total
            
            # Pakistani tourists
            pak_tourists = demo.get('pakistaniTourists', {})
            pak_count = pak_tourists.get('count', 0)
            demographics['pakistani_tourists'] += pak_count
            
            # Foreign tourists
            foreign_count = demo.get('foreignTourists', 0)
            demographics['foreign_tourists'] += foreign_count
            
            # Local vs non-local
            local_count = pak_tourists.get('local', 0)
            non_local_count = pak_tourists.get('nonLocal', 0)
            demographics['local_vs_nonlocal']['local'] += local_count
            demographics['local_vs_nonlocal']['non_local'] += non_local_count
            
            # Breakdown by origin
            for origin in pak_tourists.get('breakdownByOrigin', []):
                origin_name = origin.get('origin', 'Unknown')
                count = origin.get('count', 0)
                demographics['breakdown_by_origin'][origin_name] = \
                    demographics['breakdown_by_origin'].get(origin_name, 0) + count
            
            # Breakdown by foreign country
            for country in demo.get('breakdownByForeignCountry', []):
                country_name = country.get('country', 'Unknown')
                count = country.get('count', 0)
                demographics['breakdown_by_foreign_country'][country_name] = \
                    demographics['breakdown_by_foreign_country'].get(country_name, 0) + count

        return demographics

    def _compute_facilities_stats(self):
        """Compute facilities statistics"""
        facilities = {
            'wifi': 0,
            'guide_services': 0,
            'transport': 0,
            'restaurant': 0,
            'laundry': 0,
            'own_transport': 0,
            'conference_hall': 0,
            'parking': 0
        }

        total_hotels = len(self.hotels_data)

        for hotel in self.hotels_data:
            hotel_facilities = hotel.get('facilities', {})
            
            if hotel_facilities.get('wifiInternet'):
                facilities['wifi'] += 1
            if hotel_facilities.get('guideServices'):
                facilities['guide_services'] += 1
            if hotel_facilities.get('transportArrangement'):
                facilities['transport'] += 1
            if hotel_facilities.get('restaurantDining'):
                facilities['restaurant'] += 1
            if hotel_facilities.get('laundryServices'):
                facilities['laundry'] += 1
            if hotel.get('hasOwnTransport'):
                facilities['own_transport'] += 1
            
            # Check other facilities
            other_facilities = hotel_facilities.get('otherFacilities', '').lower()
            if 'conference' in other_facilities:
                facilities['conference_hall'] += 1
            if 'parking' in other_facilities:
                facilities['parking'] += 1

        # Convert to percentages
        facilities_percentage = {}
        for facility, count in facilities.items():
            facilities_percentage[facility] = {
                'count': count,
                'percentage': round((count / total_hotels) * 100, 2)
            }

        return facilities_percentage

    def _compute_popular_places(self):
        """Compute popular places analysis"""
        place_counter = Counter()
        
        for hotel in self.hotels_data:
            places = hotel.get('mostPopularPlaces', [])
            for place in places:
                place_counter[place] += 1
        
        return dict(place_counter.most_common())

    def _compute_geographic_stats(self):
        """Compute geographic distribution"""
        locations = {}
        
        for hotel in self.hotels_data:
            location_key = hotel['fullAddress'].split(',')[-1].strip()
            locations[location_key] = locations.get(location_key, 0) + 1
        
        return locations

    def _compute_temporal_stats(self):
        """Compute temporal statistics"""
        avg_occupancy = np.mean([h.get('averageOccupancyPerDay', 0) for h in self.hotels_data])
        avg_stay_duration = np.mean([h.get('averageStayDurationDays', 0) for h in self.hotels_data])
        
        return {
            'avg_occupancy': round(avg_occupancy, 2),
            'avg_stay_duration': round(avg_stay_duration, 2)
        }

    def _get_summary_stats(self):
        """Get summary statistics"""
        total_hotels = len(self.hotels_data)
        total_rooms = sum(h.get('facilities', {}).get('rooms', {}).get('numberOfRooms', 0) for h in self.hotels_data)
        total_tourists = self.analytics_cache['demographics']['total_tourists']
        
        return {
            'total_hotels': total_hotels,
            'total_rooms': total_rooms,
            'total_tourists': total_tourists,
            'avg_tourists_per_hotel': round(total_tourists / total_hotels) if total_hotels > 0 else 0,
            **self.analytics_cache['temporal']
        }

    def _estimate_revenue(self):
        """Estimate tourism revenue"""
        demographics = self.analytics_cache['demographics']
        
        # Simple revenue estimation model
        avg_spending_per_tourist = 15000  # PKR per tourist
        total_revenue = demographics['total_tourists'] * avg_spending_per_tourist
        
        return {
            'estimated_total_revenue': total_revenue,
            'revenue_per_tourist': avg_spending_per_tourist,
            'potential_growth': round(total_revenue * 0.3)  # 30% growth potential
        }

    def _analyze_seasonal_trends(self):
        """Analyze seasonal tourism trends"""
        # This would typically use historical data
        # For now, we'll provide estimated trends
        return {
            'peak_season': {'months': ['May', 'June', 'July', 'August', 'September'], 'factor': 1.8},
            'shoulder_season': {'months': ['April', 'October'], 'factor': 1.2},
            'off_season': {'months': ['November', 'December', 'January', 'February', 'March'], 'factor': 0.6}
        }

    def _competitor_analysis(self):
        """Perform competitor analysis"""
        hotels_by_size = {
            'small': [h for h in self.hotels_data if h.get('facilities', {}).get('rooms', {}).get('numberOfRooms', 0) < 10],
            'medium': [h for h in self.hotels_data if 10 <= h.get('facilities', {}).get('rooms', {}).get('numberOfRooms', 0) < 30],
            'large': [h for h in self.hotels_data if h.get('facilities', {}).get('rooms', {}).get('numberOfRooms', 0) >= 30]
        }
        
        return {
            'size_distribution': {size: len(hotels) for size, hotels in hotels_by_size.items()},
            'market_share_by_size': {
                size: round(len(hotels) / len(self.hotels_data) * 100, 2)
                for size, hotels in hotels_by_size.items()
            }
        }

    def _identify_market_gaps(self):
        """Identify market gaps and opportunities"""
        facilities = self.analytics_cache['facilities']
        
        # Identify facilities with low availability but high demand
        gaps = []
        
        if facilities['conference_hall']['percentage'] < 20:
            gaps.append("Conference facilities (only {:.1f}% availability)".format(facilities['conference_hall']['percentage']))
        
        if facilities['laundry']['percentage'] < 40:
            gaps.append("Laundry services (only {:.1f}% availability)".format(facilities['laundry']['percentage']))
        
        return gaps

    def _identify_growth_opportunities(self):
        """Identify growth opportunities"""
        demographics = self.analytics_cache['demographics']
        
        opportunities = []
        
        # Foreign tourist opportunities
        foreign_percentage = (demographics['foreign_tourists'] / demographics['total_tourists']) * 100
        if foreign_percentage < 20:
            opportunities.append("Increase foreign tourist focus (currently {:.1f}%)".format(foreign_percentage))
        
        # Facility improvement opportunities
        facilities = self.analytics_cache['facilities']
        if facilities['wifi']['percentage'] < 80:
            opportunities.append("Improve WiFi infrastructure")
        
        return opportunities