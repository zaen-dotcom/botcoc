import cv2
import numpy as np
import os
import json
import time

class CoCDeploy:
    def __init__(self, device):
        self.device = device
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(self.base_dir, "assets")
        self.config_path = os.path.join(self.base_dir, "config", "troops.json")

    def load_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def scan_single_unit(self, unit_name):
        """Mencari koordinat ikon unit secara real-time."""
        raw = self.device.screencap()
        if not raw: return None
        screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
        path = os.path.join(self.assets_path, f"{unit_name}.png")
        if not os.path.exists(path): return None
        
        template = cv2.imread(path, 0)
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val >= 0.7:
            h, w = template.shape
            return (max_loc[0] + w//2, max_loc[1] + h//2)
        return None

    def execute_deployment(self):
        config = self.load_config()
        
        # Koordinat pojok kiri bawah (Area Laut/Pinggir) yang lebih stabil
        # X kita buat 80 agar benar-benar di pinggir
        safe_line = [(80, 400), (80, 500), (80, 600), (80, 700)]

        # URUTAN: NAGA -> WARDEN -> BALOON -> KING -> QUEEN
        order = ["naga", "warden", "baloon", "king", "queen"]

        for unit in order:
            pos = self.scan_single_unit(unit)
            if pos:
                print(f"[*] Menyiapkan {unit}...")
                # Pilih ikon (Hapus & agar fokus memilih ikon dulu)
                self.device.shell(f"input tap {pos[0]} {pos[1]}")
                time.sleep(0.4) # Jeda agar game sempat 'highlight' ikonnya

                if unit in ["naga", "baloon"]:
                    count = config['troops'].get(unit, 0)
                    print(f"[*] Melepas {count} {unit}...")
                    for i in range(count + 2):
                        tx, ty = safe_line[i % len(safe_line)]
                        # Kirim perintah tap tanpa '&' tapi dengan jeda tipis 0.08
                        self.device.shell(f"input tap {tx} {ty}")
                        time.sleep(0.08) # Jeda optimal agar tidak macet
                else:
                    # Untuk Hero (Warden/King/Queen)
                    print(f"[*] Melepas Hero: {unit}")
                    self.device.shell(f"input tap 100 550")
                    time.sleep(0.2)

        # SPELLS
        for spell in ["amarah", "freeze"]:
            pos = self.scan_single_unit(spell)
            if pos:
                self.device.shell(f"input tap {pos[0]} {pos[1]}")
                time.sleep(0.5)
                target = (500, 550) if spell == "amarah" else (960, 540)
                self.device.shell(f"input tap {target[0]} {target[1]}")
                time.sleep(1)