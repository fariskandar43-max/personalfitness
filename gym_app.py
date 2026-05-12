import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# setup google sheet connection
conn = st.connection("gsheets",type=GSheetsConnection)

try:
    existing_data = conn.read()
except Exception as e:
    st.error("Connection failed. Using temporary local data")
    existing_data = pd.DataFrame([
        {"Date": "2026-05-10", "Calories": 2500, "Protein": 150},
        {"Date": "2026-05-11", "Calories": 800, "Protein": 45}
    ])

# LOGIC SECTION ------------------------------------------------------------

# mom's meal dictionary
calories = {
    1 : 500,
    2 : 800,
    3 : 1100
}

protein_estimate = {
    1 : 20,
    2 : 35,
    3 : 50
}

# get body weight to display data
if "Body Weight" in existing_data.columns and not existing_data["Body Weight"].isnull().all():
    latest_weight = existing_data[existing_data["Body Weight"] > 0]["Body Weight"].iloc[-1]
else:
    latest_weight = 71.0

# function to calculate calories
def calc_calories(calory, check_protein):
    return (calory) + (120 if check_protein else 0)

# get data for todays ribbon
# convert date column to datetime objects
existing_data['Date'] = pd.to_datetime(existing_data['Date'])

# get only rows from today
today = datetime.now().date()
today_data = existing_data[existing_data['Date'].dt.date == today]

# calculate sums for metrics
# sum calories column
total_calories_today = today_data['Calories'].sum()
# sum protein column
total_protein_today = today_data['Protein'].sum()
# calories remaining
calories_remaining = 3000 - total_calories_today


# UI SECTION -----------------------------------------------------------------

st.title("My Fitness Journey")

# top ribbon
st.header("Main Part")
col1, col2, col3, col4 = st.columns(4)

with col1 :
    st.metric("Current Weight", f"{latest_weight} kg")
with col2:
    st.metric("Daily Calories",f"{total_calories_today} kcal")
with col4:
    st.metric("Calories Remaining", f"{calories_remaining} kcal")
with col3:
    st.metric("Protein Hit",f"{total_protein_today} g")

# action center
st.header("Action Center")
log, view = st.columns([2,1])

with log:
    tab_nutrition, tab_workout, tab_body_stats = st.tabs(["Daily Fuel","Iron Progress","Body Stats"])
    # nutrition tab
    with tab_nutrition:
        st.subheader("Eat to Grow")
        st.info("1 = Small, 2 = Medium, 3 = Large")

        # get meal size
        meal_size = st.slider("Mom's Meal",1,3)

        st.subheader("Extra Supplements")

        protein_checked = st.checkbox("Protein")
        st.checkbox("Creatine")
        # st.checkbox("Steroid [!]")

        if st.button("Save Nutrition"):
            get_meal_size = calories[meal_size]

            total_calories = calc_calories(get_meal_size, protein_checked)

            # upload to google sheets
            # 1. create dictionary
            new_entry = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Category": "Nutrition",
                "Calories": total_calories,
                "Protein": protein_estimate[meal_size] + (25 if protein_checked else 0),
                "Exercise": "NA",
                "Weight Lifted": 0,
                "Reps": 0,
                "Body Weight": 0
            }])

            # 2. combine with existing data
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)

            # 3. push back to google sheets
            conn.update(data=updated_df)
            st.success("Gains logged to the cloud!")

            # rerun the script
            tab_nutrition.rerun()

    # workout tab
    with tab_workout:
        st.subheader("Lift to Grow")
        exercise_name = st.selectbox("Choose one:", ["Ex1","Ex2","Ex3"])

        weight, reps = st.columns(2)

        with weight:
            lifted_weight = st.number_input("Weight (kg)")
        with reps:
            total_reps = st.number_input("Total Reps")

        if st.button("Save Workout"):
            # create dataframe
            new_workout = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Category": "Workout",
                "Calories": 0, "Protein":0,
                "Exercise": exercise_name,
                "Weight Lifted": lifted_weight,
                "Reps": total_reps,
                "Body Weight": 0
            }])

            # upload to gsheets
            updated_df = pd.concat([existing_data, new_workout], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"Logged: {exercise_name}")
            st.rerun()

    # body stats tab
    with tab_body_stats as tbs:
        tbs.subheader("Scale to Grow")
        body_weight = tbs.number_input("Current weight (kg)")

        if tbs.button("Save Body Weight"):
            # create data frame
            new_weight_log = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Category": "Body Weight",
                "Calories": 0, "Protein": 0,
                "Exercise": "NA",
                "Weight Lifted": 0,
                "Reps": 0,
                "Body Weight": body_weight
            }])

            # save to gsheets
            updated_df = pd.concat([existing_data, new_weight_log], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"Weight updated: {body_weight} kg!")
            st.rerun()

with view:
    st.write("View Column")

# growth zone