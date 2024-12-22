import serial
import serial.tools.list_ports
import sys
import numpy as np
import joblib
import time
import requests
import asyncio
from telegram import Bot
from flask import Flask, jsonify, render_template
import threading

sys.stdout.reconfigure(encoding='utf-8')

# Flask uygulamasını başlatıyoruz
app = Flask(__name__)

# Modeli yükleyelim (önceden kaydedildiğini varsayıyoruz)
model = joblib.load('C:/Astroit/smell_model.pkl')

# Telegram bot ayarları
TELEGRAM_TOKEN = '7185824936:AAGHjelLErQmoJ9DBoMrYvcW36h7KC7eaU4'  # BotFather'dan aldığınız token
CHAT_IDS = ['360310929', '5619771051']  # Mesaj göndermek istediğiniz kullanıcıların chat id'leri
bot = Bot(token=TELEGRAM_TOKEN)

# ChatGPT API kullanarak yorum yapma
API_KEY = "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"

def chatgpt_response(message):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'model': 'gpt-4',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': message},
        ],
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "ChatGPT API yanıtı alınamadı."

# Telegram mesajı gönderme (asenkron)
async def send_telegram_message(message):
    try:
        for chat_id in CHAT_IDS:
            await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Telegram mesaj gönderimi sırasında hata: {e}")

# Sensör verisi ve ChatGPT yanıtı ile mesaj oluşturma
async def create_telegram_message(predicted_smell, temperature, humidity):
    base_message = f"Tahmin edilen koku: {predicted_smell}\nSıcaklık: {temperature-19}°C\nNem: {humidity}%"
    # ChatGPT API'ye soruyu gönderelim
    message = f"{base_message}. Bu verilere göre ne yapmalıyım?"
    suggestion = chatgpt_response(message)
    full_message = f"{base_message}\nYorum: {suggestion}"
    await send_telegram_message(full_message)

# Modelle tahmin işlemi yapma ve sonucu Telegram'a gönderme
async def predict_smell(formatted_data, temperature, humidity):
    try:
        prediction = model.predict(formatted_data)
        label_map = {0: "Hava", 1: "Kahve", 2: "Kolonya", 3: "Parfüm"}
        predicted_smell = label_map[int(prediction[0])]
        print(f"Tahmin edilen koku: {predicted_smell}")

        # Telegram'a tahmin sonucunu gönder
        await create_telegram_message(predicted_smell, temperature, humidity)

    except Exception as e:
        print(f"Tahmin sırasında hata oluştu: {e}")

# Sensör verilerini sürekli dinleyen bir döngü
async def sensor_loop():
    global sensor_data_list  # Global değişkeni kullanacağımızı belirtiyoruz
    try:
        s = serial.Serial(SERIAL_PORT, baudrate=SERIAL_BAUD)  # Seri portu açıyoruz
        send_command(s, 'G')
        
        while True:
            if s.in_waiting:
                read_res = read_response(s)
                print(f"Sensör Verisi: {read_res}")
                
                formatted_data = format_sensor_data(read_res)
                if formatted_data is not None:
                    # Sıcaklık ve nem verilerini alıyoruz (son iki veri)
                    humidity = formatted_data[0][-2]  # 65. veri (nem)
                    temperature = formatted_data[0][-1]  # 66. veri (sıcaklık)
                    
                    # Kokuyu tahmin et ve sonucu Telegram'a gönder
                    await predict_smell(formatted_data, temperature, humidity)

                    # sensor_data_list global değişkenini güncelle
                    sensor_data_list = formatted_data.flatten().tolist()

            await asyncio.sleep(10)
    except serial.SerialException as e:
        print(f'Seri port hatası: {e}')
    except Exception as e:
        print(f'Genel hata: {e}')

# Seri port ayarları
SERIAL_PORT = 'COM3'  # Sensörünüzün bağlı olduğu seri portu doğru şekilde belirtin
SERIAL_BAUD = 115200  # Baud rate'inizi girin

# Verileri global olarak tutacağız
sensor_data_list = []

# Seri port üzerinden komut gönderme
def send_command(s, command):
    s.write(('%s\n' % command).encode())
    line = s.readline().decode()
    print(line.rstrip())

# Sensörden gelen cevabı okuma
def read_response(s):
    return s.readline().decode().rstrip()

# Sensör verisini formatlama (verileri modele uygun hale getirme)
def format_sensor_data(sensor_data):
    try:
        sensor_data = sensor_data.replace("start;", "").replace(";", ",")
        formatted_data = np.array([float(x) for x in sensor_data.split(",")])
        formatted_data = formatted_data.reshape(1, -1)
        return formatted_data
    except ValueError:
        print(f"Hatalı veri formatı atlandı: {sensor_data}")
        return None

# Flask rota: Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Flask rota: Sensör verilerini JSON formatında gönder
@app.route('/sensor_data')
def get_sensor_data():
    global sensor_data_list  # Global değişkeni kullanarak verileri JSON formatında döndürüyoruz
    return jsonify(sensor_data_list)

# Flask uygulamasını çalıştır
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Hem Flask web sunucusunu hem de sensör dinleyiciyi aynı anda çalıştırmak için iki farklı thread
if __name__ == "__main__":
    loop = asyncio.new_event_loop()  # DeprecationWarning için yeni bir event loop oluşturuyoruz
    asyncio.set_event_loop(loop)
    
    t1 = threading.Thread(target=run_flask)
    t1.start()
    loop.run_until_complete(sensor_loop())
