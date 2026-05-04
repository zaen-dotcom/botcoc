import cv2
import numpy as np
import pytesseract
import os
import time

# Sesuaikan path Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class CoCLoot:
    def __init__(self, device):
        self.device = device
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(self.base_dir, "assets")
        self.threshold = 0.7 

    def get_number_from_region(self, screen, x, y, w, h):
        try:
            roi = screen[y-10:y+h+10, x+w:x+w+280]
            if roi.size == 0: return 0

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            
            _, thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            config = '--psm 7 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(thresh, config=config)
            
            clean_text = "".join(filter(str.isdigit, text))
            return int(clean_text) if clean_text else 0
        except Exception:
            return 0

    def find_and_click(self, asset_name):
        raw = self.device.screencap()
        if not raw: return False
        
        screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
        path = os.path.join(self.assets_path, f"{asset_name}.png")
        template = cv2.imread(path, 0)
        
        if template is None: return False

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= 0.7: 
            h, w = template.shape
            cx, cy = max_loc[0] + w//2, max_loc[1] + h//2
            self.device.shell(f"input tap {cx} {cy}")
            return True
        return False

    def check_loot(self, target_gold, target_elixir):
        raw = self.device.screencap()
        if not raw: return False
        
        screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        loot_found = {"gold": 0, "elixir": 0, "dark": 0}
        mapping = [("goldmusuh", "gold"), ("elixirmusuh", "elixir"), ("darkelixirmusuh", "dark")]

        for icon_name, key in mapping:
            path = os.path.join(self.assets_path, f"{icon_name}.png")
            template = cv2.imread(path, 0)
            if template is None: continue

            res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val >= 0.75:
                val = self.get_number_from_region(screen, max_loc[0], max_loc[1], template.shape[1], template.shape[0])
                loot_found[key] = val

        # Tetap tampilkan DE di log hanya untuk informasi saja
        print(f"\n[*] Loot Terdeteksi: G: {loot_found['gold']} | E: {loot_found['elixir']} | DE: {loot_found['dark']}")

        # Logika validasi: Hanya Gold dan Elixir
        meets_gold = loot_found["gold"] >= target_gold
        meets_elixir = loot_found["elixir"] >= target_elixir

        return meets_gold and meets_elixir