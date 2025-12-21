"""
Flight data utilities for the trip planner application.
Handles fetching and processing flight information.
"""

import random
from datetime import datetime, timedelta
from tripadvisor.utils.crew_ai_agent import TravelCrewAI

# Initialize singleton instance of TravelCrewAI
_travel_crew_ai = None

def _get_travel_crew_ai():
    """Get or create a singleton instance of TravelCrewAI."""
    global _travel_crew_ai
    if _travel_crew_ai is None:
        _travel_crew_ai = TravelCrewAI()
    return _travel_crew_ai

def get_flight_options(origin, destination, date, flight_class="Economy", flexible_dates=False):
    """
    Get flight options from origin to destination on the specified date.
    
    Uses CrewAI to get real flight data. If that fails, generates realistic sample data.
    
    Args:
        origin (str): Departure city/airport
        destination (str): Arrival city/airport
        date (str): Departure date in YYYY-MM-DD format
        flight_class (str): Class of service (Economy, Premium Economy, Business, First)
        flexible_dates (bool): Whether to include options for nearby dates
        
    Returns:
        list: List of flight options with details
    """
    # Try to get real flight data using CrewAI
    try:
        crew_ai = _get_travel_crew_ai()
        flight_options = crew_ai.get_flight_options(
            origin=origin,
            destination=destination,
            date=date,
            flight_class=flight_class,
            flexible_dates=flexible_dates
        )
        
        # If we got valid results, return them
        if flight_options and len(flight_options) > 0:
            print(f"Retrieved {len(flight_options)} real flight options using CrewAI")
            return flight_options
        
    except Exception as e:
        print(f"Error getting real flight data: {e}")
    
    # If CrewAI fails or returns no results, generate sample data
    print("Using generated flight data as fallback")
    
    # Parse the date
    try:
        departure_date = datetime.strptime(date, "%Y-%m-%d")
    except:
        # If date is already a datetime object or in different format
        if isinstance(date, datetime):
            departure_date = date
        else:
            # Default to tomorrow if date can't be parsed
            departure_date = datetime.now() + timedelta(days=1)
    
    # Generate a list of airlines based on routes
    airlines = [
        "Delta Air Lines", "United Airlines", "American Airlines", 
        "Lufthansa", "British Airways", "Air France", "KLM",
        "Emirates", "Qatar Airways", "Singapore Airlines",
        "JetBlue", "Southwest", "Ryanair", "easyJet"
    ]
    
    # Generate flight options
    flight_options = []
    
    # Generate different date options if flexible_dates is True
    date_options = [departure_date]
    if flexible_dates:
        date_options.extend([
            departure_date - timedelta(days=1),
            departure_date - timedelta(days=2),
            departure_date + timedelta(days=1),
            departure_date + timedelta(days=2)
        ])
    
    for curr_date in date_options:
        # Number of flights to generate for this date
        num_flights = random.randint(5, 15)
        
        for _ in range(num_flights):
            # Select a random airline
            airline = random.choice(airlines)
            
            # Generate flight number
            flight_number = f"{airline[:2].upper()}{random.randint(100, 9999)}"
            
            # Generate departure and arrival times
            departure_hour = random.randint(0, 23)
            departure_minute = random.choice([0, 15, 30, 45])
            departure_time = f"{departure_hour:02d}:{departure_minute:02d}"
            
            # Random flight duration between 1 and 15 hours
            duration_hours = random.randint(1, 15)
            duration_minutes = random.choice([0, 15, 30, 45])
            
            # Calculate arrival time
            arrival_datetime = (
                curr_date + 
                timedelta(hours=departure_hour, minutes=departure_minute) + 
                timedelta(hours=duration_hours, minutes=duration_minutes)
            )
            arrival_time = arrival_datetime.strftime("%H:%M")
            
            # Format duration
            duration = f"{duration_hours}h {duration_minutes}m"
            
            # Determine number of stops
            stops = random.choice([0, 0, 0, 1, 1, 2])
            
            # Generate layover cities if there are stops
            layovers = []
            if stops > 0:
                layover_cities = ["Chicago", "Atlanta", "London", "Paris", "Dubai", 
                                 "Amsterdam", "Frankfurt", "Tokyo", "Toronto", "Singapore"]
                layovers = random.sample(layover_cities, stops)
            
            # Generate price based on class, stops, and random factor
            base_price = random.randint(150, 800)
            
            # Adjust price for flight class
            class_multiplier = {
                "Economy": 1.0,
                "Premium Economy": 1.5,
                "Business": 2.5,
                "First": 4.0
            }.get(flight_class, 1.0)
            
            # Adjust for stops (direct flights are more expensive)
            stops_discount = 1.0 - (stops * 0.1)
            
            final_price = base_price * class_multiplier * stops_discount
            
            # Create flight option
            flight = {
                "airline": airline,
                "flight_number": flight_number,
                "departure_date": curr_date.strftime("%Y-%m-%d"),
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": duration,
                "stops": stops,
                "layovers": layovers,
                "price": final_price,
                "class": flight_class,
                "origin": origin,
                "destination": destination
            }
            
            flight_options.append(flight)
    
    return flight_options

def filter_flights(flights, max_stops=None, sort_by="Price (Low to High)"):
    """
    Filter and sort flight options based on criteria.
    
    Args:
        flights (list): List of flight options
        max_stops (int): Maximum number of stops (None for any)
        sort_by (str): Sort criteria - "Price (Low to High)", "Duration (Shortest)", "Stops (Fewest)"
        
    Returns:
        list: Filtered and sorted flight options
    """
    # Filter by stops if specified
    if max_stops is not None:
        flights = [f for f in flights if f["stops"] <= max_stops]
    
    # Sort based on criteria
    if sort_by == "Price (Low to High)":
        flights.sort(key=lambda x: x["price"])
    elif sort_by == "Duration (Shortest)":
        # Convert duration string to minutes for sorting
        def duration_to_minutes(duration_str):
            parts = duration_str.split()
            hours = int(parts[0].replace("h", ""))
            minutes = int(parts[1].replace("m", "")) if len(parts) > 1 else 0
            return hours * 60 + minutes
        
        flights.sort(key=lambda x: duration_to_minutes(x["duration"]))
    elif sort_by == "Stops (Fewest)":
        flights.sort(key=lambda x: x["stops"])
    
    return flights
