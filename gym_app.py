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
    "Carbs/Base": {
        "White Rice (1 scoop)": {"cal": 160, "prot": 3},
        "White Rice (2 scoop)": {"cal": 320, "prot": 6},
        "White Rice (3 scoop)": {"cal": 480, "prot": 9},
        "White Rice (1 portion)": {"cal": 300, "prot": 5},
        "Nasi Lemak Rice (1 portion)": {"cal": 350, "prot": 5},
        "Gardenia Wholemeal (2 slices)": {"cal": 150, "prot": 7},
        "Nasi Goreng (1 portion)": {"cal": 550, "prot": 11},
        "Nasi Briyani (1 portion)": {"cal": 450, "prot": 8},
        "Nasi Hujan Panas (1 portion)": {"cal": 420, "prot": 7}
    },
    "Proteins": {
        "Ayam Goreng (Drumstick)": {"cal": 250, "prot": 15},
        "Ikan Keli (Fried)": {"cal": 320, "prot": 22},
        "Ikan Siakap (1/2 Body)": {"cal": 250, "prot": 35},
        "Telur Mata": {"cal": 190, "prot": 6},
        "Ayam Masak Kunyit (Meat)": {"cal": 140, "prot": 8},
        "Ayam Masak Merah (Thigh)": {"cal": 350, "prot": 19},
        "Ayam Masak Merah (Isi)": {"cal": 350, "prot": 28},
        "Kari Ayam (Wings)": {"cal": 150, "prot": 7},
        "Ayam Masak Lemak": {"cal": 300, "prot": 21},
        "Ayam Paprik (Standard)": {"cal": 220, "prot": 20},
        "Ayam Goreng Kunyit (Standard)": {"cal": 240, "prot": 20},
        "Ayam Kerutuk (Standard)": {"cal": 320, "prot": 20}
    },
    "Sides/Veggies": {
        "Mixed Veggies (1 scoop)": {"cal": 60, "prot": 2},
        "Sambal + Anchovies": {"cal": 100, "prot": 3},
    },
    "Drinks/Snacks": {
        "Green Tea Latte": {"cal": 130, "prot": 2},
        "Kuih Raya (Small portion)": {"cal": 180, "prot": 1},
        "Ice Cream Dark Choc Borneo": {"cal": 222, "prot": 3},
        "Ice Cream Pistachio La Cremeria": {"cal": 210, "prot": 2}
    },
    "Supplements": {
        "Creatine (5g)": {"cal": 0, "prot": 0},
        "Whey Protein (Future)": {"cal": 0, "prot": 0}
    }
}

# WORKOUT DATABASE
WORKOUT_DATABASE = {
    "Chest": ["Machine Pec Deck", "Weighted Dips", "Flat Bench Press", "Incline Bench Press", "Decline Bench Press", "DB Chest Fly", "Incline Cable Fly", "Decline Cable Fly", "Push-Ups"],
    "Back": ["Machine Lat Pullover", "DB Shrugs", "Reverse Pec Deck", "T-Bar Row", "Weighted Pull-Up", "Machine Row", "Barbell Shrug", "DB Shrug", "Machine Lat Pulldown"],
    "Legs": ["Standing Calf Raise", "Nautilus Glute Drive", "Barbell Hip Thrust", "DB Walking Lunges", "DB Lunges", "Seated Leg Curl", "Lying Leg Curl", "Leg Extension", "Romanian Deadlift"],
    "Bicep": ["DB Wrist Curls", "DB Wrist Extensions", "Bayesian Cable Curl", "Preacher Curl"],
    "Tricep": ["Overhead Cable Triceps Extension", "Tricep Pushdown", "Overhead DB Triceps Extension", "Single Arm OH DB Triceps Extension", "DB Skull Crusher"],
    "Shoulder": ["Barbell Overhead Press", "Lateral Raise", "Face Pulls", "Front Raise"],
    "Neck" : ["Neck Curls", "Neck Extensions"],
    "Abs": ["Cable Crunch", "Flat Sit-Up", "Decline Sit-Up", "Supported Leg Raise"],
    "Core": ["Deadlift"]
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

        if "meal_basket" not in st.session_state:
            st.session_state.meal_basket = []

        # 1. Quick meals option integration
        is_quick_meal = st.checkbox("⚡ Use Quick Meal / Combo Preset")

        if is_quick_meal:
            # add standalone category check for quick combos
            combo_options = [
                "Nasi Lemak + 1 Half Egg + Fruits",
                "Nasi Ayam Full Set"
            ]
            selected_combo = st.selectbox("Choose Preset Combo", combo_options)

            # preset parse mapping logic
            preset_map = {
                "Nasi Lemak + 1 Half Egg + Fruits": {"name": "Nasi Lemak Combo", "cal": 645, "prot": 16},
                "Nasi Ayam Full Set": {"name": "Nasi Ayam Full Set", "cal": 640, "prot": 27}
            }

            if st.button("Add Combo to Log Basket"):
                combo_data = preset_map[selected_combo]
                st.session_state.meal_basket.append({
                    "item": combo_data["name"],
                    "cal": combo_data["cal"],
                    "prot": combo_data["prot"]
                })
                st.success(f"Added {combo_data['name']} to basket!")

        else:
            # Standard atomic selection process

            # 1. UI: Category and multi select
            # add "custom/manual" to dictionary or as standalone option
            meal_categories = [cat for cat in FOOD_DATABASE.keys() if cat != "Supplements"]  # remove the supplements category
            selected_category = st.selectbox("Meal Category", meal_categories)

            # add the manual entry option to the food list
            food_options = list(FOOD_DATABASE[selected_category].keys()) + ["➕ Manual Entry"]
            selected_food = st.multiselect("Select Dish", food_options, key="food_selector")

            # temporary manual capture scope
            custom_name, custom_cal, custom_prot = "", 0, 0
            if "➕ Manual Entry" in selected_food:
                st.markdown("#### 📝 Custom Entry Specs")

                col_name, col_cal, col_prot = st.columns(3)
                with col_name:
                    custom_name = st.text_input("What did you eat?", placeholder="e.g Cendol")
                with col_cal:
                    custom_cal = st.number_input("Calories", min_value=0, step=10)
                with col_prot:
                    custom_prot = st.number_input("Protein (g)", min_value=0, step=1)

            # interactive basket append trigger
            if st.button("📥 Add Selection to Basket"):
                # handle database values
                db_items = [item for item in selected_food if item != "➕ Manual Entry"]
                for item in db_items:
                    st.session_state.meal_basket.append({
                        "item": item,
                        "cal": FOOD_DATABASE[selected_category][item]["cal"],
                        "prot": FOOD_DATABASE[selected_category][item]["prot"]
                    })

                # handle manual strings
                if custom_name:
                    st.session_state.meal_basket.append({
                        "item": custom_name,
                        "cal": custom_cal,
                        "prot": custom_prot
                    })
                st.success("Items cached into current basket session!")

        # 2. Logic : Supplements Integration
        st.subheader("Extra Supplements")

        # pull supplements key only
        supp_options = list(FOOD_DATABASE["Supplements"].keys())
        selected_supps = st.multiselect("Select Boosters", supp_options, key="supp_selector")

        if st.button("➕ Add Supplements to Basket"):
            for supp in selected_supps:
                st.session_state.meal_basket.append({
                    "item": supp,
                    "cal": FOOD_DATABASE["Supplements"][supp]["cal"],
                    "prot": FOOD_DATABASE["Supplements"][supp]["prot"]
                })
                st.success("Supplements verified and staged!")

        # 3. Dynamic aggregator view (display current basket status)
        if st.session_state.meal_basket:
            st.divider()
            st.markdown("#### 🧺 Current Meal Basket Staging")

            # loop values out of list items
            staged_names = [x["item"] for x in st.session_state.meal_basket]
            final_calories = sum(x["cal"] for x in st.session_state.meal_basket)
            final_protein = sum(x["prot"] for x in st.session_state.meal_basket)
            final_dish_string = ", ".join(staged_names)

            st.info(f"**Items Staged** {final_dish_string}\n\n**Accumulated Payload:** {final_calories} kcal | {final_protein}g protein")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                # 4. Action : Commit single integrated row packet back to target worksheet
                if st.button("🚀 Push Whole Meal to Sheets", type="primary"):
                    new_entry = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Dish": final_dish_string,
                        "Calories": final_calories,
                        "Protein": final_protein
                    }])

                    try:
                        # use ttl=0 to get absolute latest data before saving
                        existing_fuel = conn.read(worksheet="Nutritions", ttl=0)
                        updated_fuel = pd.concat([existing_fuel, new_entry], ignore_index=True)
                    except:
                        updated_fuel = new_entry

                    # push back to nutrition worksheet
                    conn.update(worksheet="Nutritions", data=updated_fuel)

                    st.success("Perfect data insertion complete! 🔥")
                    st.cache_data.clear()
                    st.rerun()

            with col_b2:
                if st.button("🗑️ Clear Basket"):
                    st.session_state.meal_basket = []
                    st.rerun()

    # workout tab
    with tab_workout:
        st.subheader("Lift to Grow 🦾")

        # workout plan expander
        with st.expander("📆 5 Day Hypertrophy Blueprint"):
            st.markdown("""
                | Day | Focus Split | Objective | Core / Detail Focus |
                | :--- | :--- | :--- | :--- |
                | 1 | Pull | Back Thickness & Width | Reverse Pec Deck (Rear Delts) |
                | 2 | Push | Chest Hypertrophy | Flat/Decline Sit-Up |
                | 3 | Legs | Lower Body Power | Standing Calf Raise |
                | 4 | Shoulders/Arms | Upper Body Width & Arms | Complete Arm Superset |
                | 5 | Core/Structural | Posterior Chain & Abs | Cable Crunch, Leg Raise, Wrist Curls |
            """)
        st.divider()
        
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

    tab_graphs, tab_insights = st.tabs(["Graphs", "Insights"])

    with tab_graphs:
        st.subheader("Graph to Progress 🔍")

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

    with tab_insights:
        st.subheader("Insights to Action 🚩")

        # 1. Data filtering logic
        # Get data from the last 7 days
        last_7_days = datetime.now() - pd.Timedelta(days=7)

        if not nutrition_df.empty:
            weekly_fuel = nutrition_df[nutrition_df['Date'] >= last_7_days]

            # Calculate consistency
            daily_totals = weekly_fuel.groupby(weekly_fuel['Date'].dt.date)[['Calories', 'Protein']].sum()
            days_hit_target = len(daily_totals[daily_totals['Calories'] >= user_target_cal])

            # UI: Mini dashboard for the week
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                st.metric("Target Hit Rate", f"{days_hit_target} / 7 Days")
            with col_in2:
                avg_prot = daily_totals['Protein'].mean()
                st.metric("Avg Weekly Protein", f"{avg_prot:.1f} g")

            # 2. The bulk staple - top foods
            st.markdown("#### 🏆 My Bulk Staples")
            # Split the comma separated dish string and count individuals
            all_foods = weekly_fuel['Dish'].str.split(', ').explode()
            top_foods = all_foods.value_counts().head(3)
            st.write("You relied of these most this week:")
            for food, count in top_foods.items():
                st.write(f"- **{food}**: {count} times")

        st.divider()

        # 3. Workout Comparison
        if not workouts_df.empty:
            st.markdown("#### 🦾 Last Session vs Best Session")
            ex_list = workouts_df['Exercise'].unique()
            selected_ex = st.selectbox("Compare Exercise:", ex_list, key="comp_ex")

            ex_history = workouts_df[workouts_df['Exercise'] == selected_ex]

            last_weight = ex_history.iloc[-1]['Weight']
            max_weight = ex_history['Weight'].max()

            c1, c2 = st.columns(2)
            c1.metric("Last Lift", f"{last_weight} kg")
            c2.metric("All-Time PB", f"{max_weight} kg", delta=f"{last_weight - max_weight} kg")
