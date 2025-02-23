import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

uri = "mongodb+srv://shigenoid:GPcE7pnxgRAGBf3x@monjaw-cluster.mx7pn.mongodb.net/?retryWrites=true&w=majority&appName=Monjaw-Cluster"
client = MongoClient(uri)
db = client['data_sensor']
sensor_collection = db['sensor_data']

@app.route('/')
def index():
    return "API is running!"

@app.route('/kirim_data', methods=['POST'])
def sensor_data():
    data = request.json
    
    if not data or 'temperature' not in data or 'humidity' not in data or 'distance' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Temperature, humidity, and distance are required!'}), 400

    try:
        data['timestamp'] = datetime.utcnow()
        sensor_collection.insert_one(data)
        return jsonify({'message': 'Data inserted successfully!'}), 201
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
