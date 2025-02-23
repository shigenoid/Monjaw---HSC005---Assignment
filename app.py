import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

uri = "mongodb+srv://shigenoid:GPcE7pnxgRAGBf3x@monjaw-cluster.mx7pn.mongodb.net/?retryWrites=true&w=majority&appName=Monjaw-Cluster"
client = MongoClient(uri)
db = client['data_sensor']
dht11_collection = db['dht11']  
ultrasonic_collection = db['ultrasonic'] 

@app.route('/')
def index():
    return "Hello, World!"

# DHT11
@app.route('/send_dht11', methods=['POST'])
def send_dht11():
    data = request.json  
    if not data or 'temperature' not in data or 'humidity' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Temperature and humidity are required!'}), 400

    try:
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
    except ValueError:
        return jsonify({'error': 'Bad Request', 'message': 'Temperature and humidity must be numeric!'}), 400

    sensor_data = {
        'Temperature (°C)': temperature,
        'Humidity (%)': humidity,
        'timestamp': datetime.utcnow() + timedelta(hours=7)
    }

    result = dht11_collection.insert_one(sensor_data)
    return jsonify({'message': 'DHT11 data inserted successfully!', 'id': str(result.inserted_id)}), 201

# Ultrasonic
@app.route('/send_ultrasonic', methods=['POST'])
def send_ultrasonic():
    data = request.json  
    if not data or 'distance' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Distance is required!'}), 400

    try:
        distance = float(data['distance'])
    except ValueError:
        return jsonify({'error': 'Bad Request', 'message': 'Distance must be numeric!'}), 400

    sensor_data = {
        'Distance (cm)': distance,
        'timestamp': datetime.utcnow() + timedelta(hours=7)
    }

    result = ultrasonic_collection.insert_one(sensor_data)
    return jsonify({'message': 'Ultrasonic data inserted successfully!', 'id': str(result.inserted_id)}), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
