"""import openai

# OpenAI API anahtarınızı buraya ekleyin
openai.api_key = "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"

# ChatGPT API kullanarak yorum oluşturma
async def create_chatgpt_response(predicted_smell, temperature, humidity):
    try:
        prompt = f"Tahmin edilen koku: {predicted_smell}, sıcaklık: {temperature}, nem: {humidity}. Bu verilere göre ne önerirsiniz?"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        chat_response = response.choices[0].text.strip()
        return chat_response
    except Exception as e:
        print(f"ChatGPT API isteği sırasında hata: {e}")
        return "Veriler yorumlanırken hata oluştu."

# Modelle tahmin işlemi yapma ve ChatGPT API kullanarak sonuçları yorumlama
async def predict_and_analyze_smell(formatted_data, temperature, humidity):
    try:
        prediction = model.predict(formatted_data)
        label_map = {0: "Hava", 1: "Kahve", 2: "Kolonya", 3: "Parfüm"}
        predicted_smell = label_map[int(prediction[0])]
        print(f"Tahmin edilen koku: {predicted_smell}")

        # ChatGPT API ile yorum oluştur
        chat_response = await create_chatgpt_response(predicted_smell, temperature, humidity)

        # Telegram'a tahmin sonucunu ve ChatGPT yorumunu gönder
        message = f"Tahmin edilen koku: {predicted_smell}\nSıcaklık: {temperature}°C\nNem: {humidity}%\n\n{chat_response}"
        await send_telegram_message(message)

    except Exception as e:
        print(f"Tahmin sırasında hata oluştu: {e}")

# Sensör verilerini sürekli dinleyen bir döngü
def sensor_loop():
    global sensor_data_list
    try:
        s = serial.Serial(SERIAL_PORT, baudrate=SERIAL_BAUD)
        send_command(s, 'G')
        
        while True:
            if s.in_waiting:
                read_res = read_response(s)
                print(f"Sensör Verisi: {read_res}")
                
                formatted_data = format_sensor_data(read_res)
                if formatted_data is not None:
                    sensor_data_list = formatted_data.flatten().tolist()
                    temperature = sensor_data_list[65]  # Sıcaklık verisi
                    humidity = sensor_data_list[64]     # Nem verisi
                    asyncio.run(predict_and_analyze_smell(formatted_data, temperature, humidity))

            time.sleep(10)
    except serial.SerialException as e:
        print(f'Seri port hatası: {e}')
    except Exception as e:
        print(f'Genel hata: {e}')
        """