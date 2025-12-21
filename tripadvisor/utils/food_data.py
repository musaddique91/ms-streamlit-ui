"""
Food cost estimation utilities for the trip planner application.
Handles generating food cost estimates for different destinations.
"""

import random
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

def get_food_cost_estimates(location, duration, travelers=1, dining_style="Mixed (Some Restaurants, Some Self-Catering)", dietary_preferences=None):
    """
    Get food cost estimates for a location.
    
    Uses CrewAI to get real food cost estimates. If that fails,
    generates estimates based on location cost factors.
    
    Args:
        location (str): Destination city/area
        duration (int): Number of days
        travelers (int): Number of travelers
        dining_style (str): Dining preferences (Budget, Mixed, Standard, Premium)
        dietary_preferences (list): Special dietary needs
        
    Returns:
        dict: Food cost estimates and local cuisine information
    """
    # Try to get real food cost data using CrewAI
    try:
        crew_ai = _get_travel_crew_ai()
        food_costs = crew_ai.get_food_cost_estimates(
            location=location,
            duration=duration,
            travelers=travelers,
            dining_style=dining_style,
            dietary_preferences=dietary_preferences
        )
        
        # If we got valid results, return them
        if food_costs and "breakfast_cost_per_day" in food_costs:
            print(f"Retrieved real food cost data for {location} using CrewAI")
            return food_costs
            
    except Exception as e:
        print(f"Error getting real food cost data: {e}")
    
    # If CrewAI fails or returns no results, generate estimates
    print("Using generated food cost data as fallback")
    
    # Base costs for different meal types (in USD)
    base_costs = {
        "Budget (Street Food/Self-Catering)": {
            "breakfast": 3,
            "lunch": 5,
            "dinner": 8,
            "snacks": 3
        },
        "Mixed (Some Restaurants, Some Self-Catering)": {
            "breakfast": 5,
            "lunch": 10,
            "dinner": 15,
            "snacks": 5
        },
        "Standard (Mostly Restaurants)": {
            "breakfast": 8,
            "lunch": 15,
            "dinner": 25,
            "snacks": 8
        },
        "Premium (High-end Dining)": {
            "breakfast": 15,
            "lunch": 30,
            "dinner": 60,
            "snacks": 15
        }
    }
    
    # Location cost multipliers (relative to US average)
    location_multipliers = {
        "new york": 1.5,
        "los angeles": 1.3,
        "chicago": 1.2,
        "san francisco": 1.6,
        "miami": 1.3,
        "london": 1.4,
        "paris": 1.3,
        "rome": 1.1,
        "barcelona": 1.0,
        "berlin": 0.9,
        "amsterdam": 1.2,
        "tokyo": 1.3,
        "kyoto": 1.2,
        "bangkok": 0.5,
        "singapore": 1.1,
        "hong kong": 1.3,
        "sydney": 1.2,
        "melbourne": 1.1,
        "cairo": 0.4,
        "dubai": 1.2,
        "delhi": 0.3,
        "mumbai": 0.4,
        "mexico city": 0.5,
        "rio de janeiro": 0.7,
        "sao paulo": 0.8,
        "toronto": 1.1,
        "vancouver": 1.2,
    }
    
    # Find the appropriate multiplier for the location
    multiplier = 1.0  # Default
    location_lower = location.lower()
    
    for loc in location_multipliers:
        if loc in location_lower:
            multiplier = location_multipliers[loc]
            break
    
    # Get base costs for the selected dining style
    dining_costs = base_costs.get(dining_style, base_costs["Mixed (Some Restaurants, Some Self-Catering)"])
    
    # Adjust costs based on location
    breakfast_cost = dining_costs["breakfast"] * multiplier
    lunch_cost = dining_costs["lunch"] * multiplier
    dinner_cost = dining_costs["dinner"] * multiplier
    snacks_cost = dining_costs["snacks"] * multiplier
    
    # Adjust for dietary preferences (if any)
    if dietary_preferences and "No Restrictions" not in dietary_preferences:
        # Special diets might increase costs
        dietary_multiplier = 1.1  # 10% increase for special dietary needs
        breakfast_cost *= dietary_multiplier
        lunch_cost *= dietary_multiplier
        dinner_cost *= dietary_multiplier
        snacks_cost *= dietary_multiplier
    
    # Local cuisine information (for selected destinations)
    local_cuisine = get_local_cuisine_info(location)
    
    # Return the cost estimates
    return {
        "breakfast_cost_per_day": breakfast_cost,
        "lunch_cost_per_day": lunch_cost,
        "dinner_cost_per_day": dinner_cost,
        "snacks_cost_per_day": snacks_cost,
        "total_per_day_per_person": breakfast_cost + lunch_cost + dinner_cost + snacks_cost,
        "total_for_trip": (breakfast_cost + lunch_cost + dinner_cost + snacks_cost) * duration * travelers,
        "location": location,
        "duration": duration,
        "travelers": travelers,
        "dining_style": dining_style,
        "local_cuisine": local_cuisine
    }

def get_local_cuisine_info(location):
    """
    Get information about local cuisine for a destination.
    
    Args:
        location (str): Destination city/area
        
    Returns:
        dict: Information about local cuisine
    """
    # Local cuisine information for popular destinations
    cuisine_info = {
        "paris": {
            "popular_dishes": ["Croissants", "Coq au Vin", "Beef Bourguignon", "Ratatouille", "Crème Brûlée"],
            "specialties": ["French Pastries", "Cheese", "Wine", "Escargot"],
            "dining_tips": "In Paris, service is typically included in the bill. Many restaurants offer fixed-price menus (prix fixe) which are good value.",
            "recommended_restaurants": [
                {"name": "Le Comptoir", "description": "Classic French bistro with seasonal menu"},
                {"name": "L'As du Fallafel", "description": "Famous falafel in the Marais district"},
                {"name": "Café de Flore", "description": "Historic café known for people watching"}
            ]
        },
        "rome": {
            "popular_dishes": ["Pasta Carbonara", "Cacio e Pepe", "Pizza al Taglio", "Saltimbocca", "Gelato"],
            "specialties": ["Roman Artichokes", "Supplì", "Espresso", "Tiramisu"],
            "dining_tips": "Romans usually eat dinner after 8 PM. Avoid restaurants with menus in multiple languages near tourist sites.",
            "recommended_restaurants": [
                {"name": "Da Enzo", "description": "Authentic Roman cuisine in Trastevere"},
                {"name": "Pizzarium", "description": "Gourmet pizza by the slice"},
                {"name": "Armando al Pantheon", "description": "Classic Roman dishes near the Pantheon"}
            ]
        },
        "tokyo": {
            "popular_dishes": ["Sushi", "Ramen", "Tempura", "Yakitori", "Udon"],
            "specialties": ["Wagyu Beef", "Matcha Desserts", "Sake", "Okonomiyaki"],
            "dining_tips": "Tipping is not customary in Japan. Many restaurants have plastic food displays outside to show their menu items.",
            "recommended_restaurants": [
                {"name": "Sushi Dai", "description": "Famous sushi restaurant at Tsukiji Outer Market"},
                {"name": "Ichiran", "description": "Popular ramen chain with individual booths"},
                {"name": "Gonpachi", "description": "Inspiration for the 'Kill Bill' restaurant scene"}
            ]
        },
        "new york": {
            "popular_dishes": ["Pizza", "Bagels", "Pastrami Sandwich", "Cheesecake", "Hot Dogs"],
            "specialties": ["Deli Sandwiches", "Cronuts", "Craft Beer", "Food Truck Cuisine"],
            "dining_tips": "Tipping 15-20% is expected. Many restaurants have a no-reservation policy, so expect to wait during peak hours.",
            "recommended_restaurants": [
                {"name": "Katz's Delicatessen", "description": "Iconic deli famous for pastrami"},
                {"name": "Joe's Pizza", "description": "Classic New York slice shop"},
                {"name": "Shake Shack", "description": "Popular burger chain that started in NYC"}
            ]
        },
        "bangkok": {
            "popular_dishes": ["Pad Thai", "Tom Yum Goong", "Green Curry", "Mango Sticky Rice", "Som Tam"],
            "specialties": ["Street Food", "Durian", "Thai Iced Tea", "Satay"],
            "dining_tips": "Street food is often the best food in Bangkok. Look for stalls with lots of locals.",
            "recommended_restaurants": [
                {"name": "Jay Fai", "description": "Michelin-starred street food"},
                {"name": "Thip Samai", "description": "Famous for Pad Thai"},
                {"name": "Gaggan", "description": "Progressive Indian cuisine"}
            ]
        }
    }
    
    # Find matching cuisine info
    location_lower = location.lower()
    
    for loc in cuisine_info:
        if loc in location_lower:
            return cuisine_info[loc]
    
    # If no specific info, return generic info
    return {
        "popular_dishes": ["Local Specialties", "Regional Cuisine", "Traditional Dishes"],
        "specialties": ["Local Ingredients", "Cultural Dishes", "Seasonal Food"],
        "dining_tips": "Try to eat where locals eat for authentic cuisine. Ask hotel staff for recommendations.",
        "recommended_restaurants": [
            {"name": "Local recommendation", "description": "Ask locals for the best places to eat"}
        ]
    }
