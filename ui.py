import customtkinter as ctk
import compress_to_size
import os
import pathlib
import threading
import traceback
import urllib.request
import zipfile

WIDTH = 900
HEIGHT = 480
INPUT_WIDTH = 160
OPTIONS_WIDTH = 220
CONSOLE_WIDTH = WIDTH - INPUT_WIDTH - OPTIONS_WIDTH - 20

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.geometry(f"{WIDTH}x{HEIGHT}")
root.title("VidSquisher")

def add_ffmpeg_to_path():
    # Add ffmpeg to PATH
    if os.path.exists(os.path.join(os.curdir, "ffmpeg")):
        ffmpeg_folder = os.path.join(pathlib.Path().resolve(), "ffmpeg")
        ffmpeg_folder = os.path.join(ffmpeg_folder, "bin")
        os.environ["PATH"] += ffmpeg_folder + ";"

def download_ffmpeg():
    # Get ffmpeg
    label_status.configure(text="You are running the app for the first time.\nPlease wait for FFmpeg to download...", text_color="red")
    label_status.pack(pady=12, padx=10)
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    urllib.request.urlretrieve(url, "ffmpeg-release-essentials.zip")
    with zipfile.ZipFile("ffmpeg-release-essentials.zip", 'r') as zip_ref:
       zip_ref.extractall()
    os.remove("ffmpeg-release-essentials.zip")

    # Rename folder
    ffmpeg_folder = next((f for f in os.listdir() if f.startswith("ffmpeg") and os.path.isdir(f)), None)
    if ffmpeg_folder != "ffmpeg":
        os.rename(ffmpeg_folder, "ffmpeg")
        ffmpeg_folder = "ffmpeg"

    add_ffmpeg_to_path()
    label_status.configure(text="FFmpeg downloaded successfully!\nClick \"Compress\" again.", text_color="green")

def compress(size, audio, preset, overhead, divisor):
    in_file = entry_in.get()
    out_file = entry_out.get()
    start_time = start_time_entry.get() or None
    stop_time = stop_time_entry.get() or None
    if not os.path.exists(os.path.join(os.curdir, "ffmpeg")):
        threading.Thread(target=download_ffmpeg).start()
    else:
        threading.Thread(target=compress_thread, args=(in_file, out_file, size.get(), audio.get(), preset.get(), overhead.get(), start_time, stop_time, divisor.get())).start()

def compress_thread(in_file, out_file, size, audio, preset, overhead, start_time, stop_time, divisor):
    label_status.configure(text="Compressing...", text_color="black")
    try:
        compress_to_size.compress(in_file, size, audio, preset, overhead, start_time, stop_time, out_file, divisor)
    except Exception:
        label_status.configure(text="Compression failed!", text_color="red")
        printlog(f"PATH: {os.environ["PATH"]}\n\nWHERE ffprobe output:\n{os.popen('WHERE ffprobe').read()}\n\n{traceback.format_exc()}")
        return
    printlog(f"Compression complete!\nOutput file: {out_file}", text_color="green")
    label_status.configure(text=f"Compression complete!", text_color="green")

def browse():
    fname_in = ctk.filedialog.askopenfilename()
    fname_out = fname_in.split(".")[0] + " (compressed).mp4"

    entry_in.delete(0, ctk.END)
    entry_in.insert(0, fname_in)

    entry_out.delete(0, ctk.END)
    entry_out.insert(0, fname_out)

def printlog(text, text_color="red"):
    console.configure(state="normal")
    console.configure(text_color=text_color)
    console.delete(1.0, ctk.END)
    console.insert(1.0, text + "\n")
    console.configure(state="disabled")

def hide_console():
    console_frame.grid_remove()
    root.geometry(f"{WIDTH-CONSOLE_WIDTH-20}x{HEIGHT}")

def show_console():
    console_frame.grid()
    root.geometry(f"{WIDTH}x{HEIGHT}")

def toggle_console():
    if console_frame.winfo_ismapped():
        hide_console()
    else:
        show_console()

size = ctk.IntVar(value=10)
audio = ctk.IntVar(value=128)
preset = ctk.StringVar(value="fast")
overhead = ctk.BooleanVar(value=True)
divisor = ctk.IntVar(value=1)

#--------------------------------------------------------------------------------------------------#
input_frame = ctk.CTkFrame(master=root, height=HEIGHT, width=INPUT_WIDTH)
input_frame.grid(row=0, column=0)

label_in = ctk.CTkLabel(master=input_frame, text="Input Video File:")
label_in.pack(pady=12, padx=10)

entry_in = ctk.CTkEntry(master=input_frame, placeholder_text="example.mp4")
entry_in.pack(pady=12, padx=10)

button_browse = ctk.CTkButton(master=input_frame, text="Browse", command=browse)
button_browse.pack(pady=12, padx=10)

label_out = ctk.CTkLabel(master=input_frame, text="Output:")
label_out.pack(pady=12, padx=10)

entry_out = ctk.CTkEntry(master=input_frame, placeholder_text="example_out.mp4")
entry_out.pack(pady=12, padx=10)

button_compress = ctk.CTkButton(master=input_frame, text="Compress", command=lambda: compress(size, audio, preset, overhead, divisor))
button_compress.pack(pady=40, padx=10)

label_status = ctk.CTkLabel(master=input_frame, text="")
label_status.pack(pady=4, padx=10)

button_toggle_console = ctk.CTkButton(master=input_frame, text="Toggle Console", command=toggle_console)
button_toggle_console.pack(pady=12, padx=10)

#--------------------------------------------------------------------------------------------------#
options_frame = ctk.CTkFrame(master=root, height=HEIGHT, width=OPTIONS_WIDTH)
options_frame.grid(row=0, column=1)

overhead_checkbox = ctk.CTkCheckBox(master=options_frame, variable=overhead, text="Overhead")
overhead_checkbox.pack(pady=6, padx=10)

def update_size_label(value):
    size_label.configure(text=f"Size (MB): {int(float(value))}")

size_label = ctk.CTkLabel(master=options_frame, text=f"Size (MB): {size.get()}")
size_label.pack(pady=6, padx=10)
size_slider = ctk.CTkSlider(master=options_frame, variable=size, from_=2, to=100, number_of_steps=98//2, command=update_size_label)
size_slider.pack(pady=6, padx=10)

def update_audio_label(value):
    audio_label.configure(text=f"Audio Bitrate (Kbps): {int(float(value))}")

audio_label = ctk.CTkLabel(master=options_frame, text=f"Audio Bitrate (Kbps): {audio.get()}")
audio_label.pack(pady=6, padx=10)
audio_slider = ctk.CTkSlider(master=options_frame, variable=audio, from_=32, to=320, number_of_steps=(320 - 16) // 32, command=update_audio_label)
audio_slider.pack(pady=6, padx=10)

preset_label = ctk.CTkLabel(master=options_frame, text="Preset")
preset_label.pack(pady=6, padx=10)
preset_menu = ctk.CTkOptionMenu(master=options_frame, variable=preset, values=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"])
preset_menu.pack(pady=6, padx=10)

start_time_label = ctk.CTkLabel(master=options_frame, text="Start Time")
start_time_label.pack(pady=6, padx=10)
start_time_entry = ctk.CTkEntry(master=options_frame, placeholder_text="HH:MM:SS.msecs")
start_time_entry.pack(pady=6, padx=10)

stop_time_label = ctk.CTkLabel(master=options_frame, text="Stop Time")
stop_time_label.pack(pady=6, padx=10)
stop_time_entry = ctk.CTkEntry(master=options_frame, placeholder_text="HH:MM:SS.msecs")
stop_time_entry.pack(pady=6, padx=10)

def update_divisor_label(value):
    divisor_label.configure(text=f"Resolution Divisor: {int(float(value))}")

divisor_label = ctk.CTkLabel(master=options_frame, text=f"Resolution Divisor: {divisor.get()}")
divisor_label.pack(pady=6, padx=10)
divisor_slider = ctk.CTkSlider(master=options_frame, variable=divisor, from_=1, to=8, number_of_steps=7, command=update_divisor_label)
divisor_slider.pack(pady=6, padx=10)

#--------------------------------------------------------------------------------------------------#
console_frame = ctk.CTkFrame(master=root, height=HEIGHT, width=CONSOLE_WIDTH)
console_frame.grid(row=0, column=2)
console = ctk.CTkTextbox(master=console_frame, text_color="red", state="disabled", height=HEIGHT-20, width=CONSOLE_WIDTH)
console.pack(pady=12, padx=10)
#--------------------------------------------------------------------------------------------------#

add_ffmpeg_to_path()

root.mainloop()