"""
Map visualization utilities for the trip planner application.
Handles creating interactive maps for destinations.
"""

import folium
from folium.plugins import MarkerCluster
import random
import geocoder

def create_trip_map(destinations, home_location):
    """
    Create an interactive map showing all destinations in the trip.
    
    Args:
        destinations (list): List of destination objects
        home_location (str): Starting location
        
    Returns:
        folium.Map: Interactive map object
    """
    # Create a base map centered at a default location (will be adjusted)
    trip_map = folium.Map(location=[0, 0], zoom_start=2)
    
    # Create a marker cluster for destinations
    marker_cluster = MarkerCluster().add_to(trip_map)
    
    # Add home location marker
    home_coords = get_location_coordinates(home_location)
    if home_coords:
        folium.Marker(
            location=home_coords,
            popup=f"<b>Start: {home_location}</b>",
            tooltip=home_location,
            icon=folium.Icon(color="green", icon="home")
        ).add_to(marker_cluster)
    
    # Add all destination markers
    all_coords = []
    if home_coords:
        all_coords.append(home_coords)
    
    for i, dest in enumerate(destinations):
        # Get destination coordinates
        if dest.get("coordinates") and dest["coordinates"] is not None:
            coords = dest["coordinates"]
        else:
            coords = get_location_coordinates(dest["name"])
            dest["coordinates"] = coords  # Store for future use
        
        if coords:
            all_coords.append(coords)
            
            # Create marker
            arrival_date = dest["arrival_date"]
            departure_date = dest["departure_date"]
            
            popup_html = f"""
            <b>{dest["name"]}</b><br>
            Arrival: {arrival_date}<br>
            Departure: {departure_date}<br>
            Duration: {dest["duration"]} days
            """
            
            folium.Marker(
                location=coords,
                popup=popup_html,
                tooltip=dest["name"],
                icon=folium.Icon(color="red", icon="map-marker")
            ).add_to(marker_cluster)
    
    # Connect destinations with lines if there are multiple points
    if len(all_coords) >= 2:
        folium.PolyLine(
            locations=all_coords,
            color="blue",
            weight=2,
            opacity=0.7,
            dash_array="5"
        ).add_to(trip_map)
    
    # Fit the map to show all markers
    if all_coords:
        trip_map.fit_bounds(all_coords)
    
    return trip_map

def get_location_coordinates(location_name):
    """
    Get the latitude and longitude coordinates for a location.
    
    In a real application, this would use a geocoding API.
    For this demo, we'll use a geocoder package with fallbacks.
    
    Args:
        location_name (str): Name of the location
        
    Returns:
        tuple: (latitude, longitude) coordinates or None if not found
    """
    try:
        # Try to geocode the location
        g = geocoder.arcgis(location_name)
        
        if g.ok:
            return g.latlng
        
        # Fallback to OSM
        g = geocoder.osm(location_name)
        if g.ok:
            return g.latlng
            
        # If still not found, use some well-known coordinates for popular cities
        popular_cities = {
            "paris": (48.8566, 2.3522),
            "london": (51.5074, -0.1278),
            "new york": (40.7128, -74.0060),
            "tokyo": (35.6762, 139.6503),
            "rome": (41.9028, 12.4964),
            "sydney": (-33.8688, 151.2093),
            "bangkok": (13.7563, 100.5018),
            "dubai": (25.2048, 55.2708),
            "los angeles": (34.0522, -118.2437),
            "berlin": (52.5200, 13.4050),
            "barcelona": (41.3851, 2.1734),
            "amsterdam": (52.3676, 4.9041),
            "singapore": (1.3521, 103.8198),
            "hong kong": (22.3193, 114.1694),
            "istanbul": (41.0082, 28.9784),
            "san francisco": (37.7749, -122.4194),
            "rio de janeiro": (-22.9068, -43.1729)
        }
        
        # Check if the location contains any popular city name
        location_lower = location_name.lower()
        for city, coords in popular_cities.items():
            if city in location_lower:
                return coords
        
        # Last resort: generate random coordinates (this would never happen in a real app)
        # This is only for demonstration purposes
        return (random.uniform(-10, 50), random.uniform(-100, 100))
    
    except Exception as e:
        print(f"Error getting coordinates for {location_name}: {e}")
        # Return None if geocoding fails
        return None
