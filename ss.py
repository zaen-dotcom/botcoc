import cv2
import numpy as np
import pyautogui
import os

# Konfigurasi
WIN_NAME = "CoC_Asset_Grabber"
SAVE_DIR = "assets"

def setup_directory():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def main():
    setup_directory()
    cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN_NAME, 960, 540)
    
    print("=== CoC Asset Grabber (Stable Mode) ===")
    print("- 'S' : Ambil Gambar")
    print("- 'Q' : Keluar")
    print("---------------------------------------")

    try:
        while True:
            # Screenshot real-time
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            cv2.imshow(WIN_NAME, frame)
            
            # Cek input keyboard (1ms)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):
                print("\n[!] FREEZE: Silakan tarik kotak di jendela OpenCV lalu tekan ENTER.")
                
                # Biarkan user pilih ROI
                roi = cv2.selectROI(WIN_NAME, frame, fromCenter=False, showCrosshair=True)
                
                if roi[2] > 0 and roi[3] > 0:
                    x, y, w, h = [int(v) for v in roi]
                    cropped_img = frame[y:y+h, x:x+w]
                    
                    # Tampilkan preview kecil agar Anda yakin
                    preview_name = "Preview (Tekan sembarang tombol)"
                    cv2.imshow(preview_name, cropped_img)
                    cv2.waitKey(500) # Intip sebentar 0.5 detik

                    # PINDAH KE TERMINAL
                    print(f"\n[COORD] X:{x} Y:{y} W:{w} H:{h}")
                    file_name = input(">> Masukkan nama file (atau Enter untuk batal): ").strip()
                    
                    if file_name:
                        path = os.path.join(SAVE_DIR, f"{file_name}.png")
                        cv2.imwrite(path, cropped_img)
                        print(f"[SUCCESS] Tersimpan di {path}")
                    
                    cv2.destroyWindow(preview_name)
                    # Kembalikan fokus ke jendela utama
                    cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_TOPMOST, 1)
                else:
                    print("[!] Seleksi dibatalkan.")
                
                print("\n[*] Kembali ke mode LIVE. Siap ambil gambar lagi...")

            elif key == ord('q'):
                print("[*] Keluar...")
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()