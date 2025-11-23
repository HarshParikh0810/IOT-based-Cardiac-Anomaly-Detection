📡 IoT-Based Cardiac Anomaly Detection System

Real-Time ECG, Heart Rate & SpO₂ Monitoring With ML-Based Cardiac Risk Prediction

⭐ Overview

This project implements a real-time IoT-enabled cardiac monitoring system capable of measuring ECG signals, heart rate (BPM), and oxygen saturation (SpO₂).
Data is acquired using ESP32 + AD8232 + MAX30102, processed by a FastAPI backend, visualized on a Streamlit dashboard, and analyzed using an ML model trained on the UCI Cleveland Heart Disease Dataset to predict cardiac anomalies.

The system is low-cost, portable, and designed for remote health monitoring & telemedicine applications.

🏗 System Architecture
            ┌──────────────┐
            │   Streamlit   │
            │   Dashboard   │
            └───────▲──────┘
                    │
    Real-time ECG, BPM & SpO₂ Visualization
                    │
        ┌───────────┴───────────┐
        │       FastAPI Backend  │
        │  - ECG Filtering        │
        │  - Peak Detection       │
        │  - SpO₂ & BPM Calc      │
        │  - ML Prediction        │
        └───────────▲───────────┘
                    │ Wi-Fi / Serial
            ┌───────┴───────┐
            │     ESP32      │
            │  Data Gateway  │
            └─────▲────▲────┘
                  │    │
        ┌─────────┘    └─────────┐
        │                          │
 AD8232 ECG Sensor        MAX30102 PPG Sensor
 (ECG Waveform)          (SpO₂ & Heart Rate)

🧰 Hardware Used

ESP32 — Wi-Fi enabled microcontroller

AD8232 ECG Sensor — ECG signal acquisition

MAX30102 — Heart rate & SpO₂ via PPG

Jumper wires & ECG electrodes

Laptop/PC — Runs FastAPI + Streamlit

🖥 Software & Technologies
Layer	Technology
UI / Frontend	Streamlit
Backend API	FastAPI
ML Model	XGBoost / Scikit-learn
Signal Processing	NumPy, SciPy
Communication	PySerial / ESP32 WiFi
Visualization	Streamlit, Matplotlib
Language	Python
🔬 Working Principle
1. Signal Acquisition (ESP32)

AD8232 captures ECG signals at analog input.

MAX30102 provides SpO₂ & PPG-based heart rate.

ESP32 reads the data and streams it via Wi-Fi/Serial.

2. Backend Signal Processing (FastAPI)

Bandpass filtering to remove noise

Smoothing & normalization

R-peak detection for BPM

PPG ratio computation for SpO₂

Data packaging & streaming

3. Real-Time Visualization (Streamlit)

ECG waveform plotted live

Heart rate & SpO₂ displayed continuously

Start button triggers ESP32 data collection

Predict button sends user input + sensor values to ML model

4. ML-Based Cardiac Anomaly Detection

Inputs:

Age

Gender

Heart Rate

SpO₂

Extracted ECG features

Backend sends inputs to ML model

Model outputs:

Probability of cardiac anomaly

Normal / At-risk status

📁 Project Structure
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── ecg_processing.py        # Filtering & ECG feature extraction
│   ├── ml_model.py              # ML model loader & inference
│   └── xgboost_cleveland_model.pkl
│
├── dashboard/
│   └── app.py                   # Streamlit frontend
│
├── requirements.txt
└── README.md

🚀 How to Run the Project
1. Install Dependencies
pip install -r requirements.txt

2. Start FastAPI Backend
uvicorn backend.main:app --reload

3. Start Streamlit Dashboard
streamlit run dashboard/app.py

4. Connect ESP32

Flash your ESP32 code

Configure Wi-Fi credentials / COM port

Click Start Monitoring in the dashboard

📊 ML Model Details

Dataset: UCI Cleveland Heart Disease

Best Algorithm: XGBoost

Features Used:

Age

Gender

Heart Rate

SpO₂

ECG-derived metrics

Output:

Probability of anomaly

Binary classification (0 = Normal, 1 = Anomaly)

📷 Features

✔ Real-time ECG waveform streaming

✔ Accurate BPM & SpO₂ extraction

✔ ML-based cardiac anomaly prediction

✔ FastAPI + Streamlit full-stack workflow

✔ Low latency biomedical data processing

✔ Easily extendable for telemedicine

🧪 Results & Observations

ECG waveform plotted in real-time with stable sampling

BPM computed accurately using both ECG & PPG

SpO₂ values within 95–100% for healthy subjects

ML model predicts anomalies with high confidence

Complete loop from sensor → backend → dashboard works in milliseconds

🔮 Future Enhancements

Cloud storage with Firebase / AWS

Mobile app for remote monitoring

Deep learning-based ECG classification

MQTT-based streaming for wearable deployment

Battery-powered wearable hardware design

👨‍⚕️ Applications

Remote cardiac monitoring

Home-based patient care

Fitness & wellness analytics

IoT health devices

Telemedicine systems


🙌 Acknowledgments

UCI Heart Disease Dataset

ESP32 & AD8232 open-source community

Streamlit & FastAPI documentation
