"""
CrewAI integration for the trip planner application.
Handles fetching real-time data using AI agents.
"""

import os
from config.setting import *
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import json
import dotenv
dotenv.load_dotenv()
# Check for API key presence
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Warning: No OpenAI API key found. CrewAI functionality will be limited.")
    
# Configure OpenAI API for CrewAI
llm_model =  "gpt-3.5-turbo" if USE_LLM=='OPEN_AI' else "deepseek-chat"
llm = ChatOpenAI(
    model=llm_model,     # or "deepseek-coder"
    temperature=0.7,
)

class TravelCrewAI:
    """
    Implementation of CrewAI for travel planning and data retrieval.
    """
    
    def __init__(self):
        """Initialize the Travel Crew AI with necessary agents."""
        # Define the agents
        self.flight_agent = Agent(
            role="Flight Search Specialist",
            goal="Find the best and most accurate flight deals, show flights in low to high price. use skyscanner to list flights ",
            backstory="An expert in the airline industry with extensive knowledge of flight pricing, routes, and booking strategies.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.accommodation_agent = Agent(
            role="Accommodation Expert",
            goal="Find the best accommodation options based on traveler preferences",
            backstory="A seasoned travel consultant who has visited numerous hotels, hostels, and rental properties worldwide.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.local_expert_agent = Agent(
            role="Local Destination Expert",
            goal="Provide authentic insights about destinations",
            backstory="A worldly traveler who has lived in many countries and knows the local customs, food, and attractions.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.budget_agent = Agent(
            role="Travel Budget Analyst",
            goal="Create accurate cost estimates for travelers",
            backstory="A financial advisor specializing in travel budgeting with knowledge of costs across different countries.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def get_flight_options(self, origin, destination, date, flight_class="Economy", flexible_dates=False):
        """
        Get real flight options using CrewAI flight agent.
        
        Args:
            origin (str): Departure city/airport
            destination (str): Arrival city/airport
            date (str): Departure date in YYYY-MM-DD format
            flight_class (str): Class of service
            flexible_dates (bool): Whether to include options for nearby dates
            
        Returns:
            list: List of flight options with details
        """
        # Create the flight search task
        flight_task = Task(
            description=f"""
            Find real flight options from {origin} to {destination} on {date}.
            
            Please consider the following:
            - Flight class: {flight_class}
            - If flexible dates: {str(flexible_dates)}
            
            You need to return a JSON array with at least 5 flight options.
            Each flight should have:
            - airline (string): Airline name
            - flight_number (string): Flight number code
            - departure_date (string): Date in YYYY-MM-DD format
            - departure_time (string): Local time in HH:MM format
            - arrival_time (string): Local time in HH:MM format
            - duration (string): In the format "Xh Ym"
            - stops (number): Number of stops
            - layovers (array): Names of layover cities if any
            - price (number): Price in USD
            - class (string): Cabin class
            - origin (string): Origin city/airport
            - destination (string): Destination city/airport
            
            Return ONLY the valid JSON array with no prefix or explanation.
            """,
            agent=self.flight_agent,
            expected_output="A JSON array containing flight options"
        )
        
        # Create a crew with just the flight agent and execute
        crew = Crew(
            agents=[self.flight_agent],
            tasks=[flight_task],
            verbose=True,
            process=Process.sequential
        )
        
        try:
            result = crew.kickoff()
            # Parse the result as JSON
            try:
                # Strip any markdown code blocks if present
                clean_result = result.strip()
                if clean_result.startswith("```json"):
                    clean_result = clean_result.replace("```json", "", 1)
                if clean_result.startswith("```"):
                    clean_result = clean_result.replace("```", "", 1)
                if clean_result.endswith("```"):
                    clean_result = clean_result[:-3]
                
                flight_options = json.loads(clean_result.strip())
                return flight_options
            except json.JSONDecodeError as e:
                print(f"Error parsing flight results: {e}")
                # Return a default empty list
                return []
        except Exception as e:
            print(f"Error getting flight options: {e}")
            return []
    
    def get_accommodation_options(self, location, check_in, check_out, guests=1, rooms=1):
        """
        Get real accommodation options using CrewAI accommodation agent.
        
        Args:
            location (str): Destination city/area
            check_in (str): Check-in date in YYYY-MM-DD format
            check_out (str): Check-out date in YYYY-MM-DD format
            guests (int): Number of guests
            rooms (int): Number of rooms
            
        Returns:
            list: List of accommodation options with details
        """
        # Create the accommodation search task
        accommodation_task = Task(
            description=f"""
            Find real accommodation options in {location} for the following dates:
            - Check-in: {check_in}
            - Check-out: {check_out}
            - Number of guests: {guests}
            - Number of rooms: {rooms}
            
            You need to return a JSON array with at least 5 accommodation options.
            Each accommodation should have:
            - name (string): Property name
            - type (string): Type (Hotel, Hostel, Apartment, Resort, Guesthouse, Vacation Rental)
            - location (string): Specific area within the destination
            - rating (number): Rating from 1.0 to 5.0
            - price_per_night (number): Price per night in USD
            - amenities (array): Available amenities
            - check_in (string): Check-in date in YYYY-MM-DD format
            - check_out (string): Check-out date in YYYY-MM-DD format
            - nights (number): Number of nights
            - guests (number): Number of guests
            - rooms (number): Number of rooms
            
            Return ONLY the valid JSON array with no prefix or explanation.
            """,
            agent=self.accommodation_agent,
            expected_output="A JSON array containing accommodation options"
        )
        
        # Create a crew with just the accommodation agent and execute
        crew = Crew(
            agents=[self.accommodation_agent],
            tasks=[accommodation_task],
            verbose=True,
            process=Process.sequential
        )
        
        try:
            result = crew.kickoff()
            # Parse the result as JSON
            try:
                # Strip any markdown code blocks if present
                clean_result = result.strip()
                if clean_result.startswith("```json"):
                    clean_result = clean_result.replace("```json", "", 1)
                if clean_result.startswith("```"):
                    clean_result = clean_result.replace("```", "", 1)
                if clean_result.endswith("```"):
                    clean_result = clean_result[:-3]
                
                accommodation_options = json.loads(clean_result.strip())
                return accommodation_options
            except json.JSONDecodeError as e:
                print(f"Error parsing accommodation results: {e}")
                # Return a default empty list
                return []
        except Exception as e:
            print(f"Error getting accommodation options: {e}")
            return []
    
    def get_food_cost_estimates(self, location, duration, travelers=1, dining_style="Mixed", dietary_preferences=None):
        """
        Get real food cost estimates using CrewAI budget agent.
        
        Args:
            location (str): Destination city/area
            duration (int): Number of days
            travelers (int): Number of travelers
            dining_style (str): Dining preferences
            dietary_preferences (list): Special dietary needs
            
        Returns:
            dict: Food cost estimates and local cuisine information
        """
        dietary_prefs = "No specific preferences" if not dietary_preferences else ", ".join(dietary_preferences)
        
        # Create the food cost estimation task
        food_task = Task(
            description=f"""
            Provide realistic food cost estimates for {travelers} traveler(s) in {location} for {duration} days.
            
            Consider:
            - Dining style: {dining_style}
            - Dietary preferences: {dietary_prefs}
            
            You need to return a JSON object with:
            - breakfast_cost_per_day (number): Average cost per person in USD
            - lunch_cost_per_day (number): Average cost per person in USD
            - dinner_cost_per_day (number): Average cost per person in USD
            - snacks_cost_per_day (number): Average cost per person in USD
            - total_per_day_per_person (number): Sum of daily costs per person
            - total_for_trip (number): Total food cost for all travelers for the entire trip
            - location (string): The destination
            - duration (number): Trip duration in days
            - travelers (number): Number of travelers
            - dining_style (string): Chosen dining style
            
            Additionally, include a "local_cuisine" object with:
            - popular_dishes (array): List of popular local dishes
            - specialties (array): Local specialties and ingredients
            - dining_tips (string): Tips for dining in this location
            - recommended_restaurants (array): Each with "name" and "description"
            
            Return ONLY the valid JSON object with no prefix or explanation.
            """,
            agent=self.budget_agent,
            expected_output="A JSON object containing food cost estimates and local cuisine info"
        )
        
        # Create a crew with budget and local expert agents
        crew = Crew(
            agents=[self.budget_agent, self.local_expert_agent],
            tasks=[food_task],
            verbose=True,
            process=Process.sequential
        )
        
        try:
            result = crew.kickoff()
            # Parse the result as JSON
            try:
                # Strip any markdown code blocks if present
                clean_result = result.strip()
                if clean_result.startswith("```json"):
                    clean_result = clean_result.replace("```json", "", 1)
                if clean_result.startswith("```"):
                    clean_result = clean_result.replace("```", "", 1)
                if clean_result.endswith("```"):
                    clean_result = clean_result[:-3]
                
                food_cost_data = json.loads(clean_result.strip())
                return food_cost_data
            except json.JSONDecodeError as e:
                print(f"Error parsing food cost results: {e}")
                # Return a default empty dict
                return {}
        except Exception as e:
            print(f"Error getting food cost estimates: {e}")
            return {}
    
    def get_tricrew_recommendations(self, trip_type, budget_level, destinations, num_travelers):
        """
        Get personalized trip recommendations using CrewAI local expert.
        
        Args:
            trip_type (list): Types of trip (Beach, City, etc.)
            budget_level (str): Budget level (Budget, Economy, etc.)
            destinations (list): List of destination objects
            num_travelers (int): Number of travelers
            
        Returns:
            list: Personalized recommendations for each destination
        """
        # Convert destinations to a simple string format for the prompt
        dest_str = ", ".join([f"{d['name']} ({d['arrival_date']} to {d['departure_date']})" for d in destinations])
        trip_types_str = ", ".join(trip_type)
        
        # Create the recommendations task
        recommendations_task = Task(
            description=f"""
            Provide personalized travel recommendations for a trip with the following details:
            
            - Trip types: {trip_types_str}
            - Budget level: {budget_level}
            - Number of travelers: {num_travelers}
            - Destinations: {dest_str}
            
            For each destination, provide:
            
            1. A list of recommended activities tailored to the trip types and budget level
            2. Local tips for making the most of the visit
            3. The best time to visit (even if it doesn't match the planned dates)
            
            You need to return a JSON array with one object per destination.
            Each object should have:
            - destination (string): Destination name
            - activities (array): List of recommended activities
            - local_tips (string): Insider tips for the destination
            - best_time (string): Best time to visit
            
            Return ONLY the valid JSON array with no prefix or explanation.
            """,
            agent=self.local_expert_agent,
            expected_output="A JSON array containing personalized recommendations"
        )
        
        # Create a crew with just the local expert agent and execute
        crew = Crew(
            agents=[self.local_expert_agent],
            tasks=[recommendations_task],
            verbose=True,
            process=Process.sequential
        )
        
        try:
            result = crew.kickoff()
            # Parse the result as JSON
            try:
                # Strip any markdown code blocks if present
                clean_result = result.strip()
                if clean_result.startswith("```json"):
                    clean_result = clean_result.replace("```json", "", 1)
                if clean_result.startswith("```"):
                    clean_result = clean_result.replace("```", "", 1)
                if clean_result.endswith("```"):
                    clean_result = clean_result[:-3]
                
                recommendations = json.loads(clean_result.strip())
                return recommendations
            except json.JSONDecodeError as e:
                print(f"Error parsing recommendations results: {e}")
                # Return a default empty list
                return []
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []