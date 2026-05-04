import cv2
import numpy as np
import os
import time

class CoCReturn:
    def __init__(self, device):
        self.device = device
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(self.base_dir, "assets")

    def back_to_home(self, timeout=30):
        """
        Menunggu dan mengklik tombol return_home.png.
        timeout: Batas waktu maksimal (detik) untuk mencari tombol.
        """
        path = os.path.join(self.assets_path, "return_home.png")
        template = cv2.imread(path, 0)
        
        if template is None:
            print("[!] File return_home.png tidak ditemukan di folder assets.")
            return False

        start_time = time.time()
        print("[*] Menunggu tombol Return Home muncul...")

        while time.time() - start_time < timeout:
            raw = self.device.screencap()
            if not raw:
                continue

            # Konversi ke grayscale untuk pencocokan cepat
            screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
            
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # Skor 0.75 cukup aman untuk tombol UI yang statis
            if max_val >= 0.65:
                h, w = template.shape
                cx, cy = max_loc[0] + w//2, max_loc[1] + h//2
                
                print(f"[+] Tombol ditemukan! Klik Return Home di {cx, cy} (Score: {max_val:.2f})")
                self.device.shell(f"input tap {cx} {cy}")
                return True
            
            # Beri jeda 2 detik sebelum scan ulang agar tidak membebani CPU
            time.sleep(2)

        print("[!] Timeout: Tombol Return Home tidak ditemukan.")
        return False