import cv2
import numpy as np
from ppadb.client import Client as AdbClient
import io
from PIL import Image
import subprocess
import os
import time

# --- PENGATURAN PATH ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "tools", "adb.exe")

def init_adb_connection():
    try:
        if not os.path.exists(ADB_PATH):
            print(f"[!] File adb.exe tidak ditemukan di: {ADB_PATH}")
            return False
            
        # Jalankan server
        subprocess.run([ADB_PATH, "start-server"], capture_output=True)
        # Paksa koneksi ke BlueStacks port 5555
        subprocess.run([ADB_PATH, "connect", "127.0.0.1:5555"], capture_output=True)
        return True
    except Exception as e:
        print(f"[!] Error ADB: {e}")
        return False

def connect_device():
    if not init_adb_connection(): return None
    client = AdbClient(host="127.0.0.1", port=5037)
    try:
        devices = client.devices()
        if len(devices) == 0: return None
        device = devices[0]
        print(f"[*] Berhasil Terhubung ke: {device.serial}")
        return device
    except Exception:
        return None

def get_screenshot(device):
    """Fungsi ini tetap ada agar Bot bisa 'melihat' layar tanpa menampilkannya"""
    try:
        image_bytes = device.screencap()
        image = Image.open(io.BytesIO(image_bytes))
        frame = np.array(image)
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    except:
        return None

def main():
    device = connect_device()
    
    if not device:
        print("[!] Gagal memulai. Pastikan BlueStacks ON dan Port 5555 tersedia.")
        return

    print("\n" + "="*30)
    print(" BOT COC RUNNING IN BACKGROUND")
    print(" Tekan CTRL+C di Terminal untuk berhenti")
    print("="*30 + "\n")

    # Di sini nanti adalah tempat logika auto-attack Anda bekerja
    # Untuk sementara kita buat loop kosong agar skrip tidak langsung mati
    try:
        while True:
            # Contoh: bot mengambil gambar setiap 2 detik untuk diproses
            # frame = get_screenshot(device)
            # print("[*] Bot sedang memantau layar...")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Bot dihentikan.")

if __name__ == "__main__":
    main()