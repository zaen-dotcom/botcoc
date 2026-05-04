import time
import sys
import os

# Menambahkan path agar Python bisa melihat ke dalam folder adb dan core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adb.connect import connect_device
from core.attack import CoCAttack 
from core.loot import CoCLoot
from core.deploy import CoCDeploy
# Ganti dari core.return menjadi core.balik
from core.balik import CoCReturn 

def main():
    print("="*40)
    print("      COC AUTO-ATTACK STARTING      ")
    print("      FULL AUTO: SEARCH & DEPLOY     ")
    print("="*40)

    # 1. Input Target Loot
    try:
        print("\n[CONFIG] Masukkan Target Loot Musuh:")
        target_gold = int(input(">> Min Gold: ") or 100000)
        target_elixir = int(input(">> Min Elixir: ") or 100000)
    except ValueError:
        print("[!] Input salah. Menggunakan default 100k.")
        target_gold, target_elixir = 100000, 100000

    # 2. Inisialisasi Koneksi
    device = connect_device()
    if not device:
        print("\n[!] Gagal menginisialisasi device.")
        return

    # 3. Inisialisasi Modul
    bot_attack = CoCAttack(device)
    bot_loot = CoCLoot(device)
    bot_deploy = CoCDeploy(device)
    bot_return = CoCReturn(device) 

    print("\n[*] Bot Ready. Mencari lawan...")

    try:
        while True:
            # LANGKAH A: Navigasi
            if bot_attack.run_attack_sequence():
                print("[*] Berpindah menu / Mencari lawan...")
                time.sleep(3)
                continue 

            # LANGKAH B: Cek Loot
            is_match = bot_loot.check_loot(target_gold, target_elixir)

            if is_match:
                print("\n" + "!"*40)
                print("   TARGET DITEMUKAN! MEMULAI SERANGAN   ")
                print("!"*40)
                
                # LANGKAH C: Deployment
                bot_deploy.execute_deployment()
                
                print("\n[*] Serangan selesai dideploy.")
                
                # LANGKAH D: Monitoring Selesai Pertandingan via balik.py
                if bot_return.back_to_home(timeout=240):
                    print("[*] Berhasil kembali ke Desa.")
                else:
                    print("[!] Gagal menemukan jalan pulang otomatis.")
                
                break
                
            else:
                # LANGKAH E: Klik Next
                print("[*] Loot tidak sesuai target. Mencari NEXT...")
                if bot_loot.find_and_click("next"):
                    print("[+] NEXT! Menunggu base berikutnya...")
                    time.sleep(5) 
                else:
                    time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Bot dihentikan oleh user.")
    except Exception as e:
        print(f"\n[!] Terjadi error pada main loop: {e}")
    finally:
        print("\n" + "="*40)
        print("           BOT SHUTDOWN             ")
        print("="*40)

if __name__ == "__main__":
    main()