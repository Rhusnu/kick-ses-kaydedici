import subprocess
import time
import sys
import os
import requests

USERNAME = os.getenv("KICK_USERNAME")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CHUNK_DURATION = 60  # 45 dakika
MAX_RUN_TIME = 19800   # 5.5 saat

def send_to_telegram(file_path):
    print(f"Telegram'a gonderiliyor: {file_path}")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
    try:
        with open(file_path, 'rb') as audio:
            files = {'audio': audio}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': f"🎤 {USERNAME} Kick Yayini"}
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                print("Basariyla gonderildi!")
            else:
                print(f"Hata: {response.text}")
    except Exception as e:
        print(f"Gonderim sirasinda hata: {e}")

def get_stream_url():
    cmd = ["yt-dlp", "--get-url", f"https://kick.com/{USERNAME}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def main():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Sifreler (Secrets) bulunamadi!")
        sys.exit(1)

    start_time = time.time()
    chunk_index = 1
    while True:
        if time.time() - start_time >= MAX_RUN_TIME:
            break

        stream_url = get_stream_url()
        if not stream_url:
            time.sleep(60)
            continue

        filename = f"{USERNAME}_yayin_parca_{chunk_index}.m4a"
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", stream_url, 
            "-t", str(CHUNK_DURATION), 
            "-c:a", "aac", "-vn", filename
        ]
        
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 1000:
            send_to_telegram(filename)
            os.remove(filename)
            chunk_index += 1
        else:
            time.sleep(60)

if __name__ == "__main__":
    main()
