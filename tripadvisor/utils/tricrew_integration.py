"""
Tricrew integration utilities for the trip planner application.
Handles personalized recommendations based on user preferences.
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

def get_tricrew_recommendations(trip_type, budget_level, destinations, num_travelers):
    """
    Get personalized trip recommendations from the Tricrew service.
    
    Uses CrewAI to get personalized recommendations. If that fails,
    generates realistic recommendations based on destination and preferences.
    
    Args:
        trip_type (list): Types of trip (Beach, City, etc.)
        budget_level (str): Budget level (Budget, Economy, etc.)
        destinations (list): List of destination objects
        num_travelers (int): Number of travelers
        
    Returns:
        list: Personalized recommendations for each destination
    """
    # Try to get real recommendations using CrewAI
    try:
        crew_ai = _get_travel_crew_ai()
        recommendations = crew_ai.get_tricrew_recommendations(
            trip_type=trip_type,
            budget_level=budget_level,
            destinations=destinations,
            num_travelers=num_travelers
        )
        
        # If we got valid results, return them
        if recommendations and len(recommendations) > 0:
            print(f"Retrieved personalized recommendations using CrewAI")
            return recommendations
            
    except Exception as e:
        print(f"Error getting personalized recommendations: {e}")
    
    # If CrewAI fails or returns no results, generate fallback recommendations
    print("Using generated recommendations as fallback")
    
    recommendations = []
    
    # Trip type preferences affect activity recommendations
    activity_by_trip_type = {
        "Beach": [
            "Snorkeling", "Surfing", "Beach Volleyball", "Sunset Watching", 
            "Beachside Yoga", "Jet Skiing", "Parasailing", "Beach Picnic"
        ],
        "City": [
            "Museum Tours", "Historical Walks", "Local Markets", "Food Tours",
            "Architecture Tours", "Shopping", "Theater Shows", "Cafe Hopping"
        ],
        "Mountains": [
            "Hiking", "Mountain Biking", "Scenic Drives", "Photography",
            "Skiing", "Snowboarding", "Wildlife Watching", "Camping"
        ],
        "Cultural": [
            "Museum Visits", "Historical Tours", "Local Workshops", "Traditional Performances",
            "Cooking Classes", "Local Festivals", "Temple/Church Visits", "Art Galleries"
        ],
        "Adventure": [
            "Zip-lining", "Rock Climbing", "White Water Rafting", "Skydiving",
            "Bungee Jumping", "Scuba Diving", "Paragliding", "Canyoning"
        ],
        "Relaxation": [
            "Spa Treatments", "Yoga Retreats", "Meditation Sessions", "Hot Springs",
            "Reading by the Pool", "Nature Walks", "Massage Therapy", "Scenic Picnics"
        ],
        "Food & Wine": [
            "Wine Tasting", "Cooking Classes", "Food Tours", "Farm Visits",
            "Market Tours", "Restaurant Hopping", "Brewery Tours", "Food Festivals"
        ]
    }
    
    # Budget level affects the recommendation types
    budget_tips = {
        "Budget": [
            "Look for free walking tours",
            "Stay in hostels or budget accommodations",
            "Use public transportation",
            "Eat at local street food vendors",
            "Visit free attractions and museums on discount days"
        ],
        "Economy": [
            "Consider mid-range hotels with good deals",
            "Mix restaurant dining with self-catering",
            "Look for city passes for attractions",
            "Use ride-sharing for longer trips",
            "Find happy hour specials for dining"
        ],
        "Standard": [
            "Book quality hotels in good locations",
            "Try mix of local and upscale restaurants",
            "Consider guided tours for convenience",
            "Use taxis for convenience when needed",
            "Book skip-the-line tickets for popular attractions"
        ],
        "Premium": [
            "Stay at luxury hotels with good amenities",
            "Dine at renowned restaurants",
            "Book private tours for personalized experiences",
            "Use private transfers for convenience",
            "Consider concierge services for reservations"
        ],
        "Luxury": [
            "Book 5-star accommodations with premium locations",
            "Dine at Michelin-starred restaurants",
            "Hire private guides for customized experiences",
            "Book private transportation throughout your trip",
            "Arrange VIP access to attractions and events"
        ]
    }
    
    # Destination-specific recommendations
    destination_specific = {
        "paris": {
            "activities": [
                "Visit the Eiffel Tower", "Explore the Louvre", "Stroll along the Seine", 
                "Visit Montmartre", "See Notre Dame Cathedral", "Shop on Champs-Élysées",
                "Visit the Catacombs", "Take a day trip to Versailles"
            ],
            "local_tips": "Paris is best explored on foot or using the Metro. Consider buying a Paris Museum Pass for significant savings on attractions.",
            "best_time": "April to June or September to October for mild weather and fewer tourists."
        },
        "rome": {
            "activities": [
                "Visit the Colosseum", "Explore the Vatican Museums", "See the Pantheon", 
                "Throw a coin in Trevi Fountain", "Walk through the Roman Forum",
                "Visit the Spanish Steps", "Explore Trastevere", "Try authentic Roman pizza"
            ],
            "local_tips": "Many museums in Rome are free on the first Sunday of the month. Carry a water bottle as you can refill it at Rome's many public fountains.",
            "best_time": "April to May or September to October for pleasant weather and fewer crowds."
        },
        "new york": {
            "activities": [
                "Visit Times Square", "Explore Central Park", "See the Statue of Liberty", 
                "Walk the High Line", "Visit the Metropolitan Museum of Art",
                "Experience Broadway", "Shop in SoHo", "Visit the 9/11 Memorial"
            ],
            "local_tips": "Buy a 7-day MetroCard for unlimited subway and bus rides. Many museums have 'pay what you wish' hours on certain days.",
            "best_time": "April to June or September to November for mild weather and cultural events."
        },
        "tokyo": {
            "activities": [
                "Visit Senso-ji Temple", "Explore Shibuya Crossing", "See the Imperial Palace", 
                "Shop in Ginza", "Visit Meiji Shrine", "Experience a Robot Restaurant",
                "Enjoy Ueno Park", "Take a day trip to Mount Fuji"
            ],
            "local_tips": "Purchase a PASMO or Suica card for easy travel on public transportation. Many restaurants have ticket machines outside where you order before entering.",
            "best_time": "March to May for cherry blossoms, or October to November for autumn colors."
        },
        "bangkok": {
            "activities": [
                "Visit the Grand Palace", "Explore Wat Pho", "Shop at Chatuchak Weekend Market", 
                "Take a boat tour on the Chao Phraya River", "Visit Jim Thompson House",
                "Experience Thai massage", "Try street food at Yaowarat (Chinatown)", "Visit Wat Arun"
            ],
            "local_tips": "Use the BTS Skytrain or MRT to avoid Bangkok's notorious traffic. Always negotiate prices for tuk-tuks before getting in.",
            "best_time": "November to February for cooler, drier weather."
        },
        "london": {
            "activities": [
                "Visit the British Museum", "See the Tower of London", "Watch the Changing of the Guard", 
                "Ride the London Eye", "Explore Camden Market", "Visit Westminster Abbey",
                "Walk across Tower Bridge", "See a West End show"
            ],
            "local_tips": "Get an Oyster card for public transportation. Many of London's best museums are free, including the British Museum and Tate Modern.",
            "best_time": "May to September for warmer weather and outdoor events."
        }
    }
    
    # Generate recommendations for each destination
    for dest in destinations:
        dest_name = dest["name"].lower()
        
        # Find matching destination-specific recommendations
        specific_rec = None
        for loc in destination_specific:
            if loc in dest_name:
                specific_rec = destination_specific[loc]
                break
        
        # If no specific match, create generic recommendations
        if not specific_rec:
            # Pick activities based on trip type preferences
            activities = []
            for trip_pref in trip_type:
                if trip_pref in activity_by_trip_type:
                    activities.extend(random.sample(activity_by_trip_type[trip_pref], 2))
            
            # If no activities selected or no valid trip type, add some defaults
            if not activities:
                activities = [
                    "Visit main tourist attractions", 
                    "Try local cuisine", 
                    "Take a walking tour", 
                    "Visit local markets",
                    "Take photos at scenic viewpoints"
                ]
            
            # Create generic recommendations
            specific_rec = {
                "activities": activities,
                "local_tips": "Research local transportation options before arriving. Try to learn a few basic phrases in the local language.",
                "best_time": "Research seasonal weather patterns for this destination to find the optimal time to visit."
            }
        
        # Get budget tips based on selected level
        budget_recommendation = random.choice(budget_tips.get(budget_level, budget_tips["Standard"]))
        
        # Adjust recommendations based on number of travelers
        group_tip = ""
        if num_travelers > 4:
            group_tip = "For large groups, consider booking private tours or transportation for convenience."
        elif num_travelers == 1:
            group_tip = "Solo travelers should consider staying at social accommodations like hostels to meet other travelers."
        elif num_travelers == 2:
            group_tip = "Couples can look for romantic dining options or special experiences."
        
        # Combine all recommendations
        recommendation = {
            "destination": dest["name"],
            "activities": specific_rec["activities"],
            "local_tips": specific_rec["local_tips"] + " " + budget_recommendation + " " + group_tip,
            "best_time": specific_rec["best_time"]
        }
        
        recommendations.append(recommendation)
    
    return recommendations
