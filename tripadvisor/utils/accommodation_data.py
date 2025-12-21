"""
Accommodation data utilities for the trip planner application.
Handles fetching and processing accommodation information.
"""

import random
from datetime import datetime, timedelta
import os
from tripadvisor.utils.crew_ai_agent import TravelCrewAI

# Initialize singleton instance of TravelCrewAI
_travel_crew_ai = None

def _get_travel_crew_ai():
    """Get or create a singleton instance of TravelCrewAI."""
    global _travel_crew_ai
    if _travel_crew_ai is None:
        _travel_crew_ai = TravelCrewAI()
    return _travel_crew_ai

def get_accommodation_options(location, check_in, check_out, guests=1, rooms=1):
    """
    Get accommodation options for a location and date range.
    
    Uses CrewAI to get real accommodation data. If that fails,
    generates realistic sample data as a fallback.
    
    Args:
        location (str): Destination city/area
        check_in (str): Check-in date in YYYY-MM-DD format
        check_out (str): Check-out date in YYYY-MM-DD format
        guests (int): Number of guests
        rooms (int): Number of rooms
        
    Returns:
        list: List of accommodation options with details
    """
    # Try to get real accommodation data using CrewAI
    try:
        crew_ai = _get_travel_crew_ai()
        accommodations = crew_ai.get_accommodation_options(
            location=location,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            rooms=rooms
        )
        
        # If we got valid results, return them
        if accommodations and len(accommodations) > 0:
            print(f"Retrieved {len(accommodations)} real accommodation options using CrewAI")
            return accommodations
            
    except Exception as e:
        print(f"Error getting real accommodation data: {e}")
    
    # If CrewAI fails or returns no results, generate sample data
    print("Using generated accommodation data as fallback")
    
    # Parse the dates
    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d") if isinstance(check_in, str) else check_in
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d") if isinstance(check_out, str) else check_out
    except:
        # Default to tomorrow and day after if dates can't be parsed
        check_in_date = datetime.now() + timedelta(days=1)
        check_out_date = check_in_date + timedelta(days=1)
    
    # Calculate number of nights
    nights = (check_out_date - check_in_date).days
    
    # Generate accommodation options based on location
    accommodations = []
    
    # Number of options to generate
    num_options = random.randint(10, 20)
    
    # Accommodation types with different probabilities based on location
    accommodation_types = ["Hotel", "Hostel", "Apartment", "Resort", "Guesthouse", "Vacation Rental"]
    
    # Common amenities
    all_amenities = [
        "WiFi", "Breakfast", "Pool", "Gym", "Air Conditioning", "Kitchen", 
        "Parking", "TV", "Washer/Dryer", "Elevator", "24-hour Front Desk",
        "Restaurant", "Bar", "Spa", "Room Service", "Airport Shuttle"
    ]
    
    # Generate names based on location
    location_adjectives = ["Grand", "Royal", "Central", "City", "Downtown", "Seaside", 
                          "Luxury", "Budget", "Cozy", "Modern", "Historic", "Premier"]
                          
    # Location-based words for property names
    location_words = {
        "Paris": ["Eiffel", "Seine", "Champs", "Montmartre", "Louvre"],
        "Rome": ["Vatican", "Colosseum", "Tiber", "Forum", "Trevi"],
        "New York": ["Manhattan", "Broadway", "Times Square", "Hudson", "Central Park"],
        "Tokyo": ["Shibuya", "Shinjuku", "Ginza", "Imperial", "Asakusa"],
        "London": ["Thames", "Westminster", "Kensington", "Piccadilly", "Hyde Park"],
    }
    
    # Get location-specific words or use general ones
    specific_words = []
    for loc in location_words:
        if loc.lower() in location.lower():
            specific_words = location_words[loc]
            break
    
    if not specific_words:
        specific_words = ["Plaza", "Inn", "Suites", "Residences", "Palace", "Lodge"]
    
    # Generate accommodations
    for _ in range(num_options):
        # Select a random type
        acc_type = random.choice(accommodation_types)
        
        # Generate a name
        adjective = random.choice(location_adjectives)
        word = random.choice(specific_words)
        
        # Different name formats based on type
        if acc_type == "Hotel":
            name = f"{adjective} {word} Hotel"
        elif acc_type == "Hostel":
            name = f"{word} {adjective} Hostel"
        elif acc_type == "Apartment":
            name = f"{adjective} {word} Apartments"
        elif acc_type == "Resort":
            name = f"{word} {adjective} Resort & Spa"
        elif acc_type == "Guesthouse":
            name = f"{adjective} {word} Guesthouse"
        else:  # Vacation Rental
            name = f"{adjective} {word} Vacation Home"
        
        # Generate a specific location within the destination
        neighborhoods = {
            "Paris": ["Montmartre", "Le Marais", "Saint-Germain", "Champs-Élysées", "Latin Quarter"],
            "Rome": ["Trastevere", "Monti", "Testaccio", "Prati", "Centro Storico"],
            "New York": ["Midtown", "SoHo", "Upper East Side", "Chelsea", "Greenwich Village"],
            "Tokyo": ["Shibuya", "Shinjuku", "Ginza", "Asakusa", "Roppongi"],
            "London": ["Covent Garden", "Notting Hill", "Soho", "Camden", "Kensington"],
        }
        
        area = "City Center"  # Default
        for loc in neighborhoods:
            if loc.lower() in location.lower():
                area = random.choice(neighborhoods[loc])
                break
        
        specific_location = f"{area}, {location}"
        
        # Generate a rating between 3.0 and 5.0
        rating = round(random.uniform(3.0, 5.0), 1)
        
        # Generate price based on type, rating, and random factor
        base_price = random.randint(30, 200)
        
        # Adjust for accommodation type
        type_multiplier = {
            "Hotel": 1.5,
            "Hostel": 0.6,
            "Apartment": 1.2,
            "Resort": 2.0,
            "Guesthouse": 0.9,
            "Vacation Rental": 1.3
        }.get(acc_type, 1.0)
        
        # Adjust for rating
        rating_multiplier = 0.7 + (rating / 5.0)
        
        # Calculate final price
        price_per_night = round(base_price * type_multiplier * rating_multiplier)
        
        # Make sure hostels have appropriate pricing
        if acc_type == "Hostel" and price_per_night > 50:
            price_per_night = random.randint(20, 50)
        
        # Select random amenities (more for higher ratings)
        num_amenities = int(rating) + random.randint(1, 5)
        amenities = random.sample(all_amenities, min(num_amenities, len(all_amenities)))
        
        # Create accommodation option
        accommodation = {
            "name": name,
            "type": acc_type,
            "location": specific_location,
            "rating": rating,
            "price_per_night": price_per_night,
            "amenities": amenities,
            "check_in": check_in_date.strftime("%Y-%m-%d"),
            "check_out": check_out_date.strftime("%Y-%m-%d"),
            "nights": nights,
            "guests": guests,
            "rooms": rooms
        }
        
        accommodations.append(accommodation)
    
    return accommodations

def filter_accommodations(accommodations, accommodation_type=None, amenities=None, max_price=None):
    """
    Filter accommodation options based on criteria.
    
    Args:
        accommodations (list): List of accommodation options
        accommodation_type (list): Filter by these accommodation types
        amenities (list): Must have these amenities
        max_price (float): Maximum price per night
        
    Returns:
        list: Filtered accommodation options
    """
    filtered = accommodations.copy()
    
    # Filter by type
    if accommodation_type:
        filtered = [a for a in filtered if a["type"] in accommodation_type]
    
    # Filter by amenities (must have all specified amenities)
    if amenities:
        filtered = [a for a in filtered if all(amenity in a["amenities"] for amenity in amenities)]
    
    # Filter by price
    if max_price is not None:
        filtered = [a for a in filtered if a["price_per_night"] <= max_price]
    
    # Sort by price (low to high)
    filtered.sort(key=lambda x: x["price_per_night"])
    
    return filtered
