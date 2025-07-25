# 📁 Project Structure
# ----------------------
# neo_predictor_dashboard/
# ├─ app.py
# ├─ nearest-earth-objects.csv
# ├─ static/
# │   ├─ style.css
# │   └─ script.js
# └─ templates/
#     ├─ index.html
#     ├─ result.html
#     ├─ live.html
#     ├─ about.html
#     └─ insights.html

from flask import Flask, render_template, request, session
import numpy as np
import pandas as pd
import joblib
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

MODEL_PATH = os.getenv('MODEL_PATH', 'model.pkl')
try:
    model = joblib.load(MODEL_PATH)
except:
    model = None

@app.route('/')
def index():
    session['prediction_history'] = session.get('prediction_history', [])
    return render_template("index.html", prediction_history=session['prediction_history'])

@app.route('/predict', methods=["POST"])
def predict():
    try:
        abs_mag = float(request.form['abs_mag'])
        dia_min = float(request.form['dia_min'])
        dia_max = float(request.form['dia_max'])
        velocity = float(request.form['velocity'])
        miss_distance = float(request.form['miss_distance'])

        input_data = np.array([[abs_mag, dia_min, dia_max, velocity, miss_distance]])
        prediction = model.predict(input_data)[0]
        result_text = "🌋 Hazardous" if prediction else "✅ Not Hazardous"

        prediction_proba = None
        if hasattr(model, 'predict_proba'):
            prediction_proba = f"{model.predict_proba(input_data)[0][1] * 100:.2f}%"

        history = {
            'abs_mag': abs_mag,
            'dia_min': dia_min,
            'dia_max': dia_max,
            'velocity': velocity,
            'miss_distance': miss_distance,
            'result': result_text,
            'probability': prediction_proba,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        session['prediction_history'] = [history] + session.get('prediction_history', [])[:4]

        return render_template("index.html", prediction=result_text,
                               prediction_proba=prediction_proba,
                               input_values=request.form,
                               prediction_history=session['prediction_history'])

    except Exception as e:
        return render_template("index.html", error_message=str(e),
                               input_values=request.form,
                               prediction_history=session.get('prediction_history', []))

@app.route('/live')
def live():
    nasa_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={nasa_key}"
    try:
        response = requests.get(url)
        data = response.json()
        neos = []
        for neo in data['near_earth_objects'][today]:
            neos.append({
                'name': neo['name'],
                'hazardous': neo['is_potentially_hazardous_asteroid'],
                'velocity': float(neo['close_approach_data'][0]['relative_velocity']['kilometers_per_second']),
                'miss_distance': float(neo['close_approach_data'][0]['miss_distance']['astronomical']),
                'close_approach': neo['close_approach_data'][0]['close_approach_date_full']
            })
        return render_template("live.html", neos=neos, date=today)
    except Exception as e:
        return render_template("live.html", error=str(e), date=today)

@app.route('/insights')
def insights():
    try:
        df = pd.read_csv("nearest-earth-objects.csv")
        df.fillna(0, inplace=True)
        if 'hazardous' not in df.columns or 'diameter_min' not in df.columns or 'relative_velocity' not in df.columns or 'miss_distance' not in df.columns:
            raise ValueError("Required columns are missing in the CSV file.")

        df['hazardous'] = df['hazardous'].astype(str)
        df = df[(df['hazardous'].isin(['True', 'False'])) & (df['diameter_min'] > 0) & (df['relative_velocity'] > 0) & (df['miss_distance'] > 0)]
        records = df.to_dict(orient="records")
        return render_template("insights.html", data=records)
    except Exception as e:
        return render_template("insights.html", data=[], error=str(e))

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)
