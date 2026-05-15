import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import altair as alt

# keep data for 5 minutes (300 seconds)
@st.cache_data(ttl=300)

def get_data(worksheet_name):
    return conn.read(worksheet=worksheet_name, ttl=0)

# setup google sheet connection
conn = st.connection("gsheets",type=GSheetsConnection)

# LOGIC SECTION ------------------------------------------------------------

# intialize empty dataframes
nutrition_df = pd.DataFrame()
bodystats_df = pd.DataFrame()

# for ribbon section
try:
    # read from the nutrition sheet
    nutrition_df = get_data("Nutritions")
    if not nutrition_df.empty:
        nutrition_df['Date'] = pd.to_datetime(nutrition_df['Date'])

        # filter for today
        today_fuel = nutrition_df[nutrition_df['Date'].dt.date == datetime.now().date()]
        total_calories_today = today_fuel['Calories'].sum()
        total_protein_today = today_fuel['Protein'].sum()
    else:
        total_calories_today = 0
        total_protein_today = 0

    # read from bodystats sheet and save the weight
    bodystats_df = get_data("BodyStats")
    if not bodystats_df.empty:
        # pulling latest entry for weight and targets
        latest_stats = bodystats_df.iloc[-1]
        current_body_weight = latest_stats['Weight']
        user_target_cal = latest_stats['Target Calories']
        user_target_weight = latest_stats['Target Weight']
        user_target_prot = latest_stats['Target Protein']
    else:
        # Default fallback values
        current_body_weight = 70.0
        user_target_cal = 3000
        user_target_weight = 80.0
        user_target_prot = 160.0

except Exception as e:
    st.error("Wait, google is resting.. Using cached/empty data")
    total_protein_today, total_calories_today = 0, 0
    current_body_weight, user_target_cal, user_target_weight, user_target_prot = 70, 3000, 80, 160

# dynamic calculation
calories_remaining = user_target_cal - total_calories_today
protein_remaining = user_target_prot - total_protein_today

# TODO : complete this food database
# FOOD DATABASE
FOOD_DATABASE = {
    "Breakfast": {
        "Gardenia Wholemeal (2 Slices)": {"cal": 150, "prot": 7},
        "Choc Peanut Spread (2 tbsp)": {"cal": 195, "prot": 8},
        "Nasi Lemak + 1 Half Egg + Fruits": {"cal": 645, "prot": 16}
        # can add more here
    },
    "Lunch": {
        "3 Rice, 1/2 Body Siakap, Vegs": {"cal": 790 , "prot": 51}
        # add individual dish here
    },
    "Dinner": {
        "3 Rice, 3 Small Chicks, Vegs": {"cal": 950, "prot": 50}
        # add individual dish here
    },
    "Snacks/Other": {
        # add individual dish here
    },
    "Supplements": {
        "Creatine (5g)": {"cal": 0, "prot": 0}
        # can add more here
    }
}

# TODO : complete this workout database
# WORKOUT DATABASE
WORKOUT_DATABASE = {
    "Chest": ["Flat Bench Press", "Incline Bench Press", "Decline Bench Press", "Incline DB Press", "Chest Fly", "Push-ups"],
    "Back": ["Barbell Row", "Lat Pulldown", "Deadlift", "Pull-ups"],
    "Legs": ["Barbell Squat", "Leg Press", "Leg Extension", "Calf Raise"],
    "Arms": ["DB Curl", "Barbell Curl", "Tricep Pushdown", "Hammer Curl"],
    "Shoulders": ["Overhead Press", "Lateral Raise", "Face Pulls", "Front Raise"]
}

# UI SECTION -----------------------------------------------------------------

st.title("My Fitness Journey 🐺💪")

# top ribbon
st.header("Quick Glance 👀")
col_q1, col_q2, col_q3 = st.columns(3)
with col_q1:
    st.metric("Current Weight/Target (kg)", f"{current_body_weight} / {user_target_weight}")
with col_q2:
    st.metric("Daily Calories/Remains (kcal)",f"{total_calories_today} / {calories_remaining}")
with col_q3:
    st.metric("Protein Hit/Remains (g)",f"{total_protein_today} / {protein_remaining}")

# action center
st.divider()
st.header("Action Center 📝")
log, view = st.columns(2)

with log:
    st.subheader("Log Zone 🖊️")
    tab_nutrition, tab_workout, tab_body_stats = st.tabs(["Daily Fuel","Iron Progress","Body Stats"])
    # nutrition tab
    with tab_nutrition:
        st.subheader("Eat to Grow 🍚")

        # 1. UI: Category and multi select
        # add "custom/manual" to dictionary or as standalone option
        meal_categories = [cat for cat in FOOD_DATABASE.keys() if cat != "Supplements"] # remove the supplements category
        selected_category = st.selectbox("Meal Category", meal_categories)

        # add the manual entry option to the food list
        food_options = list(FOOD_DATABASE[selected_category].keys()) + ["➕ Manual Entry"]
        selected_food = st.multiselect(
            "Select Dish",
            food_options,
            key="food_selector"
        ) # to select many foods and sum the calories and proteins

        # initialize totals
        total_calories = 0
        total_protein = 0
        dish_parts = []

        # 2. Logic : handle the regulars (database items)
        # filter out "manual entry"
        db_items = [item for item in selected_food if item != "➕ Manual Entry"]

        for item in db_items:
            total_calories += FOOD_DATABASE[selected_category][item]["cal"]
            total_protein += FOOD_DATABASE[selected_category][item]["prot"]
            dish_parts.append(item)

        # 3. Logic : Handle manual entry
        # check if user (me) choose manual entry, if not, show the list
        if "➕ Manual Entry" in selected_food:
            st.divider()
            col_name, col_cal, col_prot = st.columns(3)
            with col_name:
                custom_name = st.text_input("What did you eat?", placeholder="e.g Cendol")
            with col_cal:
                custom_cal = st.number_input("Calories", min_value=0, step=10)
            with col_prot:
                custom_prot = st.number_input("Protein (g)", min_value=0, step=1)

            if custom_name:
                total_calories += custom_cal
                total_protein += custom_prot
                dish_parts.append(custom_name)

            # set variables to manual input
            dish_to_save = custom_name
            calories_to_save = custom_cal
            protein_to_save = custom_prot

        # 4. Logic : Supplements Integration
        st.subheader("Extra Supplements")

        # pull supplements key only
        supp_options = list(FOOD_DATABASE["Supplements"].keys())
        selected_supps = st.multiselect(
            "Select Boosters",
            supp_options,
            key="supp_selector"
        )

        for supp in selected_supps:
            total_calories += FOOD_DATABASE["Supplements"][supp]["cal"]
            total_protein += FOOD_DATABASE["Supplements"][supp]["prot"]
            dish_parts.append(supp)

        # 5. UI : The Summary
        full_dish_string = ", ".join(dish_parts)
        if dish_parts:
            st.info(f"Total for this log: {total_calories} kcal | {total_protein}g protein")

        # 6. Action : Save to gsheets
        # submitted = st.form_submit_button("Save Nutrition")
        if st.button("Save Nutrition"):
            if not dish_parts:
                st.warning("Please select or enter food first!")
            else:
                # create dataframe
                new_entry = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Meal": selected_category,
                    "Dish": full_dish_string,
                    "Calories": total_calories,
                    "Protein": total_protein
                }])

                # read-append-update
                try:
                    # use ttl=0 to get absolute latest data before saving
                    existing_fuel = conn.read(worksheet="Nutritions", ttl=0)
                    updated_fuel = pd.concat([existing_fuel, new_entry], ignore_index=True)
                except:
                    updated_fuel = new_entry

                # push back to nutrition worksheet
                conn.update(worksheet="Nutritions", data=updated_fuel)

                st.success(f"Logged successfully! 🔥")
                st.cache_data.clear()
                st.rerun()

    # workout tab
    with tab_workout:
        st.subheader("Lift to Grow 🦾")
        # 1. selection logic
        muscle_group = st.selectbox("Muscle Group", list(WORKOUT_DATABASE.keys()))

        # dependent dropdown
        exercise_options = WORKOUT_DATABASE[muscle_group]
        selected_exercise = st.selectbox("Exercise", exercise_options)

        col_w, col_r = st.columns(2)
        with col_w:
            lifted_weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5, format="%.1f")
        with col_r:
            total_reps = st.number_input("Total Reps", min_value=0, step=1)

        if st.button("Save Workout"):
            if total_reps == 0:
                st.warning("Did you really do 0 reps? Add some volume!")
            else:
                # create new row
                new_workout = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Muscle Group": muscle_group,
                    "Exercise": selected_exercise,
                    "Weight": lifted_weight,
                    "Reps": total_reps
                }])

                # read workouts sheet to append
                try:
                    existing_iron = conn.read(worksheet="Workouts", ttl=0)
                    updated_iron = pd.concat([existing_iron, new_workout], ignore_index=True)
                except:
                    updated_iron = new_workout

                conn.update(worksheet="Workouts", data=updated_iron)
                st.success(f"Logged: {selected_exercise} | {lifted_weight}kg x {total_reps} reps! 🔥")
                st.cache_data.clear()
                st.rerun()


    # body stats tab
    with tab_body_stats:
        st.subheader("Scale to Grow ♐")

        # 1. goal settings
        st.markdown("#### 🎯 Goal Setting")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            target_weight = st.number_input("Target Weight (kg)", value=80.0, step=0.5)
        with col_t2:
            target_calories = st.number_input("Target Daily Calories (kcal)", value=3000, step=100)
        with col_t3:
            target_protein = st.number_input("Target Daily Protein (g)", value=160, step=10)

        st.divider()

        # 2. daily entry
        st.markdown("#### ⚖️ Today's Entry")
        body_weight = st.number_input("Current weight (kg)", min_value=0.0, step=0.1, format="%.1f")

        # 3. optional muscle measurements (bodybuilding style)
        with st.expander("📏 Add Muscle Measurements (Optional)"):
            st.info("Measure in cm for precision")
            m_chest = st.number_input("Chest", min_value=0.0)
            m_waist = st.number_input("Waist", min_value=0.0)
            m_bicep = st.number_input("Bicep (L/R Avg)", min_value=0.0)

        if st.button("Save Body Stats"):
            # create new row
            new_stats_log = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Weight": body_weight,
                "Target Weight": target_weight,
                "Target Calories": target_calories,
                "Target Protein": target_protein,
                "Chest": m_chest,
                "Waist": m_waist,
                "Bicep": m_bicep
            }])

            # read bodystats sheet to append
            try:
                existing_bodystats = conn.read(worksheet="BodyStats", ttl=0)
                updated_bodystats = pd.concat([existing_bodystats, new_stats_log], ignore_index=True)
            except:
                updated_bodystats = new_stats_log

            conn.update(worksheet="BodyStats", data=updated_bodystats)
            st.success(f"Stats updated for {datetime.now().strftime('%d %b')}!")
            st.cache_data.clear()
            st.rerun()

# GRAPH PART -------------------------------------------------------------
with view:
    st.subheader("Growth Zone 📈")

    # body weight trend with target line
    if not bodystats_df.empty:
        st.write("Weight Progress (kg)")

        plot_df = bodystats_df.copy()
        plot_df['Date'] = pd.to_datetime(plot_df['Date']).dt.date

        # create dual line chart (actual vs target)
        weight_data = plot_df.set_index("Date")[["Weight", "Target Weight"]]
        st.line_chart(weight_data)
    else:
        st.info("Log your weight to see the trend!")

    st.divider()

    # nutrition consistency with target line
    if not nutrition_df.empty:
        st.write("Daily Calorie Intake")

        # 1. Prepare the data
        daily_cals = nutrition_df.groupby(nutrition_df['Date'].dt.date)['Calories'].sum().reset_index()
        daily_cals.columns = ['Date', 'Calories']

        # 2. Create the bar chart
        bars = alt.Chart(daily_cals).mark_bar(color="#ff4b4b").encode(
            x='Date:T',
            y='Calories:Q'
        )

        # 3. Create text labels
        text = bars.mark_text(
            align='center',
            baseline='bottom',
            dy=5,
            color='white'
        ).encode(text='Calories:Q')

        # 4. Create Target Line
        rule = alt.Chart(pd.DataFrame({'y': [user_target_cal]})).mark_rule(color='white', strokeDash=[5,5]).encode(y='y:Q')

        # Layer them together
        st.altair_chart(bars + text + rule, use_container_width=True)

    else:
        st.info("Eat to see your fuel charts!")

    st.divider()

    # strength progress
    try:
        workouts_df = conn.read(worksheet="Workouts", ttl=0)
        if not workouts_df.empty:
            st.write("Iron Progress")

            # selection
            ex_to_view = st.selectbox("View Progress for:", workouts_df['Exercise'].unique())

            # filter for chosen exercise
            ex_data = workouts_df[workouts_df['Exercise'] == ex_to_view].copy()
            # convert 'date' to datetime objects and strip the time
            ex_data['Date'] = pd.to_datetime(ex_data['Date']).dt.date

            # calculation for volume vs max weight
            # why? volume captures progress even if weight stay the same
            ex_data['Volume'] = ex_data['Weight'] * ex_data['Reps']

            metric_to_plot = st.radio("Metric Type:", ["Max Weight (kg)", "Total Volume (kg)"], horizontal=True)

            if metric_to_plot == "Max Weight (kg)":
                ex_trend = ex_data.groupby("Date")["Weight"].max()
                st.line_chart(ex_trend)
            else:
                # group volume by date shows total work for that day
                ex_trend = ex_data.groupby("Date")["Volume"].sum()
                st.area_chart(ex_trend)
                st.caption("Total Weight moved (Weight x Reps) per session")

    except:
        st.write("No workouts logged yet.. go lift some iron!")

    st.divider()

    # muscle group distribution
    if not workouts_df.empty:
        st.write("Muscle Group Distribution")
        # count how many sets per muscle group
        muscle_dist = workouts_df['Muscle Group'].value_counts()
        st.bar_chart(muscle_dist)

    else:
        st.info("Start your workouts!")
