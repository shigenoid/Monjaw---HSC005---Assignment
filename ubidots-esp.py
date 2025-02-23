from machine import Pin, time_pulse_us
import dht
import network
import urequests as requests
import utime as time

# WiFi Credentials
WIFI_SSID = "Kiddo"
WIFI_PASSWORD = "kidstore45"

# Ubidots API
DEVICE_ID = "esp32"
TOKEN = "BBUS-o8jBgkNR8w2ERAU1vjXLGMmnP7z5Z9"
UBIDOTS_URL = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_ID}"
HEADERS = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}

# API untuk mengirim ke Flask (MongoDB)
MONGO_API_URL = "http://192.168.18.87:5000/kirim_data"  # Ganti dengan IP lokal Flask

# Inisialisasi Sensor
DHT_PIN = Pin(27)  # Pin DHT11
dht_sensor = dht.DHT11(DHT_PIN)

TRIG = Pin(33, Pin.OUT)  # Pin Trig HC-SR04
ECHO = Pin(32, Pin.IN)  # Pin Echo HC-SR04

# Koneksi ke WiFi
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)

    print("Connecting to WiFi...")
    timeout = 10
    while not wifi.isconnected() and timeout > 0:
        time.sleep(1)
        print(f"Trying... {timeout}s left")
        timeout -= 1

    if wifi.isconnected():
        print("WiFi Connected! IP:", wifi.ifconfig()[0])
    else:
        print("WiFi connection failed. Restarting ESP32...")
        time.sleep(2)
        machine.reset()

# Mengukur jarak dari sensor Ultrasonic
def get_distance():
    TRIG.value(0)
    time.sleep_us(5)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    pulse_time = time_pulse_us(ECHO, 1, 30000)  # Waktu pantulan
    if pulse_time < 0:
        return -1  # Jika gagal

    distance = (pulse_time * 0.0343) / 2  # Rumus jarak (cm)
    return round(distance, 2)

# Mengirim data ke Ubidots
def send_to_ubidots(temp, humidity, distance):
    data = {"temperature": temp, "humidity": humidity, "distance": distance}
    try:
        response = requests.post(UBIDOTS_URL, json=data, headers=HEADERS)
        print("Data sent to Ubidots:", response.text)
    except Exception as e:
        print("Failed to send data to Ubidots:", e)

# Mengirim data ke Flask API (MongoDB)
def send_to_mongo(temp, humidity, distance):
    data = {"temperature": temp, "humidity": humidity, "distance": distance}
    try:
        response = requests.post(MONGO_API_URL, json=data, headers={"Content-Type": "application/json"})
        print("Data sent to MongoDB:", response.text)
    except Exception as e:
        print("Failed to send data to MongoDB:", e)

# Koneksi ke WiFi
connect_wifi()

# Loop utama
while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        distance = get_distance()

        print(f"Temperature: {temp}°C, Humidity: {humidity}%, Distance: {distance}cm")

        send_to_ubidots(temp, humidity, distance)
        send_to_mongo(temp, humidity, distance)

    except Exception as e:
        print("Sensor error:", e)

    time.sleep(5)  # Kirim setiap 5 detik
