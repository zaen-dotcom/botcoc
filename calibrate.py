"""
Calibration Tool: Ambil screenshot dan gambar titik-titik deploy di atasnya.
Jalankan saat sudah masuk mode attack (setelah klik attack, sebelum deploy).
Hasilnya di-save ke calibrate_output.png - cek apakah titik-titik jatuh di zona hijau.
"""
import cv2
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from adb.connect import connect_device

def main():
    device = connect_device()
    if not device:
        print("[!] Device tidak terhubung")
        return

    raw = device.screencap()
    if not raw:
        print("[!] Gagal ambil screenshot")
        return

    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    print(f"[*] Screenshot: {w}x{h}")

    # --- TITIK DEPLOY TOP-LEFT (dikalibrasi v3) ---
    funnel_top  = (640, 90)
    funnel_left = (140, 350)
    main_start  = (600, 110)
    main_end    = (170, 330)

    # Gambar garis deploy utama
    cv2.line(img, main_start, main_end, (0, 255, 0), 2)
    cv2.line(img, funnel_top, main_start, (0, 255, 0), 1)
    cv2.line(img, funnel_left, main_end, (0, 255, 0), 1)

    # Funnel points (MERAH)
    cv2.circle(img, funnel_top, 12, (0, 0, 255), -1)
    cv2.putText(img, "F-TOP", (funnel_top[0]+15, funnel_top[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    cv2.circle(img, funnel_left, 12, (0, 0, 255), -1)
    cv2.putText(img, "F-LEFT", (funnel_left[0]+15, funnel_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    # Main deploy points - 8 naga (HIJAU)
    for i in range(8):
        t = i / 7
        x = int(main_start[0] + (main_end[0] - main_start[0]) * t)
        y = int(main_start[1] + (main_end[1] - main_start[1]) * t)
        cv2.circle(img, (x, y), 8, (0, 255, 0), -1)
        cv2.putText(img, f"N{i+1}", (x+10, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)

    # Balloon points (BIRU) - slight offset
    for i in range(16):
        t = i / 15
        x = int(main_start[0] + (main_end[0] - main_start[0]) * t) + 15
        y = int(main_start[1] + (main_end[1] - main_start[1]) * t) + 8
        cv2.circle(img, (x, y), 5, (255, 150, 0), -1)

    # Hero point (KUNING) - tengah garis
    mx = (main_start[0] + main_end[0]) // 2
    my = (main_start[1] + main_end[1]) // 2
    cv2.circle(img, (mx, my), 15, (0, 255, 255), 3)
    cv2.putText(img, "HERO", (mx+18, my), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    # Rage path (MAGENTA)
    rage = [(450,240),(550,310),(660,370),(750,430)]
    for i, (rx, ry) in enumerate(rage):
        cv2.circle(img, (rx, ry), 10, (255, 0, 255), 2)
        cv2.putText(img, f"R{i+1}", (rx+12, ry), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,0,255), 1)

    # Freeze path (CYAN)
    freeze = [(700,380),(780,430),(620,340)]
    for i, (fx, fy) in enumerate(freeze):
        cv2.circle(img, (fx, fy), 10, (255, 255, 0), 2)
        cv2.putText(img, f"FZ{i+1}", (fx+12, fy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,0), 1)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibrate_output.png")
    cv2.imwrite(out, img)
    print(f"[*] Saved: {out}")
    print("[*] Buka file tersebut dan cek:")
    print("    MERAH  = Funnel naga (harus di ujung zona hijau)")
    print("    HIJAU  = Naga utama (harus di sepanjang zona hijau)")
    print("    BIRU   = Balon (di belakang naga)")
    print("    KUNING = Heroes (di tengah)")
    print("    MAGENTA= Rage spells")
    print("    CYAN   = Freeze spells")

if __name__ == "__main__":
    main()
