import serial
import serial.tools.list_ports
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

SERIAL_PORT = 'COM3'  # Seri portunuzu girin
SERIAL_BAUD = 112500  # Baud rate'inizi girin

def send_command(s, command):
    s.write(('%s\n' % command).encode())
    line = s.readline().decode()
    print(line.rstrip())

def read_response(s):
    return s.readline().decode().rstrip()

def send_data_to_flask(data):
    url = "http://127.0.0.1:5000/generate_features"
    try:
        response = requests.post(url, json={'features': data})
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to Flask: {e}")

try:
    s = serial.Serial(SERIAL_PORT, baudrate=SERIAL_BAUD)
    ports = serial.tools.list_ports.comports()
    send_command(s, 'G')
    sensors = []
    while True:
        if s.in_waiting:
            read_res = read_response(s)
            sensors.append(read_res)
            print("%s" % (sensors[-1]))
            send_data_to_flask(sensors)  # Flask uygulamasına veriyi gönder
            sensors = []  # Her bir veriyi gönderdikten sonra listeyi temizle
except serial.SerialException as e:
    print('ERROR: %s' % e)
