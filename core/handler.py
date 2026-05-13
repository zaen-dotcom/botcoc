import cv2
import numpy as np
import os
import time

class CoCHandler:
    def __init__(self, device):
        self.device = device
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(self.base_dir, "assets")

    def check_and_clear(self, ignore_battle_buttons=True):
        """
        Mengecek gangguan teknis saja (Koneksi & Popup).
        Logika klik End dan Surrender sementara dinonaktifkan.
        """
        # Hanya fokus pada gangguan sistem/koneksi
        obstacles = [
            ("try", "Connection Error / Try Again"),
            ("reload", "Game Client Timeout / Reload"),
            ("okay", "Popup Okay / Bonus Clan"),
        ]
        
        raw = self.device.screencap()
        if not raw: return False
        
        # Menggunakan Grayscale agar deteksi cepat
        screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
        cleared = False

        for asset, label in obstacles:
            path = os.path.join(self.assets_path, f"{asset}.png")
            if not os.path.exists(path): continue
            
            template = cv2.imread(path, 0)
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # Threshold 0.8 untuk tombol UI statis
            if max_val >= 0.8:
                h, w = template.shape
                cx, cy = max_loc[0] + w//2, max_loc[1] + h//2
                print(f"[!] Gangguan Terdeteksi: {label} ({max_val:.2f}). Membersihkan...")
                
                # Klik tombol pengganggu (Reload/Try Again/Okay)
                self.device.shell(f"input tap {cx} {cy}")
                cleared = True
                
                # Jeda khusus untuk reload agar game sempat loading
                if asset in ["reload", "try"]:
                    print("[*] Menunggu game loading ulang (10 detik)...")
                    time.sleep(10)
                else:
                    time.sleep(2)
        
        return cleared