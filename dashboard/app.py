import streamlit as st
import requests
import pandas as pd
import joblib
import time

# Backend API URL (replace with your PC's local IP)
BACKEND_URL = "http://172.16.83.116:8000"

# Device ID
ESP_ID = "esp32_01"  # Change this to match your ESP32's ID

st.title("Cardiac Anomaly Detection Dashboard")

# Initialize session state
if "latest_data" not in st.session_state:
    st.session_state.latest_data = None

# --- Start Measurement Button ---
if st.button("Start Measurement"):
    st.info(f"Sending start signal to ESP32 ({ESP_ID})... (collecting for ~15 s)")
    
    try:
        # Send start signal with device ID
        resp = requests.get(f"{BACKEND_URL}/start/{ESP_ID}", timeout=5)
        if resp.status_code == 200:
            st.success("Start signal sent!")
        else:
            st.error(f"Failed to start: {resp.status_code}")
            st.stop()
    except Exception as e:
        st.error(f"Could not send start signal: {e}")
        st.stop()

    # Wait for ESP32 to collect and upload data
    st.info("Waiting for ESP32 to finish and upload data...")
    max_wait = 30  # seconds
    poll_interval = 2
    start_time = time.time()
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    while time.time() - start_time < max_wait:
        elapsed = time.time() - start_time
        progress = min(elapsed / max_wait, 1.0)
        progress_bar.progress(progress)
        
        try:
            resp = requests.get(f"{BACKEND_URL}/latest/{ESP_ID}", timeout=5)
            data = resp.json()
            
            if data.get("status") == "waiting":
                status_text.info(f"⏳ Still collecting... ({elapsed:.0f}s)")
            elif data.get("status") == "unknown_id":
                status_text.error("ESP32 ID not recognized. Check your device ID.")
                break
            elif "hr" in data and data.get("hr", 0) > 0:
                status_text.success("✅ Data received!")
                st.session_state.latest_data = data  # store in session state
                break
            else:
                status_text.info(f"⏳ Waiting for valid data... ({elapsed:.0f}s)")
                
        except Exception as e:
            status_text.warning(f"Polling... ({elapsed:.0f}s)")

        time.sleep(poll_interval)
    
    progress_bar.empty()

# --- Display collected data ---
latest_data = st.session_state.latest_data
if latest_data:
    st.subheader("Latest Measurement")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Heart Rate", f"{latest_data.get('hr', 0):.2f} bpm")
    with col2:
        st.metric("SpO₂", f"{latest_data.get('spo2', 0):.2f} %")

    # ECG waveform
    ecg_data = latest_data.get("ecg", [])
    if ecg_data:
        st.subheader("ECG Waveform")
        df = pd.DataFrame(ecg_data, columns=["ECG"])
        st.line_chart(df)

    # Patient info and prediction
    st.subheader("Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
    with col2:
        sex = st.selectbox("Sex", ["M", "F"])

    if st.button("Predict Cardiac Anomaly"):
        try:
            # Load ML model
            try:
                model = joblib.load("xgboost_cleveland_model.pkl")
            except FileNotFoundError:
                try:
                    model = joblib.load("../xgboost_cleveland_model.pkl")
                except FileNotFoundError:
                    st.error("❌ Model file not found. Please ensure 'xgboost_cleveland_model.pkl' is in the correct location.")
                    st.stop()
            
            # Prepare features as DataFrame
            rest_ecg = latest_data.get("rest_ecg", 0)
            sex_val = 1 if sex == "M" else 0
            hr = latest_data.get("hr", 0)
            age_val = age

            # --- Clip values to training range (Cleveland dataset) ---
            age_val_clipped = max(29, min(age_val, 77))
            if age_val != age_val_clipped:
                print(f"[LOG] Age {age_val} clipped to {age_val_clipped}")
            age_val = age_val_clipped

            hr_clipped = max(71, min(hr, 202))
            if hr != hr_clipped:
                print(f"[LOG] Heart rate {hr} clipped to {hr_clipped}")
            hr = hr_clipped

            rest_ecg_clipped = max(0, min(rest_ecg, 2))
            if rest_ecg != rest_ecg_clipped:
                print(f"[LOG] rest_ecg {rest_ecg} clipped to {rest_ecg_clipped}")
            rest_ecg = rest_ecg_clipped

            feature_df = pd.DataFrame([{
                "age": age_val,
                "sex": sex_val,
                "thalach": hr,       # heart rate
                "restecg": rest_ecg
            }])

            print("Feature DataFrame (used for prediction):")
            print(feature_df)

            # Make prediction
            prediction = model.predict(feature_df)[0]
            prob = model.predict_proba(feature_df)[0][1] if hasattr(model, "predict_proba") else None

            # Display results
            st.subheader("Prediction Result")
            if prediction == 1:
                st.error("⚠️ **Prone to cardiac anomaly**")
                st.warning("Please consult a healthcare professional for proper diagnosis.")
            else:
                st.success("💚 **Normal heart activity**")
                st.info("No cardiac anomaly detected based on the provided data.")

            if prob is not None:
                prob_float = float(prob)
                st.metric("Anomaly Probability", f"{prob_float*100:.1f}%")
                st.progress(min(max(prob_float, 0.0), 1.0))

            print(f"Model probabilities: {model.predict_proba(feature_df)[0]}")

        except Exception as e:
            st.error(f"❌ Error during prediction: {e}")
            st.exception(e)


# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("Configuration")
    st.write(f"**Backend URL:** {BACKEND_URL}")
    st.write(f"**ESP32 ID:** {ESP_ID}")
    
    if st.button("Check Connection"):
        try:
            resp = requests.get(f"{BACKEND_URL}/latest/{ESP_ID}", timeout=3)
            if resp.status_code == 200:
                st.success("✅ Backend connected")
            else:
                st.error(f"❌ Backend error: {resp.status_code}")
        except Exception as e:
            st.error(f"❌ Cannot connect to backend: {e}")
