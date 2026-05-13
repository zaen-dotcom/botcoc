import cv2
import numpy as np
import os
import json
import time
import random

class CoCDeploy:
    def __init__(self, device):
        self.device = device
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(self.base_dir, "assets")
        self.record_path = os.path.join(self.base_dir, "config", "recorded_moves.json")

    def load_records(self):
        if not os.path.exists(self.record_path):
            print(f"[!] File {self.record_path} tidak ditemukan!")
            return {}
        with open(self.record_path, 'r') as f:
            return json.load(f)

    def scan_single_unit(self, unit_name, threshold=0.7):
        raw = self.device.screencap()
        if not raw: return None
        screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
        path = os.path.join(self.assets_path, f"{unit_name}.png")
        if not os.path.exists(path): return None
        template = cv2.imread(path, 0)
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            h, w = template.shape
            return (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return None

    def _tap_sync(self, x, y):
        # Hapus '&' agar perintah dikirim secara sinkron dan urut
        self.device.shell(f"input tap {x} {y}")

    def execute_deployment(self):
        records = self.load_records()
        if not records: return

        # Pengaturan Offset (Sesuaikan nilai ini!)
        # Jika deploy terlalu MAJU, kita kurangi nilainya (negatif)
        # Jika deploy terlalu KE KANAN, kita kurangi X-nya
        OFFSET_X = 0   
        OFFSET_Y = -65  # Menarik semua titik mundur 35 pixel ke atas/luar

        order = ["switch", "naga", "baloon", "warden", "king", "queen", "amarah", "freeze"]

        print(f"\n[*] Deploying with Offset Y: {OFFSET_Y} px untuk akurasi...")
        
        for unit in order:
            if unit not in records: continue

            pos_icon = self.scan_single_unit(unit)
            if pos_icon:
                print(f"[+] Deploying {unit.upper()}...")
                self.device.shell(f"input tap {pos_icon[0]} {pos_icon[1]}")
                time.sleep(0.7) 

                for i, coord in enumerate(records[unit]):
                    # TERAPKAN OFFSET DISINI
                    final_x = coord[0] + OFFSET_X
                    final_y = coord[1] + OFFSET_Y
                    
                    self._tap_sync(final_x, final_y)
                    time.sleep(0.05) 
                
                time.sleep(0.5)

    def start_timer(self):
        print("[*] Menunggu pertempuran 2m 15d...")
        time.sleep(60)
        print("[!] Selesai.")