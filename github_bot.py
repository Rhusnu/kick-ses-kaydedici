import subprocess
import sys
import os
import requests

USERNAME = os.getenv("KICK_USERNAME")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
    requests.post(url, data=data)

def upload_to_gofile(file_path):
    print("Gofile sunucusu araniyor...")
    try:
        server_res = requests.get("https://api.gofile.io/servers").json()
        if server_res["status"] != "ok":
            return None
        server = server_res["data"]["servers"][0]["name"]
        
        print(f"Sunucu bulundu: {server}. Yukleme basliyor...")
        url = f"https://{server}.gofile.io/contents/uploadfile"
        with open(file_path, 'rb') as f:
            upload_res = requests.post(url, files={'file': f}).json()
        
        if upload_res["status"] == "ok":
            return upload_res["data"]["downloadPage"]
    except Exception as e:
        print(f"Gofile yukleme hatasi: {e}")
    return None

def is_live():
    cmd = ["yt-dlp", "--simulate", f"https://kick.com/{USERNAME}"]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except:
        return False

def main():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not USERNAME:
        print("Sifreler eksik!")
        sys.exit(1)

    print(f"{USERNAME} yayin durumu kontrol ediliyor...")
    
    if not is_live():
        print("Yayin kapali. Islem bitiriliyor.")
        sys.exit(0)
        
    print("Yayin acik! Kayit basliyor...")
    send_telegram_message(f"🔴 {USERNAME} yayina girdi! Kayit (360p Video - 60 SANIYELIK TEST) basladi.")
    
    filename = f"{USERNAME}_yayin.mp4"
    
    cmd = [
        "yt-dlp",
        "-f", "best[height<=360]",
        "--downloader", "ffmpeg",
        "--downloader-args", "ffmpeg:-t 60",
        "-o", filename,
        f"https://kick.com/{USERNAME}"
    ]
    subprocess.run(cmd)
    
    if os.path.exists(filename) and os.path.getsize(filename) > 100000:
        print("Kayit bitti. Gofile'a yukleniyor...")
        gofile_link = upload_to_gofile(filename)
        
        if gofile_link:
            msg = f"✅ Test kaydi bitti ve sisteme yuklendi!\n\nIzlemek veya Indirmek icin tikla:\n👉 {gofile_link}"
            send_telegram_message(msg)
        else:
            send_telegram_message("❌ Yayin bitti ama Gofile'a yuklenirken bir hata olustu.")
    else:
        send_telegram_message("❌ Yayin sirasinda bir kopma oldu veya dosya kaydedilemedi.")

if __name__ == "__main__":
    main()
