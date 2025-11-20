import json
import re


class DataLoader:
    def __init__(self):
        self.data_file = 'static/data/cleaned_tourist_data.json'

    def load_data(self):
        """Load and clean tourism data"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            hotels = data.get('touristData', [])
            cleaned_hotels = []

            for hotel in hotels:
                cleaned_hotel = self._clean_hotel_data(hotel)
                cleaned_hotels.append(cleaned_hotel)

            print(f"Successfully loaded {len(cleaned_hotels)} hotels")
            return cleaned_hotels

        except FileNotFoundError:
            print(f"Data file not found: {self.data_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []

    def _clean_hotel_data(self, hotel):
        """Clean individual hotel data"""
        # Ensure all required fields exist with default values
        hotel.setdefault('type', {'hotel': True, 'guestHouse': True, 'other': None})
        hotel.setdefault('location', {'latitude': 0, 'longitude': 0})
        hotel.setdefault('constructionMaterials', {'cement': True, 'wood': False, 'organic': False, 'other': None})
        hotel.setdefault('facilities', {
            'rooms': {'numberOfRooms': 0, 'available': True},
            'wifiInternet': False,
            'guideServices': False,
            'transportArrangement': False,
            'restaurantDining': False,
            'laundryServices': False,
            'otherFacilities': ''
        })
        hotel.setdefault('touristDemographics', {})
        demo = hotel['touristDemographics']
        demo.setdefault('totalTouristsRecorded', 0)
        demo.setdefault('pakistaniTourists', {'local': 0, 'nonLocal': 0, 'count': 0, 'breakdownByOrigin': []})
        demo.setdefault('foreignTourists', 0)
        demo.setdefault('breakdownByForeignCountry', [])

        hotel.setdefault('mostlyTouristInterests', {})
        hotel.setdefault('mostPopularPlaces', [])
        hotel.setdefault('additionalNotes', {
            'challengesFaced': '',
            'specialServices': '',
            'touristOriginFeedback': ''
        })

        # Clean numeric fields
        self._clean_numeric_fields(hotel)

        # Clean text fields
        self._clean_text_fields(hotel)

        # Clean list fields
        self._clean_list_fields(hotel)

        return hotel

    def _clean_numeric_fields(self, hotel):
        """Clean numeric fields in hotel data"""
        demo = hotel.get('touristDemographics', {})

        if 'totalTouristsRecorded' in demo and isinstance(demo['totalTouristsRecorded'], str):
            demo['totalTouristsRecorded'] = self._extract_number(demo['totalTouristsRecorded'])

        if 'foreignTourists' in demo and isinstance(demo['foreignTourists'], str):
            demo['foreignTourists'] = self._extract_number(demo['foreignTourists'])

        pak = demo.get('pakistaniTourists', {})
        for field in ['local', 'nonLocal', 'count']:
            if field in pak and isinstance(pak[field], str):
                pak[field] = self._extract_number(pak[field])

        for origin in pak.get('breakdownByOrigin', []):
            if 'count' in origin and isinstance(origin['count'], str):
                origin['count'] = self._extract_number(origin['count'])

        for country in demo.get('breakdownByForeignCountry', []):
            if 'count' in country and isinstance(country['count'], str):
                country['count'] = self._extract_number(country['count'])

        if 'averageOccupancyPerDay' in hotel and isinstance(hotel['averageOccupancyPerDay'], str):
            hotel['averageOccupancyPerDay'] = self._extract_number(hotel['averageOccupancyPerDay'])

        if 'averageStayDurationDays' in hotel and isinstance(hotel['averageStayDurationDays'], str):
            hotel['averageStayDurationDays'] = self._extract_number(hotel['averageStayDurationDays'])

        rooms = hotel['facilities'].get('rooms', {})
        if 'numberOfRooms' in rooms and isinstance(rooms['numberOfRooms'], str):
            rooms['numberOfRooms'] = self._extract_number(rooms['numberOfRooms'])

    def _clean_text_fields(self, hotel):
        """Clean text fields in hotel data"""
        if 'hotelGuestHouseName' in hotel and isinstance(hotel['hotelGuestHouseName'], str):
            hotel['hotelGuestHouseName'] = hotel['hotelGuestHouseName'].strip().title()

        hotel['fullAddress'] = hotel.get('fullAddress', '').strip()

        if 'phoneNumbers' in hotel:
            if isinstance(hotel['phoneNumbers'], str):
                hotel['phoneNumbers'] = [phone.strip() for phone in hotel['phoneNumbers'].split(',')]
            hotel['phoneNumbers'] = [re.sub(r'[^\d+]', '', str(phone)) for phone in hotel['phoneNumbers'] if phone and str(phone).strip()]

        other_facilities = hotel['facilities'].get('otherFacilities', '')
        if other_facilities and isinstance(other_facilities, str):
            hotel['facilities']['otherFacilities'] = other_facilities.strip()

    def _clean_list_fields(self, hotel):
        """Clean list fields in hotel data"""
        if 'interestingMeals' in hotel:
            if isinstance(hotel['interestingMeals'], str):
                hotel['interestingMeals'] = [meal.strip() for meal in hotel['interestingMeals'].split(',')]
            hotel['interestingMeals'] = [meal for meal in hotel['interestingMeals'] if isinstance(meal, str) and meal.lower() != 'true']

        if 'mostPopularPlaces' in hotel:
            if isinstance(hotel['mostPopularPlaces'], str):
                hotel['mostPopularPlaces'] = [place.strip() for place in hotel['mostPopularPlaces'].split(',')]
            hotel['mostPopularPlaces'] = [place for place in hotel['mostPopularPlaces'] if place]

    def _extract_number(self, text):
        """Extract first number from text or return 0"""
        if not text:
            return 0

        if isinstance(text, (int, float)):
            return int(text)

        numbers = re.findall(r'\d+', str(text))
        if numbers:
            return int(numbers[0])

        return 0
