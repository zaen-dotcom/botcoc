import json
import os
import sys
from pynput import mouse, keyboard

# Global State
recording = False
current_unit = None
data = {}
temp_moves = []

print("="*40)
print("   CoC MACRO RECORDER (PURE TAP)   ")
print("="*40)
print("Daftar Tombol Unit:")
print("  N=Naga, B=Balon, W=Warden, K=King, Q=Queen, A=Amarah, F=Freeze")
print("  S=Super Witch (Switch)")
print("-" * 40)
print("Kontrol Alur:")
print("  Klik di Emulator = Catat Koordinat")
print("  Space/Enter = SAVE UNIT")
print("  ESC = SIMPAN FILE & KELUAR")
print("="*40)

def on_click(x, y, button, pressed):
    global recording, temp_moves, current_unit
    if pressed and recording:
        coord = [int(x), int(y)]
        temp_moves.append(coord)
        sys.stdout.write(f"\r[REC] {current_unit.upper()}: Klik ke-{len(temp_moves)} di {coord}   ")
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
            'k': 'king', 'q': 'queen', 'a': 'amarah', 
            'f': 'freeze', 's': 'switch'
        }

        if k in unit_map and not recording:
            current_unit = unit_map[k]
            recording = True
            temp_moves = []
            print(f"\n\n>>> RECORDING: {current_unit.upper()} (Klik sebanyak mungkin!)")

        # Pakai tombol Space atau Enter untuk simpan unit agar tidak bentrok karakter
    except Exception: pass

def on_release(key):
    global recording, current_unit, temp_moves, data
    
    # Simpan unit dengan Space
    if key == keyboard.Key.space and recording:
        data[current_unit] = temp_moves
        recording = False
        print(f"\n>>> SAVED: {current_unit.upper()} ({len(temp_moves)} titik)")
        print("Pilih unit lain atau tekan ESC.")

    elif key == keyboard.Key.esc:
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