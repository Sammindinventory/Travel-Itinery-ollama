import streamlit as st
from crewai import Crew
from tasks import (
    intent_mapping_task,
    finding_recommendations_task,
    creating_itinerary_task
)
from agents import (
    intent_mapper_agent,
    finder_agent,
    itinerary_maker_agent,
)

# Initialize Streamlit app
st.title('Travel Planner with MindInventory')

# Initialize session state to store user inputs
if 'first_result' not in st.session_state:
    st.session_state.first_result = ""

if 'user_query' not in st.session_state:
    st.session_state.user_query = ""

if 'user_selected_stay' not in st.session_state:
    st.session_state.user_selected_stay = ""

if 'second_result' not in st.session_state:
    st.session_state.second_result = ""

if 'days' not in st.session_state:
    st.session_state.days = ""

# User input for the travel query
st.session_state.user_query = st.text_input('Enter your travel query (e.g., "Ahmedabad to Los Angeles for 5 days"):',
                                            key='travel_query_input')

# Add fields for additional user information
current_location = st.text_input('Enter your current location (e.g., "Ahmedabad"):', key='current_location')
destination_location = st.text_input('Enter your destination location (e.g., "Los Angeles"):',
                                     key='destination_location')
location_description = st.text_area('Enter a brief description of your destination:', key='location_description')
check_in_date = st.date_input('Enter your check-in date:', key='check_in_date')
check_out_date = st.date_input('Enter your check-out date:', key='check_out_date')
amenities = st.multiselect('Select amenities you want (e.g., "Pool", "Gym", etc.):',
                           ['Pool', 'Gym', 'Free WiFi', 'Parking', 'Restaurant', 'Spa'], key='amenities')
stay_type = st.selectbox('Select your preferred stay type:', ['Hotel', 'Airbnb', 'Hostel', 'Guesthouse'],
                         key='stay_type')
stay_budget = st.number_input('Enter your stay budget (in USD):', min_value=0, step=10, key='stay_budget')

# Handle the first agent call (intent mapping & recommendations finding)
if st.button('Submit Query', key='submit_query'):
    if st.session_state.user_query:
        st.write("Running Crew AI to map intent and find recommendations...")

        # Prepare the query with all necessary fields
        user_search_query = {
            'user_query': st.session_state.user_query,
            'current_location': current_location,
            'destination_location': destination_location,
            'location_description': location_description,
            'check_in_date': str(check_in_date),
            'check_out_date': str(check_out_date),
            'amenities': amenities,
            'stay_type': stay_type,
            'stay_budget': stay_budget
        }

        # Initialize Crew for intent mapping and finding recommendations
        first_crew = Crew(
            agents=[intent_mapper_agent, finder_agent],
            tasks=[intent_mapping_task, finding_recommendations_task],
            verbose=True
        )

        # Process the query through Crew
        first_result = first_crew.kickoff(inputs=user_search_query)

        # Store the result in session state
        st.session_state.first_result = first_result

        # Display the results (assumed as a JSON or a string that needs rendering)
        st.write("Recommendations found based on your query:")
        st.markdown(st.session_state.first_result)

    else:
        st.write("Please enter a valid travel query.")

# Display recommendation options and prompt for stay selection
if st.session_state.first_result:
    st.write("Select your preferred stay from the recommendations:")
    st.session_state.user_selected_stay = st.text_input(
        'Enter the name of your preferred stay (from the recommendations above):', key='stay_input')

    # Ask for the number of days for the trip (with default value set to 2)
    st.session_state.days = st.number_input('Enter the number of days for your trip:', min_value=1, max_value=14,
                                            value=2, key='stay_days')

    if st.button('Get Itinerary', key='get_itinerary'):
        if st.session_state.user_selected_stay and st.session_state.days:
            # Prepare input for the second agent (itinerary generation)
            second_crew_input = {
                'user_selected_stay': st.session_state.user_selected_stay,
                'days': st.session_state.days,
                'current_location': current_location,
                'destination_location': destination_location,
                'location_description': location_description,
                'check_in_date': str(check_in_date),
                'check_out_date': str(check_out_date),
                'amenities': amenities,
                'stay_type': stay_type,
                'stay_budget': stay_budget
            }

            # Initialize Crew for itinerary creation
            second_crew = Crew(
                agents=[itinerary_maker_agent],
                tasks=[creating_itinerary_task],
                verbose=True
            )

            # Execute the second crew to generate the itinerary
            second_result = second_crew.kickoff(inputs=second_crew_input)

            # Store the second result in session state
            st.session_state.second_result = second_result

        else:
            st.write("Please make sure you have entered a preferred stay and the number of days.")

# Display the itinerary result if available
if st.session_state.second_result:
    st.write("Your personalized itinerary:")
    st.markdown(st.session_state.second_result)
