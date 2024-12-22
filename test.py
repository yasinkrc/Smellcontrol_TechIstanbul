import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# CSV dosyasını oku
file_path = r"C:\Users\ismai\Downloads\perfumm.csv"  # Dosya yolunu düzelttim
df = pd.read_csv(file_path)

# Kullanıcıdan yeni satır eklemek için tüm sütunlara uygun değerleri alalım
new_row = {}
for column in df.columns:
    value = input(f"{column} için yeni değeri girin: ")
    new_row[column] = value

# Yeni satırı DataFrame'e ekle
new_row_df = pd.DataFrame([new_row])  # Yeni satırı DataFrame olarak oluştur
df = pd.concat([df, new_row_df], ignore_index=True)  # Yeni satırı eklemek için pd.concat kullan

# Dosyayı tekrar CSV olarak kaydet
save_path = 'updated_file.csv'  # Kaydedilecek yeni dosya ismi
df.to_csv(save_path, index=False)

print(f"Yeni dosya '{save_path}' olarak kaydedildi.")
