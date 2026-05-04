import cv2
import numpy as np
import os
import time

class CoCAttack:
    def __init__(self, device):
        self.device = device
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(self.base_dir, "assets")
        
        # Pre-load grayscale templates ke RAM agar tidak baca disk terus-menerus
        self.templates = {}
        for name in ["attack1", "attack2", "attack3"]:
            path = os.path.join(self.assets_path, f"{name}.png")
            if os.path.exists(path):
                self.templates[name] = cv2.imread(path, 0)

    def run_attack_sequence(self):
        # 1. Ambil screenshot SATU KALI saja (Hemat waktu 1-2 detik)
        start_time = time.time()
        raw = self.device.screencap()
        if not raw: return False
        
        screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
        
        # 2. Cek semua tombol dalam satu frame memori
        # Gunakan urutan terbalik agar jika attack3 sudah ada, bot langsung eksekusi
        for name in ["attack3", "attack2", "attack1"]:
            template = self.templates.get(name)
            if template is None: continue

            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # Threshold adaptif
            thresh = 0.65 if name == "attack1" else 0.85

            if max_val >= thresh:
                h, w = template.shape
                cx, cy = max_loc[0] + w//2, max_loc[1] + h//2
                
                # Filter koordinat sampah
                if cx < 10 or cy < 10: continue

                # Eksekusi Klik
                print(f"[+] {name.upper()} ({max_val:.2f}) -> Tap: {cx}, {cy} | Latency: {time.time()-start_time:.2f}s")
                self.device.shell(f"input tap {cx} {cy}")
                
                # Jeda transisi UI (diperkecil agar lebih ngebut)
                wait = 2.0 if name == "attack3" else 0.5
                time.sleep(wait)
                return True
                
        return False