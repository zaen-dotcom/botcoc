import time
import sys
import os
import cv2
import numpy as np
import threading
import customtkinter as ctk
from datetime import datetime

# Setup Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adb.connect import connect_device
from core.attack import CoCAttack 
from core.loot import CoCLoot
from core.deploy import CoCDeploy
from core.balik import CoCReturn 
from core.handler import CoCHandler

class CoCBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Judul & Ukuran Window
        self.title("Bot CoC Auto")
        self.geometry("700x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.is_running = False
        self.attack_count = 0

        # --- UI LAYOUT ---
        self.grid_columnconfigure(0, weight=1)

        # Header Title
        self.header = ctk.CTkLabel(self, text="BOT COC AUTO", font=ctk.CTkFont(size=26, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sub_header = ctk.CTkLabel(self, text="Advanced Farming Dashboard", font=ctk.CTkFont(size=14))
        self.sub_header.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Input Frame (Target Loot)
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.lbl_gold = ctk.CTkLabel(self.frame_input, text="Min Gold:")
        self.lbl_gold.grid(row=0, column=0, padx=(20, 5), pady=20)
        self.entry_gold = ctk.CTkEntry(self.frame_input, width=120)
        self.entry_gold.insert(0, "400000")
        self.entry_gold.grid(row=0, column=1, padx=5, pady=20)

        self.lbl_elixir = ctk.CTkLabel(self.frame_input, text="Min Elixir:")
        self.lbl_elixir.grid(row=0, column=2, padx=(20, 5), pady=20)
        self.entry_elixir = ctk.CTkEntry(self.frame_input, width=120)
        self.entry_elixir.insert(0, "400000")
        self.entry_elixir.grid(row=0, column=3, padx=5, pady=20)

        # Buttons Frame
        self.frame_btn = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btn.grid(row=3, column=0, padx=20, pady=10)

        self.btn_start = ctk.CTkButton(self.frame_btn, text="START BOT", fg_color="#2ecc71", hover_color="#27ae60", 
                                       font=ctk.CTkFont(weight="bold"), command=self.start_thread)
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_stop = ctk.CTkButton(self.frame_btn, text="STOP BOT", fg_color="#e74c3c", hover_color="#c0392b", 
                                      font=ctk.CTkFont(weight="bold"), command=self.stop_bot)
        self.btn_stop.grid(row=0, column=1, padx=10)

        # Log Box
        self.log_box = ctk.CTkTextbox(self, width=650, height=250, font=("Consolas", 12))
        self.log_box.grid(row=4, column=0, padx=20, pady=20)
        self.add_log("System Ready. Masukkan target dan tekan START.")

    def add_log(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{now}] {text}\n")
        self.log_box.see("end")

    def stop_bot(self):
        self.is_running = False
        self.add_log("Bot akan berhenti setelah siklus ini.")

    def start_thread(self):
        if not self.is_running:
            self.is_running = True
            self.btn_start.configure(state="disabled")
            thread = threading.Thread(target=self.bot_loop, daemon=True)
            thread.start()

    def bot_loop(self):
        try:
            t_gold = int(self.entry_gold.get())
            t_elixir = int(self.entry_elixir.get())
            
            device = connect_device()
            if not device:
                self.add_log("ERROR: Device tidak terdeteksi!")
                return

            bot_attack = CoCAttack(device)
            bot_loot = CoCLoot(device)
            bot_deploy = CoCDeploy(device)
            bot_return = CoCReturn(device)
            bot_handler = CoCHandler(device)

            self.add_log("Bot Berjalan...")

            while self.is_running:
                bot_handler.check_and_clear(ignore_battle_buttons=True)
                
                res = bot_attack.run_attack_sequence()
                if res:
                    if res == "attack3": self.add_log("Mencari Match...")
                    continue

                raw = device.screencap()
                if not raw: continue
                
                # Cek apakah sudah di map lawan
                screen = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
                next_path = os.path.join(bot_loot.assets_path, "next.png")
                
                if os.path.exists(next_path):
                    match = cv2.matchTemplate(screen, cv2.imread(next_path, 0), cv2.TM_CCOEFF_NORMED)
                    if cv2.minMaxLoc(match)[1] < 0.7:
                        time.sleep(2)
                        continue
                else:
                    continue

                # Baca Loot
                if bot_loot.check_loot(t_gold, t_elixir):
                    self.attack_count += 1
                    self.add_log(f"TARGET MATCH! Serangan #{self.attack_count}")
                    bot_deploy.execute_deployment()
                    
                    # Monitoring
                    start_t = time.time()
                    while time.time() - start_t < 210 and self.is_running:
                        bot_handler.check_and_clear(ignore_battle_buttons=False)
                        if bot_return.back_to_home(timeout=5): break
                        time.sleep(5)
                    
                    self.add_log("Kembali ke desa. Menunggu...")
                    time.sleep(2)
                else:
                    self.add_log("Loot tidak cocok. Next...")
                    bot_loot.find_and_click("next")
                    time.sleep(3)

        except Exception as e:
            self.add_log(f"CRITICAL ERROR: {e}")
        finally:
            self.is_running = False
            self.btn_start.configure(state="normal")
            self.add_log("Bot Berhenti.")

if __name__ == "__main__":
    app = CoCBotGUI()
    app.mainloop()