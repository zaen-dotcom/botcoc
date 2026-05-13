"""
Tool untuk crop ulang template attack1 dari screenshot terkini
Jalankan: python recrop_attack.py
"""
import cv2
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from adb.connect import connect_device

def recrop_templates():
    device = connect_device()
    if not device:
        print("[!] Gagal konek ADB")
        return

    print("[*] Mengambil screenshot...")
    raw = device.screencap()
    if not raw:
        print("[!] Gagal screencap")
        return

    screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    h, w = screen.shape[:2]
    print(f"[*] Resolusi layar: {w}x{h}")

    assets = os.path.join(os.path.dirname(__file__), "assets")

    # ============================================================
    # Koordinat crop disesuaikan dengan layar 1920x1080 landscape
    # Sesuaikan region jika posisi tombol sedikit berbeda
    # ============================================================

    crops = {
        # Tombol "Attack!" kiri bawah - terlihat jelas di screenshot
        # Region: x_start, y_start, x_end, y_end
        "attack1": (0, 620, 175, 750),

        # Tombol "Find a Match" (muncul setelah klik Attack!) - perlu dikonfigurasi manual
        # Uncomment dan sesuaikan setelah klik Attack! duluan
        # "attack2": (???, ???, ???, ???),
    }

    for name, (x1, y1, x2, y2) in crops.items():
        # Pastikan koordinat dalam batas layar
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        crop = screen[y1:y2, x1:x2]
        if crop.size == 0:
            print(f"[!] Crop {name} kosong! Cek koordinat.")
            continue

        out_path = os.path.join(assets, f"{name}.png")
        # Backup template lama
        backup_path = os.path.join(assets, f"{name}_OLD.png")
        if os.path.exists(out_path):
            old = cv2.imread(out_path)
            cv2.imwrite(backup_path, old)
            print(f"[*] Backup lama disimpan: {name}_OLD.png (ukuran: {old.shape[1]}x{old.shape[0]})")

        cv2.imwrite(out_path, crop)
        print(f"[+] Template baru: {name}.png (ukuran: {crop.shape[1]}x{crop.shape[0]}) dari region ({x1},{y1})-({x2},{y2})")

        # Simpan preview dengan kotak merah di screenshot utuh
        preview = screen.copy()
        cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.putText(preview, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    # Simpan preview untuk verifikasi
    preview_path = os.path.join(assets, "recrop_preview.png")
    cv2.imwrite(preview_path, preview)
    print(f"\n[*] Preview disimpan: {preview_path}")
    print("[*] Buka recrop_preview.png untuk verifikasi posisi crop sudah benar!")

    # Verifikasi ulang score setelah crop baru
    print("\n--- VERIFIKASI ULANG ---")
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    for name in ["attack1"]:
        path = os.path.join(assets, f"{name}.png")
        template = cv2.imread(path, 0)
        if template is None: continue
        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        print(f"  {name}: score = {max_val:.4f} (lokasi: {max_loc})")
        if max_val >= 0.95:
            print("  [OK] Score sempurna! Template siap digunakan.")
        elif max_val >= 0.72:
            print("  [OK] Score cukup, akan terdeteksi.")
        else:
            print("  [!!] Score masih rendah. Coba sesuaikan koordinat crop di atas.")

if __name__ == "__main__":
    recrop_templates()
