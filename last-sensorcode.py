import serial
import serial.tools.list_ports
import sys
import numpy as np
import joblib  # Modeli yüklemek için
import time

sys.stdout.reconfigure(encoding='utf-8')

# Modeli yükleyelim (önceden kaydedildiğini varsayıyoruz)
model = joblib.load('C:/Astroit/smell_model.pkl')

# Seri port ayarları
SERIAL_PORT = 'COM3'  # Seri portunuzu girin
SERIAL_BAUD = 115200  # Baud rate'inizi girin

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
        # "start;" kısmını çıkar ve ";" yerine "," ile değiştir
        sensor_data = sensor_data.replace("start;", "").replace(";", ",")
        
        # String veriyi sayısal değerlere çevir
        formatted_data = np.array([float(x) for x in sensor_data.split(",")])
        
        # Veriyi modele uygun hale getir (2D array)
        formatted_data = formatted_data.reshape(1, -1)
        
        return formatted_data
    except ValueError:
        print(f"Hatalı veri formatı atlandı: {sensor_data}")
        return None  # Eğer hata varsa None dönüyoruz

# Modelle tahmin işlemi yapma
def predict_smell(formatted_data):
    try:
        prediction = model.predict(formatted_data)
        
        # Tahmin edilen sınıfı yazdır (0: Hava, 1: Kahve, 2: Kolonya, 3: Parfüm)
        label_map = {0: "Hava", 1: "Kahve", 2: "Kolonya", 3: "Parfüm"}
        print(f"Tahmin edilen koku: {label_map[int(prediction[0])]}")
    except Exception as e:
        print(f"Tahmin sırasında hata oluştu: {e}")

# Ana fonksiyon
try:
    s = serial.Serial(SERIAL_PORT, baudrate=SERIAL_BAUD)
    ports = serial.tools.list_ports.comports()
    
    send_command(s, 'G')  # Sensöre başlangıç komutu gönder (örneğin 'G')
    
    sensors = []
    while True:
        if s.in_waiting:
            # Sensörden veri oku
            read_res = read_response(s)
            sensors.append(read_res)
            print(f"Sensör Verisi: {sensors[-1]}")
            
            # Sensör verisini formatla
            formatted_data = format_sensor_data(sensors[-1])
            
            # Eğer veri formatlanabiliyorsa, modele tahmin yaptır
            if formatted_data is not None:
                predict_smell(formatted_data)
            
            # Listeyi her tahmin işleminden sonra temizle
            sensors = []
            
        time.sleep(5)  # 5 saniye bekle
except serial.SerialException as e:
    print(f'Seri port hatası: {e}')
except Exception as e:
    print(f'Genel hata: {e}')