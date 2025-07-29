from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Only render the form on initial GET request
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Retrieve form data
    temp = request.form.get('temp', type=float)
    sbp = request.form.get('sbp', type=float)
    resp = request.form.get('resp', type=float)
    wbc = request.form.get('wbc', type=float)
    lactate = request.form.get('lactate', type=float)
    creatinine = request.form.get('creatinine', type=float)
    
    # You can retrieve other fields if needed, but for simplicity,
    # we'll only use the ones in the scoring logic.
    # age = request.form.get('age', type=int)
    # gender = request.form.get('gender')
    # fio2 = request.form.get('fio2', type=float)
    # ph = request.form.get('ph', type=float)

    # --- Sepsis Risk Calculation Logic (Moved from JavaScript) ---
    score = 0
    reasons = []

    # 1. Temperature (SIRS criteria)
    if temp is not None and (temp > 38.0 or temp < 36.0):
        score += 1
        reasons.append(f"Abnormal Temperature ({temp}°C)")

    # 2. Systolic Blood Pressure (qSOFA criteria)
    if sbp is not None and sbp <= 100:
        score += 1
        reasons.append(f"Low Systolic BP (≤{sbp} mmHg)")

    # 3. Respiration Rate (qSOFA/SIRS criteria)
    if resp is not None and resp >= 22:
        score += 1
        reasons.append(f"High Respiration Rate (≥{resp}/min)")

    # 4. White Blood Cell Count (SIRS criteria)
    if wbc is not None and (wbc > 12.0 or wbc < 4.0):
        score += 1
        reasons.append(f"Abnormal WBC Count ({wbc} x10³/μL)")

    # 5. Lactate level (sepsis indicator)
    if lactate is not None and lactate > 2.0:
        score += 1
        reasons.append(f"Elevated Lactate ({lactate} mmol/L)")
        
    # 6. Creatinine (organ dysfunction indicator)
    if creatinine is not None and creatinine > 2.0:
        score += 1
        reasons.append(f"Elevated Creatinine ({creatinine} mg/dL)")

    # Determine risk level, color, width, and explanation
    risk_level = ''
    risk_color_class = ''
    risk_bar_color = ''
    risk_bar_width = '0%'
    explanation = ''

    if score == 0:
        risk_level = 'Low Risk'
        risk_color_class = 'text-green-600'
        risk_bar_color = 'bg-green-500'
        risk_bar_width = '15%'
        explanation = 'No significant risk factors identified based on the provided data. Continue monitoring.'
    elif score >= 1 and score <= 2:
        risk_level = 'Medium Risk'
        risk_color_class = 'text-yellow-600'
        risk_bar_color = 'bg-yellow-500'
        risk_bar_width = '50%'
        explanation = 'Some indicators suggest a potential risk. Clinical correlation and further evaluation are recommended.'
    else: # score >= 3
        risk_level = 'High Risk'
        risk_color_class = 'text-red-600'
        risk_bar_color = 'bg-red-500'
        risk_bar_width = '90%'
        explanation = 'Multiple indicators suggest a high risk of sepsis or septic shock. This warrants urgent medical attention.'
        
    if reasons:
        explanation += f"<br><br><strong class='font-semibold'>Contributing Factors:</strong><br>{'<br>'.join(reasons)}"

    # Render the results on a new page (results.html)
    return render_template(
        'results.html',
        risk_level=risk_level,
        risk_color_class=risk_color_class,
        risk_bar_color=risk_bar_color,
        risk_bar_width=risk_bar_width,
        result_explanation=explanation
    )

if __name__ == '__main__':
    app.run(debug=True)