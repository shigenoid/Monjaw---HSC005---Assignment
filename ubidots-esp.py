from machine import Pin, time_pulse_us
import dht
import urequests as requests
import network
import utime as time

# WiFi credentials
WIFI_SSID = "Kiddo"
WIFI_PASSWORD = "kidstore45"

# API endpoints
API_BASE_URL = "http://192.168.18.87:5000" 
DHT11_ENDPOINT = f"{API_BASE_URL}/send_dht11"
ULTRASONIC_ENDPOINT = f"{API_BASE_URL}/send_ultrasonic"

#Ubidots parameters
UBIDOTS_TOKEN = "BBUS-o8jBgkNR8w2ERAU1vjXLGMmnP7z5Z9" 
UBIDOTS_DEVICE_LABEL = "esp32"  
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE_LABEL}/"

DHT_PIN = Pin(27)
dht_sensor = dht.DHT11(DHT_PIN)

TRIG_PIN = Pin(33, Pin.OUT)
ECHO_PIN = Pin(32, Pin.IN)

def connect_wifi():
    wifi_client = network.WLAN(network.STA_IF)
    wifi_client.active(True)
    print("Connecting to WiFi...")
    wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 10
    while not wifi_client.isconnected() and timeout > 0:
        time.sleep(1)
        print(f"Trying... {timeout}s left")
        timeout -= 1
    
    if wifi_client.isconnected():
        print("WiFi Connected! IP:", wifi_client.ifconfig()[0])
    else:
        print("WiFi connection failed. Restarting ESP32...")
        time.sleep(2)
        machine.reset()

def send_data(url, data, headers=None):
    """Send data to a given URL with optional headers (for Ubidots)."""
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Data sent to {url}: {response.text}")
    except Exception as e:
        print(f"Failed to send data to {url}: {e}")

def read_ultrasonic():
    TRIG_PIN.off()
    time.sleep_us(2)
    TRIG_PIN.on()
    time.sleep_us(10)
    TRIG_PIN.off()
    
    pulse_duration = time_pulse_us(ECHO_PIN, 1, 30000)
    distance = (pulse_duration / 2) * 0.0343  # Convert to cm
    return round(distance, 2)

# Connect to WiFi
connect_wifi()

while True:
    try:
        # Read DHT11
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print(f"DHT11 - Temperature: {temp}°C, Humidity: {humidity}%")

        # Read Ultrasonic
        distance = read_ultrasonic()
        print(f"Ultrasonic - Distance: {distance} cm")
        
        # Send data to Flask Server
        send_data(DHT11_ENDPOINT, {"temperature": temp, "humidity": humidity})
        send_data(ULTRASONIC_ENDPOINT, {"distance": distance})

        # Send data to Ubidots
        ubidots_headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}
        ubidots_payload = {
            "temperature": temp,
            "humidity": humidity,
            "distance": distance
        }
        send_data(UBIDOTS_URL, ubidots_payload, ubidots_headers)

    except Exception as e:
        print("Sensor error:", e)
    
    time.sleep(5)
