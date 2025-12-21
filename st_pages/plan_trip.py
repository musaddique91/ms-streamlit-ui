import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import plotly.express as px
from datetime import datetime, timedelta
import json

# Import utility modules
from tripadvisor.utils.flight_data import get_flight_options, filter_flights
from tripadvisor.utils.accommodation_data import get_accommodation_options, filter_accommodations
from tripadvisor.utils.food_data import get_food_cost_estimates
from tripadvisor.utils.tricrew_integration import get_tricrew_recommendations
from tripadvisor.utils.map_visualization import create_trip_map

# Set page configuration
def plan_trip():
    # Initialize session state variables if they don't exist
    if 'trip_destinations' not in st.session_state:
        st.session_state.trip_destinations = []
    if 'selected_flights' not in st.session_state:
        st.session_state.selected_flights = {}
    if 'selected_accommodations' not in st.session_state:
        st.session_state.selected_accommodations = {}
    if 'total_budget' not in st.session_state:
        st.session_state.total_budget = 0
    if 'food_costs' not in st.session_state:
        st.session_state.food_costs = {}
    if 'itinerary' not in st.session_state:
        st.session_state.itinerary = []

    # Header
    st.title("✈️ Travel & Trip Planner")
    st.markdown("Plan your perfect vacation with flight comparisons, accommodation options, and budget estimates.")

    # Main tabs
    tabs = st.tabs(["Trip Builder", "Flight Comparison", "Accommodations", "Food Costs", "Itinerary", "Budget Summary"])

    with tabs[0]:
        st.header("Build Your Trip")

        # Trip basics
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Trip Details")
            trip_name = st.text_input("Trip Name", "My Awesome Vacation")
            start_date = st.date_input("Start Date", datetime.now() + timedelta(days=30))
            end_date = st.date_input("End Date", datetime.now() + timedelta(days=37))

            # Validate dates
            if start_date >= end_date:
                st.error("End date must be after start date")

            num_travelers = st.number_input("Number of Travelers", min_value=1, max_value=10, value=1)

            # Currency selection
            currency = st.selectbox("Currency", ["USD", "EUR","AED", "INR"], index=3)

        with col2:
            st.subheader("Trip Preferences")
            trip_type = st.multiselect(
                "Trip Type",
                ["Beach", "City", "Mountains", "Cultural", "Adventure", "Relaxation", "Food & Wine"],
                ["Beach", "Cultural"]
            )

            budget_level = st.select_slider(
                "Budget Level",
                options=["Budget", "Economy", "Standard", "Premium", "Luxury"],
                value="Standard"
            )

            # Budget allocation
            st.write("Budget Allocation (%):")
            col1, col2, col3 = st.columns(3)
            with col1:
                flight_allocation = st.slider("Flights", 10, 60, 30)
            with col2:
                accommodation_allocation = st.slider("Accommodation", 10, 60, 40)
            with col3:
                food_allocation = st.slider("Food", 10, 60, 20)

            # Validate allocation percentages
            total_allocation = flight_allocation + accommodation_allocation + food_allocation
            if total_allocation != 100:
                st.warning(f"Budget allocation should total 100% (currently {total_allocation}%)")

        # Destination selection
        st.subheader("Destinations")

        # Home/Starting location
        home_location = st.text_input("Home/Starting Location", placeholder="Add your home or starting location")

        # Add destination form
        with st.form("add_destination_form"):
            st.write("Add a Destination to Your Trip")
            col1, col2, col3 = st.columns(3)

            with col1:
                destination = st.text_input("Destination City", placeholder="Add a destination city")

            with col2:
                arrival_date = st.date_input("Arrival Date", start_date)

            with col3:
                departure_date = st.date_input("Departure Date", min(end_date, start_date + timedelta(days=3)))

            # Check if dates are valid
            date_valid = arrival_date >= start_date and departure_date <= end_date and arrival_date < departure_date

            submitted = st.form_submit_button("Add Destination")

            if submitted:
                if not date_valid:
                    st.error("Invalid dates. Please ensure arrival and departure dates are within your trip timeframe.")
                else:
                    # Create destination object
                    new_destination = {
                        "name": destination,
                        "arrival_date": arrival_date.strftime("%Y-%m-%d"),
                        "departure_date": departure_date.strftime("%Y-%m-%d"),
                        "duration": (departure_date - arrival_date).days,
                        "coordinates": None  # Will be filled when we fetch recommendations
                    }

                    # Add to session state
                    st.session_state.trip_destinations.append(new_destination)
                    st.success(f"Added {destination} to your trip!")
                    st.rerun()

        # Display current destinations
        if st.session_state.trip_destinations:
            st.write("Your Trip Destinations:")

            for i, dest in enumerate(st.session_state.trip_destinations):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"**{dest['name']}**")
                with col2:
                    st.write(f"Arrival: {dest['arrival_date']}")
                with col3:
                    st.write(f"Departure: {dest['departure_date']}")
                with col4:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.trip_destinations.pop(i)
                        st.rerun()

            # Display map of destinations
            st.subheader("Trip Map")
            try:
                map_data = create_trip_map(st.session_state.trip_destinations, home_location)
                folium_static(map_data)
            except Exception as e:
                st.error(f"Error displaying map: {e}")

            # Get Tricrew recommendations
            if st.button("Get Personalized Recommendations"):
                with st.spinner("Getting recommendations from Tricrew..."):
                    try:
                        recommendations = get_tricrew_recommendations(
                            trip_type,
                            budget_level,
                            st.session_state.trip_destinations,
                            num_travelers
                        )

                        if recommendations:
                            st.success("Recommendations retrieved successfully!")
                            st.subheader("Personalized Recommendations")

                            for i, rec in enumerate(recommendations):
                                with st.expander(f"Recommendation for {rec['destination']}"):
                                    st.write(f"**Activities:** {', '.join(rec['activities'])}")
                                    st.write(f"**Local Tips:** {rec['local_tips']}")
                                    st.write(f"**Best Time to Visit:** {rec['best_time']}")
                        else:
                            st.warning("No recommendations available for your selections.")
                    except Exception as e:
                        st.error(f"Error getting recommendations: {e}")
        else:
            st.info("Add destinations to start planning your trip!")

    with tabs[1]:
        st.header("Flight Comparison")

        if not st.session_state.trip_destinations:
            st.warning("Please add destinations in the Trip Builder tab first.")
        else:
            # Flight search options
            st.subheader("Search Flight Options")

            col1, col2, col3 = st.columns(3)
            with col1:
                flight_class = st.selectbox("Flight Class", ["Economy", "Premium Economy", "Business", "First"], index=0)

            with col2:
                max_stops = st.selectbox("Maximum Stops", [0, 1, 2, "Any"], index=3)

            with col3:
                sort_by = st.selectbox("Sort By", ["Price (Low to High)", "Duration (Shortest)", "Stops (Fewest)"], index=0)

            # For each leg of the journey
            for i, dest in enumerate(st.session_state.trip_destinations):
                st.subheader(f"Flights for {dest['name']}")

                # Determine origin (home or previous destination)
                origin = home_location if i == 0 else st.session_state.trip_destinations[i-1]['name']

                # Flight search form
                with st.form(f"flight_search_{i}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**From:** {origin}")
                        st.write(f"**To:** {dest['name']}")

                    with col2:
                        st.write(f"**Date:** {dest['arrival_date']}")
                        flexible_dates = st.checkbox("Flexible dates (±2 days)", key=f"flex_{i}")

                    search_submitted = st.form_submit_button("Search Flights")

                # If search is submitted, fetch and display flight options
                if search_submitted or f"flights_{i}" in st.session_state:
                    with st.spinner("Searching for flights..."):
                        try:
                            # Get flight options
                            if f"flights_{i}" not in st.session_state:
                                flights = get_flight_options(
                                    origin=origin,
                                    destination=dest['name'],
                                    date=dest['arrival_date'],
                                    flight_class=flight_class,
                                    flexible_dates=flexible_dates
                                )
                                st.session_state[f"flights_{i}"] = flights
                            else:
                                flights = st.session_state[f"flights_{i}"]

                            # Filter flights
                            filtered_flights = filter_flights(
                                flights,
                                max_stops=max_stops if max_stops != "Any" else None,
                                sort_by=sort_by
                            )

                            # Display flights
                            if filtered_flights:
                                st.write(f"Found {len(filtered_flights)} flight options:")
                                for j, flight in enumerate(filtered_flights):
                                    with st.container():
                                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                                        with col1:
                                            st.write(f"**{flight['airline']}** ({flight['flight_number']})")
                                            st.write(f"{flight['departure_time']} → {flight['arrival_time']}")

                                            # Format layovers
                                            if flight['stops'] > 0:
                                                st.write(f"{flight['stops']} stop(s): {', '.join(flight['layovers'])}")
                                            else:
                                                st.write("Direct flight")

                                        with col2:
                                            st.write(f"**Duration:**")
                                            st.write(f"{flight['duration']}")

                                        with col3:
                                            st.write(f"**Price:**")
                                            st.write(f"${flight['price']:.2f}")

                                        with col4:
                                            if st.button("Select", key=f"select_flight_{i}_{j}"):
                                                st.session_state.selected_flights[i] = flight
                                                st.success(f"Selected flight for {dest['name']}!")
                                                st.rerun()

                                        st.markdown("---")
                            else:
                                st.warning("No flights found matching your criteria. Try adjusting filters.")
                        except Exception as e:
                            st.error(f"Error searching flights: {e}")

                # Show selected flight if any
                if i in st.session_state.selected_flights:
                    flight = st.session_state.selected_flights[i]
                    st.success(f"Selected Flight: {flight['airline']} {flight['flight_number']} - ${flight['price']:.2f}")

    with tabs[2]:
        st.header("Accommodation Options")

        if not st.session_state.trip_destinations:
            st.warning("Please add destinations in the Trip Builder tab first.")
        else:
            # Accommodation filter options
            st.subheader("Accommodation Preferences")

            col1, col2, col3 = st.columns(3)
            with col1:
                accommodation_type = st.multiselect(
                    "Accommodation Type",
                    ["Hotel", "Hostel", "Apartment", "Resort", "Guesthouse", "Vacation Rental"],
                    ["Hotel", "Apartment"]
                )

            with col2:
                amenities = st.multiselect(
                    "Must-Have Amenities",
                    ["WiFi", "Breakfast", "Pool", "Gym", "Air Conditioning", "Kitchen", "Parking"],
                    ["WiFi"]
                )

            with col3:
                max_price = st.slider("Maximum Price per Night ($)", 20, 1000, 200)

            # For each destination
            for i, dest in enumerate(st.session_state.trip_destinations):
                st.subheader(f"Accommodations in {dest['name']}")

                arrival_date = dest['arrival_date']
                departure_date = dest['departure_date']
                duration = dest['duration']

                # Accommodation search form
                with st.form(f"accommodation_search_{i}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Location:** {dest['name']}")
                        st.write(f"**Check-in:** {arrival_date}")
                        st.write(f"**Check-out:** {departure_date}")

                    with col2:
                        st.write(f"**Duration:** {duration} nights")
                        guest_count = st.number_input("Guests", min_value=1, value=num_travelers, key=f"guests_{i}")
                        room_count = st.number_input("Rooms", min_value=1, value=max(1, num_travelers//2), key=f"rooms_{i}")

                    search_submitted = st.form_submit_button("Search Accommodations")

                # If search is submitted, fetch and display accommodation options
                if search_submitted or f"accommodations_{i}" in st.session_state:
                    with st.spinner("Searching for accommodations..."):
                        try:
                            # Get accommodation options
                            if f"accommodations_{i}" not in st.session_state:
                                accommodations = get_accommodation_options(
                                    location=dest['name'],
                                    check_in=arrival_date,
                                    check_out=departure_date,
                                    guests=guest_count,
                                    rooms=room_count
                                )
                                st.session_state[f"accommodations_{i}"] = accommodations
                            else:
                                accommodations = st.session_state[f"accommodations_{i}"]

                            # Filter accommodations
                            filtered_accommodations = filter_accommodations(
                                accommodations,
                                accommodation_type=accommodation_type,
                                amenities=amenities,
                                max_price=max_price
                            )

                            # Display accommodations
                            if filtered_accommodations:
                                st.write(f"Found {len(filtered_accommodations)} accommodation options:")

                                for j, acc in enumerate(filtered_accommodations):
                                    with st.container():
                                        col1, col2, col3 = st.columns([3, 2, 1])

                                        with col1:
                                            st.write(f"**{acc['name']}** ({acc['type']})")
                                            st.write(f"{acc['location']} | Rating: {acc['rating']}/5")
                                            st.write(f"Amenities: {', '.join(acc['amenities'][:5])}")

                                        with col2:
                                            st.write(f"**Price per night:** ${acc['price_per_night']:.2f}")
                                            st.write(f"**Total for {duration} nights:** ${acc['price_per_night'] * duration:.2f}")

                                        with col3:
                                            if st.button("Select", key=f"select_acc_{i}_{j}"):
                                                acc['total_price'] = acc['price_per_night'] * duration
                                                st.session_state.selected_accommodations[i] = acc
                                                st.success(f"Selected accommodation for {dest['name']}!")
                                                st.rerun()

                                        st.markdown("---")
                            else:
                                st.warning("No accommodations found matching your criteria. Try adjusting filters.")
                        except Exception as e:
                            st.error(f"Error searching accommodations: {e}")

                # Show selected accommodation if any
                if i in st.session_state.selected_accommodations:
                    acc = st.session_state.selected_accommodations[i]
                    st.success(f"Selected Accommodation: {acc['name']} - ${acc['total_price']:.2f} total")

    with tabs[3]:
        st.header("Food Cost Estimates")

        if not st.session_state.trip_destinations:
            st.warning("Please add destinations in the Trip Builder tab first.")
        else:
            st.subheader("Food Preferences")

            col1, col2 = st.columns(2)
            with col1:
                dining_style = st.select_slider(
                    "Dining Style",
                    options=["Budget (Street Food/Self-Catering)",
                             "Mixed (Some Restaurants, Some Self-Catering)",
                             "Standard (Mostly Restaurants)",
                             "Premium (High-end Dining)"],
                    value="Mixed (Some Restaurants, Some Self-Catering)"
                )

            with col2:
                dietary_preferences = st.multiselect(
                    "Dietary Preferences",
                    ["No Restrictions", "Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher"],
                    ["No Restrictions"]
                )

            # Calculate and display food costs for each destination
            for i, dest in enumerate(st.session_state.trip_destinations):
                st.subheader(f"Food Costs in {dest['name']}")

                # Calculate duration
                duration = dest['duration']

                # Get food cost estimates if not already fetched
                if dest['name'] not in st.session_state.food_costs:
                    with st.spinner(f"Getting food cost estimates for {dest['name']}..."):
                        try:
                            food_costs = get_food_cost_estimates(
                                location=dest['name'],
                                duration=duration,
                                travelers=num_travelers,
                                dining_style=dining_style,
                                dietary_preferences=dietary_preferences
                            )
                            st.session_state.food_costs[dest['name']] = food_costs
                        except Exception as e:
                            st.error(f"Error getting food cost estimates: {e}")
                            continue

                food_costs = st.session_state.food_costs[dest['name']]

                # Display food costs
                col1, col2 = st.columns(2)

                with col1:
                    st.write("### Daily Costs")
                    st.write(f"**Breakfast:** ${food_costs['breakfast_cost_per_day']:.2f} per person")
                    st.write(f"**Lunch:** ${food_costs['lunch_cost_per_day']:.2f} per person")
                    st.write(f"**Dinner:** ${food_costs['dinner_cost_per_day']:.2f} per person")
                    st.write(f"**Snacks/Drinks:** ${food_costs['snacks_cost_per_day']:.2f} per person")

                    daily_total = (
                        food_costs['breakfast_cost_per_day'] +
                        food_costs['lunch_cost_per_day'] +
                        food_costs['dinner_cost_per_day'] +
                        food_costs['snacks_cost_per_day']
                    )

                    st.write(f"**Daily Total:** ${daily_total:.2f} per person")
                    st.write(f"**Group Daily Total:** ${daily_total * num_travelers:.2f} for {num_travelers} travelers")

                with col2:
                    st.write("### Total Food Costs")
                    total_food_cost = daily_total * duration * num_travelers
                    st.write(f"**Total for {duration} days:** ${total_food_cost:.2f}")

                    # Create a pie chart of food cost breakdown
                    categories = ['Breakfast', 'Lunch', 'Dinner', 'Snacks/Drinks']
                    values = [
                        food_costs['breakfast_cost_per_day'] * duration * num_travelers,
                        food_costs['lunch_cost_per_day'] * duration * num_travelers,
                        food_costs['dinner_cost_per_day'] * duration * num_travelers,
                        food_costs['snacks_cost_per_day'] * duration * num_travelers
                    ]

                    fig = px.pie(
                        values=values,
                        names=categories,
                        title=f"Food Cost Breakdown for {dest['name']}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Local cuisine information
                st.subheader("Local Cuisine Information")
                if 'local_cuisine' in food_costs:
                    with st.expander("See Local Cuisine Details"):
                        st.write(f"**Popular Dishes:** {', '.join(food_costs['local_cuisine']['popular_dishes'])}")
                        st.write(f"**Local Specialties:** {', '.join(food_costs['local_cuisine']['specialties'])}")
                        st.write(f"**Dining Tips:** {food_costs['local_cuisine']['dining_tips']}")

                        if 'recommended_restaurants' in food_costs['local_cuisine']:
                            st.write("**Recommended Restaurants:**")
                            for restaurant in food_costs['local_cuisine']['recommended_restaurants']:
                                st.write(f"- {restaurant['name']}: {restaurant['description']}")
                else:
                    st.info("Local cuisine information not available for this destination.")

                st.markdown("---")

    with tabs[4]:
        st.header("Travel Itinerary")

        if not st.session_state.trip_destinations:
            st.warning("Please add destinations in the Trip Builder tab first.")
        else:
            st.subheader("Build Your Itinerary")

            # For each destination
            for i, dest in enumerate(st.session_state.trip_destinations):
                st.subheader(f"Itinerary for {dest['name']}")

                # Calculate duration
                duration = dest['duration']
                arrival_date = datetime.strptime(dest['arrival_date'], "%Y-%m-%d")

                # Create day-by-day itinerary
                for day in range(1, duration + 1):
                    current_date = arrival_date + timedelta(days=day-1)
                    date_str = current_date.strftime("%Y-%m-%d")
                    day_name = current_date.strftime("%A")

                    with st.expander(f"Day {day} - {day_name} ({date_str})"):
                        # Check if itinerary exists for this day
                        day_key = f"{dest['name']}_{date_str}"

                        if day_key not in st.session_state.itinerary:
                            st.session_state.itinerary.append(day_key)
                            st.session_state[day_key] = {
                                "morning": "",
                                "afternoon": "",
                                "evening": "",
                                "notes": ""
                            }

                        # Morning activities
                        st.write("### Morning")
                        morning_activity = st.text_area(
                            "Morning Activities",
                            st.session_state[day_key]["morning"],
                            key=f"morning_{day_key}"
                        )
                        st.session_state[day_key]["morning"] = morning_activity

                        # Afternoon activities
                        st.write("### Afternoon")
                        afternoon_activity = st.text_area(
                            "Afternoon Activities",
                            st.session_state[day_key]["afternoon"],
                            key=f"afternoon_{day_key}"
                        )
                        st.session_state[day_key]["afternoon"] = afternoon_activity

                        # Evening activities
                        st.write("### Evening")
                        evening_activity = st.text_area(
                            "Evening Activities",
                            st.session_state[day_key]["evening"],
                            key=f"evening_{day_key}"
                        )
                        st.session_state[day_key]["evening"] = evening_activity

                        # Notes
                        st.write("### Notes")
                        notes = st.text_area(
                            "Additional Notes",
                            st.session_state[day_key]["notes"],
                            key=f"notes_{day_key}"
                        )
                        st.session_state[day_key]["notes"] = notes

                # Add suggestions from Tricrew if available
                if st.button("Get Activity Suggestions", key=f"suggest_{i}"):
                    with st.spinner("Getting activity suggestions from Tricrew..."):
                        try:
                            recommendations = get_tricrew_recommendations(
                                trip_type=["Cultural", "Adventure"],  # Default if not specified
                                budget_level=budget_level,
                                destinations=[dest],
                                num_travelers=num_travelers
                            )

                            if recommendations and len(recommendations) > 0:
                                rec = recommendations[0]  # Get first recommendation

                                st.success("Here are some suggested activities:")
                                st.write(f"**Suggested Activities:** {', '.join(rec['activities'])}")
                                st.write(f"**Local Tips:** {rec['local_tips']}")

                                # Offer to add these to itinerary
                                if st.button("Add these to my itinerary"):
                                    # Add to first day's morning as an example
                                    first_day_key = f"{dest['name']}_{arrival_date.strftime('%Y-%m-%d')}"
                                    if first_day_key in st.session_state:
                                        st.session_state[first_day_key]["morning"] = f"Suggested activities: {', '.join(rec['activities'][:2])}"
                                        st.session_state[first_day_key]["notes"] = f"Local Tips: {rec['local_tips']}"
                                        st.success("Added suggestions to your first day in this destination!")
                                        st.rerun()
                            else:
                                st.warning("No recommendations available for this destination.")
                        except Exception as e:
                            st.error(f"Error getting suggestions: {e}")

                st.markdown("---")

            # Download itinerary option
            if st.button("Generate Downloadable Itinerary"):
                # Create a simple itinerary document
                itinerary_data = {
                    "trip_name": trip_name,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "destinations": st.session_state.trip_destinations,
                    "daily_plans": {}
                }

                # Add daily plans
                for day_key in st.session_state.itinerary:
                    if day_key in st.session_state:
                        itinerary_data["daily_plans"][day_key] = st.session_state[day_key]

                # Convert to JSON for download
                itinerary_json = json.dumps(itinerary_data, indent=2)

                # Provide download link
                st.download_button(
                    label="Download Itinerary (JSON)",
                    data=itinerary_json,
                    file_name=f"{trip_name.replace(' ', '_')}_itinerary.json",
                    mime="application/json"
                )

    with tabs[5]:
        st.header("Budget Summary")

        if not st.session_state.trip_destinations:
            st.warning("Please add destinations in the Trip Builder tab first.")
        else:
            st.subheader("Trip Budget Breakdown")

            # Calculate total flight costs
            flight_costs = 0
            for i, flight in st.session_state.selected_flights.items():
                flight_costs += flight["price"]

            # Calculate total accommodation costs
            accommodation_costs = 0
            for i, acc in st.session_state.selected_accommodations.items():
                accommodation_costs += acc["total_price"]

            # Calculate total food costs
            food_costs = 0
            for dest_name in st.session_state.food_costs:
                food_data = st.session_state.food_costs[dest_name]
                # Find the destination object to get duration
                for dest in st.session_state.trip_destinations:
                    if dest["name"] == dest_name:
                        duration = dest["duration"]
                        daily_food_cost = (
                            food_data['breakfast_cost_per_day'] +
                            food_data['lunch_cost_per_day'] +
                            food_data['dinner_cost_per_day'] +
                            food_data['snacks_cost_per_day']
                        )
                        food_costs += daily_food_cost * duration * num_travelers
                        break

            # Calculate total cost
            total_cost = flight_costs + accommodation_costs + food_costs

            # Display summary
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Cost Categories")
                st.metric("Flights", f"${flight_costs:.2f}")
                st.metric("Accommodations", f"${accommodation_costs:.2f}")
                st.metric("Food", f"${food_costs:.2f}")
                st.metric("Total Trip Cost", f"${total_cost:.2f}")

                # Per person cost
                if num_travelers > 1:
                    st.metric("Cost Per Person", f"${total_cost / num_travelers:.2f}")

            with col2:
                # Create a budget pie chart
                categories = ['Flights', 'Accommodations', 'Food']
                values = [flight_costs, accommodation_costs, food_costs]

                fig = px.pie(
                    values=values,
                    names=categories,
                    title="Budget Breakdown"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Comparison with allocation
            st.subheader("Budget Allocation vs. Actual Spending")

            # Calculate actual percentages
            actual_flight_pct = (flight_costs / total_cost * 100) if total_cost > 0 else 0
            actual_accommodation_pct = (accommodation_costs / total_cost * 100) if total_cost > 0 else 0
            actual_food_pct = (food_costs / total_cost * 100) if total_cost > 0 else 0

            # Create a comparison table
            comparison_data = {
                "Category": ["Flights", "Accommodations", "Food"],
                "Planned Allocation (%)": [flight_allocation, accommodation_allocation, food_allocation],
                "Actual Spending (%)": [actual_flight_pct, actual_accommodation_pct, actual_food_pct],
                "Difference (%)": [
                    actual_flight_pct - flight_allocation,
                    actual_accommodation_pct - accommodation_allocation,
                    actual_food_pct - food_allocation
                ]
            }

            comparison_df = pd.DataFrame(comparison_data)
            st.table(comparison_df.round(2))

            # Display a bar chart for the comparison
            fig = px.bar(
                comparison_df,
                x="Category",
                y=["Planned Allocation (%)", "Actual Spending (%)"],
                barmode="group",
                title="Budget Allocation vs. Actual Spending"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Budget recommendations
            st.subheader("Budget Recommendations")

            # Analyze the budget and provide recommendations
            recommendations = []

            if actual_flight_pct > flight_allocation + 10:
                recommendations.append("Your flight costs are significantly higher than planned. Consider looking for budget airlines or booking further in advance.")

            if actual_accommodation_pct > accommodation_allocation + 10:
                recommendations.append("Accommodation costs are exceeding your allocation. Consider alternative accommodation types or less expensive areas.")

            if actual_food_pct > food_allocation + 10:
                recommendations.append("Food costs are higher than planned. Consider more self-catering or local food options to reduce costs.")

            if not recommendations:
                recommendations.append("Your budget allocations are well balanced with your actual spending. Great job planning!")

            for rec in recommendations:
                st.info(rec)

            # Save or update the budget
            if st.button("Save Budget"):
                st.session_state.total_budget = total_cost
                st.success("Budget saved successfully!")
