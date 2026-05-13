import cv2
import numpy as np
import os
import time

class CoCAttack:
    def __init__(self, device):
        self.device = device
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(self.base_dir, "assets")
        
        self.templates = {}
        # Pre-load semua tombol attack agar eksekusi cepat
        for name in ["attack1", "attack2", "attack3"]:
            path = os.path.join(self.assets_path, f"{name}.png")
            if os.path.exists(path):
                self.templates[name] = cv2.imread(path, 0)
            else:
                print(f"[!] Template tidak ditemukan: {name}.png")

    def run_attack_sequence(self):
        # Ambil screenshot
        raw = self.device.screencap()
        if not raw: return False
        
        screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
        
        # Cek dari step terjauh dulu (3→2→1) agar bot tidak mundur
        # ke step sebelumnya jika sudah progress ke step berikutnya
        for name in ["attack3", "attack2", "attack1"]:
            template = self.templates.get(name)
            if template is None: continue

            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # attack1 = tombol "Attack!" di Home
            # attack2 = tombol lanjutan di menu attack
            # attack3 = tombol "Find a Match" / konfirmasi terakhir sebelum loading
            thresh = 0.72 if name == "attack1" else 0.75

            if max_val >= thresh:
                h, w = template.shape
                cx, cy = max_loc[0] + w//2, max_loc[1] + h//2
                
                print(f"[+] {name.upper()} DETECTED ({max_val:.2f}) -> Tap: {cx}, {cy}")
                self.device.shell(f"input tap {cx} {cy}")
                
                time.sleep(2)
                return name  # Kembalikan nama tombol yang diklik
                
        return None