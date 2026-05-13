"""
Debug: Screenshot layar & cek semua template score
Jalankan: python debug_screen.py
"""
import cv2
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from adb.connect import connect_device

def run_debug():
    device = connect_device()
    if not device:
        print("[!] Gagal konek ADB")
        return

    print("\n[*] Mengambil screenshot layar saat ini...")
    raw = device.screencap()
    if not raw:
        print("[!] Gagal ambil screenshot")
        return

    # Simpan screenshot mentah untuk dilihat
    screen_bgr = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)

    out_path = os.path.join(os.path.dirname(__file__), "assets", "debug_current_screen.png")
    cv2.imwrite(out_path, screen_bgr)
    print(f"[*] Screenshot disimpan: {out_path}")
    print(f"[*] Ukuran layar: {screen_bgr.shape[1]}x{screen_bgr.shape[0]}\n")

    # Daftar semua template yang akan dicek
    assets_path = os.path.join(os.path.dirname(__file__), "assets")
    templates_to_check = [
        ("attack1", 0.72),
        ("attack2", 0.75),
        ("attack3", 0.72),
        ("next",    0.70),
        ("end",     0.80),
        ("surend",  0.80),
        ("okay",    0.80),
        ("try",     0.80),
        ("reload",  0.80),
        ("return_home", 0.65),
    ]

    print(f"{'Template':<20} {'Score':>8}  {'Threshold':>10}  {'Status':>10}")
    print("-" * 60)

    for name, thresh in templates_to_check:
        path = os.path.join(assets_path, f"{name}.png")
        if not os.path.exists(path):
            print(f"{name:<20} {'FILE TIDAK ADA':>30}")
            continue

        template = cv2.imread(path, 0)
        if template is None:
            print(f"{name:<20} {'GAGAL BACA':>30}")
            continue

        th, tw = template.shape
        sh, sw = screen_gray.shape

        # Cek apakah template lebih besar dari layar
        if th > sh or tw > sw:
            print(f"{name:<20} {'TEMPLATE > LAYAR':>30}  (template: {tw}x{th}, layar: {sw}x{sh})")
            continue

        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        status = "[OK] DETECTED" if max_val >= thresh else "[--]"
        print(f"{name:<20} {max_val:>8.4f}  {thresh:>10.2f}  {status:>10}")

        # Jika terdeteksi, gambar kotak merah di screenshot debug
        if max_val >= thresh:
            cx = max_loc[0] + tw // 2
            cy = max_loc[1] + th // 2
            print(f"  └─ Lokasi: ({cx}, {cy})")
            cv2.rectangle(screen_bgr,
                          (max_loc[0], max_loc[1]),
                          (max_loc[0]+tw, max_loc[1]+th),
                          (0, 0, 255), 2)
            cv2.putText(screen_bgr, name, (max_loc[0], max_loc[1]-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    # Simpan screenshot dengan kotak deteksi
    annotated_path = os.path.join(os.path.dirname(__file__), "assets", "debug_annotated.png")
    cv2.imwrite(annotated_path, screen_bgr)
    print(f"\n[*] Screenshot teranotasi disimpan: {annotated_path}")
    print("[*] Buka file debug_annotated.png untuk melihat hasilnya!")

if __name__ == "__main__":
    run_debug()
