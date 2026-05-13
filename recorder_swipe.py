import json
import os
import sys
import time
from pynput import mouse, keyboard

# Global State
recording = False
current_unit = None
data = {}
temp_moves = []
start_pos = None
start_time = None

print("="*40)
print("   CoC MACRO RECORDER (SWIPE SUPPORT)   ")
print("="*40)
print("Cara Pakai:")
print("1. Tekan huruf unit (N, B, W, K, Q, A, F).")
print("2. Klik biasa = TAP.")
print("3. Klik lalu seret = SWIPE.")
print("4. Tekan 'S' untuk SAVE unit tersebut.")
print("5. Tekan 'ESC' untuk simpan file & keluar.")
print("="*40)

def on_click(x, y, button, pressed):
    global recording, temp_moves, current_unit, start_pos, start_time
    
    if not recording:
        return

    if pressed:
        # Mencatat titik awal dan waktu mulai klik
        start_pos = (int(x), int(y))
        start_time = time.time()
    else:
        # Saat tombol dilepas, hitung jarak dan durasi
        end_pos = (int(x), int(y))
        duration = int((time.time() - start_time) * 1000) # Durasi dalam milidetik
        
        # Hitung jarak geser (Euclidean distance sederhana)
        dist = ((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)**0.5
        
        if dist > 20: # Jika geser lebih dari 20 pixel, anggap SWIPE
            move = ["swipe", start_pos[0], start_pos[1], end_pos[0], end_pos[1], duration]
            label = "SWIPE"
        else: # Jika jarak sangat kecil, anggap TAP
            move = ["tap", start_pos[0], start_pos[1]]
            label = "TAP"
            
        temp_moves.append(move)
        sys.stdout.write(f"\r[REC] {current_unit.upper()}: {label} ke-{len(temp_moves)} recorded.   ")
        sys.stdout.flush()

def on_press(key):
    global recording, current_unit, temp_moves, data
    try:
        if hasattr(key, 'char') and key.char is not None:
            k = key.char.lower()
        else:
            return

        unit_map = {
            'n': 'naga', 'b': 'baloon', 'w': 'warden', 
            'k': 'king', 'q': 'queen', 'a': 'amarah', 'f': 'freeze'
        }

        if k in unit_map and not recording:
            current_unit = unit_map[k]
            recording = True
            temp_moves = []
            print(f"\n\n>>> RECORDING: {current_unit.upper()}")

        elif k == 's' and recording:
            data[current_unit] = temp_moves
            recording = False
            print(f"\n>>> SAVED {current_unit.upper()} ({len(temp_moves)} gerakan)")

    except Exception as e:
        print(f"\n[!] Error: {e}")

def on_release(key):
    if key == keyboard.Key.esc:
        if data:
            output_path = os.path.join("..", "config", "recorded_moves.json")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"\n\nBERHASIL! Data disimpan di: {output_path}")
        return False

with mouse.Listener(on_click=on_click) as m_proc:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as k_proc:
        k_proc.join()