import sys
import os

# Mencari folder root (botcoc)
# os.path.dirname(__file__) adalah folder 'tools'
# dirname kedua naik ke folder 'botcoc'
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from adb.connect import connect_device

def grab_screen():
    device = connect_device()
    if device:
        print("[*] Mengambil raw screenshot dari ADB...")
        screen_bytes = device.screencap()
        
        # Tentukan path simpan ke folder assets di root
        save_path = os.path.join(ROOT_DIR, "assets", "raw_adb_view.png")
        
        # Pastikan folder assets ada
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
            
        with open(save_path, "wb") as f:
            f.write(screen_bytes)
        print(f"[OK] File berhasil disimpan di: {save_path}")

if __name__ == "__main__":
    grab_screen()