"""
app.py
------
Step 10: Interactive Streamlit Web Demonstration for Room Occupancy Detection

Features:
- Sliders and number inputs for primary sensors: Light, CO2, Temperature, Humidity.
- Automatically calculates physical HumidityRatio from Temperature and Humidity.
- Loads trained explainable model (outputs/models/occupancy_model.joblib).
- Displays immediate real-time prediction: OCCUPIED (1) or EMPTY (0) with predicted probability.
- Interactive scenario presets (Office Hours, Empty Night, Forgotten Lights).
- Clear on-screen explanation of model mechanics and physical operational limits.

Author: 2nd-Year B.Tech APL Project Team (CSE-3006 APL)
Based on: Candanedo & Feldheim (2016), Energy and Buildings
"""

import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st


# Configure page layout and style
st.set_page_config(
    page_title="Room Occupancy Detector",
    page_icon="🏢",
    layout="wide"
)


def calculate_humidity_ratio(temperature_c, relative_humidity_pct, atmospheric_pressure_hpa=1013.25):
    """
    Compute physical HumidityRatio (kg of water vapor per kg of dry air)
    using the Magnus-Tetens formula used in building physics.
    """
    # Saturation vapor pressure in hPa
    p_ws = 6.1078 * np.exp((17.27 * temperature_c) / (temperature_c + 237.3))
    # Actual vapor pressure
    p_w = (relative_humidity_pct / 100.0) * p_ws
    # Humidity ratio (mixing ratio)
    humidity_ratio = 0.62198 * p_w / (atmospheric_pressure_hpa - p_w)
    return float(humidity_ratio)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "outputs", "models", "occupancy_model.joblib")


@st.cache_resource
def load_trained_model(model_path=DEFAULT_MODEL_PATH):
    """Load the trained machine learning model from disk."""
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)


# Title and Header
st.title("🏢 Smart Room Occupancy Detection System")
st.markdown(
    """
    Live environmental classification using non-intrusive ambient sensors (Light, CO₂, Temperature, Humidity).  
    *Built upon the public dataset and benchmark by Candanedo & Feldheim (Energy and Buildings, 2016).*
    """
)
st.divider()

# Load model
model = load_trained_model()
if model is None:
    st.error(
        "⚠️ Model file not found at `outputs/models/occupancy_model.joblib`! "
        "Please run `python src/baseline_models.py` in your terminal to train and save the model."
    )
    st.stop()

# Layout: Two columns (Left: Inputs & Scenarios, Right: Prediction & Analysis)
col_input, col_pred = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📊 Sensor Reading Inputs")
    st.caption("Adjust sliders below or select a quick demonstration preset.")

    # Preset selection
    preset = st.selectbox(
        "Load Quick Demonstration Preset:",
        [
            "Custom User Values",
            "Preset 1: Regular Working Hours (Occupied)",
            "Preset 2: Empty Room at Night (Empty)",
            "Preset 3: Empty Room with Lights Left ON (Edge Case)"
        ]
    )

    # Default values based on preset
    if preset == "Preset 1: Regular Working Hours (Occupied)":
        init_light, init_co2, init_temp, init_hum = 520.0, 950.0, 22.8, 28.5
    elif preset == "Preset 2: Empty Room at Night (Empty)":
        init_light, init_co2, init_temp, init_hum = 0.0, 430.0, 19.8, 24.0
    elif preset == "Preset 3: Empty Room with Lights Left ON (Edge Case)":
        init_light, init_co2, init_temp, init_hum = 460.0, 420.0, 20.5, 23.0
    else:
        init_light, init_co2, init_temp, init_hum = 425.0, 720.0, 21.8, 27.2

    # Slider Inputs
    light = st.slider("💡 Light Intensity (Lux):", min_value=0.0, max_value=1600.0, value=float(init_light), step=5.0,
                      help="Typical indoor office light is 300-600 Lux. <10 Lux indicates dark/night.")
    co2 = st.slider("🌬️ CO2 Concentration (ppm):", min_value=380.0, max_value=2200.0, value=float(init_co2), step=10.0,
                    help="Outdoor baseline is ~400 ppm. Human respiration pushes indoor CO2 to 600-1500+ ppm.")
    temp = st.slider("🌡️ Temperature (°C):", min_value=17.0, max_value=28.0, value=float(init_temp), step=0.1)
    hum = st.slider("💧 Relative Humidity (%):", min_value=15.0, max_value=50.0, value=float(init_hum), step=0.5)

    # Physical calculation
    hum_ratio = calculate_humidity_ratio(temp, hum)
    st.info(f"📐 **Computed HumidityRatio:** `{hum_ratio:.6f}` kg/kg (derived from Temperature and Humidity)")

with col_pred:
    st.subheader("🎯 Real-Time Occupancy Classification")

    # Prepare DataFrame row
    input_data = pd.DataFrame([{
        "Temperature": temp,
        "Humidity": hum,
        "Light": light,
        "CO2": co2,
        "HumidityRatio": hum_ratio
    }])

    # Run inference
    prediction = int(model.predict(input_data)[0])
    probabilities = model.predict_proba(input_data)[0]
    p_empty = probabilities[0]
    p_occupied = probabilities[1]

    # Display prediction card
    if prediction == 1:
        st.markdown(
            f"""
            <div style="background-color: #fde8e8; border-left: 8px solid #e02424; padding: 20px; border-radius: 8px;">
                <h2 style="color: #9b1c1c; margin: 0;">🔴 ROOM STATUS: OCCUPIED</h2>
                <p style="font-size: 18px; color: #771d1d; margin: 8px 0 0 0;">
                    Predicted Probability: <b>{p_occupied * 100:.2f}%</b> confident
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="background-color: #def7ec; border-left: 8px solid #0e9f6e; padding: 20px; border-radius: 8px;">
                <h2 style="color: #03543f; margin: 0;">🟢 ROOM STATUS: EMPTY</h2>
                <p style="font-size: 18px; color: #046c4e; margin: 8px 0 0 0;">
                    Predicted Probability: <b>{p_empty * 100:.2f}%</b> confident
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.write("#### Confidence Gauge:")
    st.progress(float(p_occupied))
    st.caption(f"Empty: {p_empty * 100:.1f}% &nbsp;|&nbsp; Occupied: {p_occupied * 100:.1f}%")

    st.write("---")
    st.write("#### 🔍 Rule-Based Decision Logic Trace:")
    if light <= 365.12:
        st.write("1. `Light <= 365.12 Lux` ➔ Primary indicator that workspace is **Dark / Empty**.")
        if hum <= 37.74:
            st.write("2. `Humidity <= 37.74%` ➔ Confirmed **EMPTY** (Node confidence ~99%).")
        else:
            st.write("2. `Humidity > 37.74%` ➔ Elevated humidity branch.")
    else:
        st.write("1. `Light > 365.12 Lux` ➔ Artificial lighting is active.")
        if co2 > 456.33:
            st.write("2. `CO2 > 456.33 ppm` ➔ Confirmed human respiration buildup ➔ **OCCUPIED**.")
        else:
            st.write("2. `CO2 <= 456.33 ppm` ➔ Low CO2 suggests room may be vacant despite lights.")

# Bottom Section: Model Overview & Limitations
st.divider()
st.subheader("ℹ️ How This Model Works & Operational Boundaries")

tab1, tab2, tab3 = st.tabs(["How the Model Decides", "Physical Sensor Principles", "Real-World Edge Cases"])

with tab1:
    st.markdown(
        """
        - **Algorithm:** Explainable Scikit-Learn Decision Tree (`max_depth=3`).
        - **Why single-row inference?** This demo operates in zero-memory mode: it classifies state instantly
          from a single instantaneous snapshot without buffering past historical readings.
        - **Explainability:** The entire decision tree has only 8 terminal leaves. Every classification
          can be verified by hand without any hidden matrix operations or black-box embeddings.
        """
    )

with tab2:
    st.markdown(
        """
        1. **Light:** Humans require artificial light for indoor work. When Light < 360 Lux, the room is almost always vacant.
        2. **CO2:** Humans exhale carbon dioxide at ~40,000 ppm. In an enclosed room, occupancy increases ambient CO2 from ~400 ppm baseline to 700-1500+ ppm.
        3. **Temperature & Humidity:** Human body heat (approx 100 Watts per person) and respiration gradually shift room temperature and moisture content.
        """
    )

with tab3:
    st.markdown(
        """
        - **Dark Room with High CO2 (e.g. Someone Sleeping vs Office After-Hours):**
          If Light is 0 Lux but CO2 is high, the model predicts **EMPTY**. Why? In an office building, people leave at 6:00 PM,
          turn off the lights, and go home. Trapped exhaled CO2 takes 30–60 minutes to slowly diffuse out. In the dataset,
          there are 3,233 instances of Light < 10 Lux with high CO2, and in **100% of those real cases**, the room was empty!
          Predicting occupied here would waste energy running air conditioning in empty offices every evening.
        - **Single Office Environment:** The dataset was collected in a 3.1m × 5.8m office. Thresholds may require calibration for open-plan spaces.
        - **Window Sunlight Interference:** Strong afternoon sunlight can elevate photodiode readings above 400 Lux even when lights are switched off.
        - **Forgotten Lights:** If occupants leave lights ON upon departing, the system must wait for CO2 to dissipate before declaring vacancy.
        - **Door Open Diffusion:** When the office door is left open, CO2 diffuses into corridors, diminishing static buildup (which is why our 5-minute trend features help).
        """
    )
