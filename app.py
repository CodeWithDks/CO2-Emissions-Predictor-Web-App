from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import os
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# Load the trained model
MODEL_PATH = 'model/co2_emission_model.pkl'

def load_model():
    """Load the trained model and return model data"""
    try:
        if os.path.exists(MODEL_PATH):
            model_data = joblib.load(MODEL_PATH)
            return model_data
        else:
            print(f"Model file not found at {MODEL_PATH}")
            return None
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Load model at startup
model_data = load_model()

# Fuel type mappings for user understanding
FUEL_TYPE_INFO = {
    'Z': {'name': 'Premium Gasoline', 'description': '91-94 octane gasoline'},
    'D': {'name': 'Diesel', 'description': 'Diesel fuel'},
    'X': {'name': 'Regular Gasoline', 'description': '87 octane gasoline'},
    'E': {'name': 'Ethanol (E85)', 'description': 'Flex fuel - 85% ethanol'},
    'N': {'name': 'Natural Gas', 'description': 'Compressed natural gas (CNG)'}
}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', fuel_types=FUEL_TYPE_INFO)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        if model_data is None:
            return jsonify({'error': 'Model not loaded. Please check if model file exists.'}), 500
        
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract and validate input values
        fuel_consumption = data.get('fuel_consumption')
        fuel_efficiency = data.get('fuel_efficiency')
        fuel_type = data.get('fuel_type')
        
        # Validation
        if fuel_consumption is None or fuel_efficiency is None or fuel_type is None:
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            fuel_consumption = float(fuel_consumption)
            fuel_efficiency = float(fuel_efficiency)
        except ValueError:
            return jsonify({'error': 'Invalid numeric values'}), 400
        
        if fuel_type not in FUEL_TYPE_INFO:
            return jsonify({'error': 'Invalid fuel type'}), 400
        
        # Additional validation ranges
        if fuel_consumption <= 0 or fuel_consumption > 50:
            return jsonify({'error': 'Fuel consumption should be between 0 and 50 L/100km'}), 400
        
        if fuel_efficiency <= 0 or fuel_efficiency > 150:
            return jsonify({'error': 'Fuel efficiency should be between 0 and 150 mpg'}), 400
        
        # Prepare input data
        input_data = {
            'Fuel Consumption (L/100 km)': [fuel_consumption],
            'Fuel Efficiency (mpg)': [fuel_efficiency],
            'Fuel Type': [fuel_type]
        }
        
        # Convert to DataFrame
        input_df = pd.DataFrame(input_data)
        
        # Make prediction
        model = model_data['model']
        prediction = model.predict(input_df)[0]
        
        # Prepare response
        response = {
            'prediction': round(prediction, 2),
            'fuel_type_name': FUEL_TYPE_INFO[fuel_type]['name'],
            'input_data': {
                'fuel_consumption': fuel_consumption,
                'fuel_efficiency': fuel_efficiency,
                'fuel_type': fuel_type
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/fuel-types')
def fuel_types():
    """Return fuel type information"""
    return jsonify(FUEL_TYPE_INFO)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)