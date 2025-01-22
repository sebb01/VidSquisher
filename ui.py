import customtkinter as ctk
import compress_to_size
import os
import pathlib
import threading
import traceback
import urllib.request
import zipfile

WIDTH = 900
HEIGHT = 500

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.geometry(f"{WIDTH}x{HEIGHT}")

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

def compress():
    if not os.path.exists(os.path.join(os.curdir, "ffmpeg")):
        threading.Thread(target=download_ffmpeg).start()
    else:
        threading.Thread(target=compress_thread).start()

def compress_thread():
    label_status.configure(text="Compressing...", text_color="black")
    fname_in = entry_in.get()
    fname_out = entry_out.get()
    try:
        compress_to_size.compress(fname_in, outFile=fname_out)
    except Exception:
        label_status.configure(text="Compression failed!", text_color="red")
        printlog(f"PATH: {os.environ["PATH"]}\n\nWHERE ffprobe output:\n{os.popen('WHERE ffprobe').read()}\n\n{traceback.format_exc()}")
        return
    printlog(f"Compression complete!\nOutput file: {fname_out}", text_color="green")
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

frame = ctk.CTkFrame(master=root)
frame.grid(row=0, column=0)

label_in = ctk.CTkLabel(master=frame, text="Input Video File:")
label_in.pack(pady=12, padx=10)

entry_in = ctk.CTkEntry(master=frame, placeholder_text="example.mp4")
entry_in.pack(pady=12, padx=10)

button_browse = ctk.CTkButton(master=frame, text="Browse", command=browse)
button_browse.pack(pady=12, padx=10)

label_out = ctk.CTkLabel(master=frame, text="Output\n(defaults to \"example compressed.mp4\"):")
label_out.pack(pady=12, padx=10)

entry_out = ctk.CTkEntry(master=frame, placeholder_text="example_out.mp4")
entry_out.pack(pady=12, padx=10)

button_compress = ctk.CTkButton(master=frame, text="Compress", command=compress)
button_compress.pack(pady=48, padx=10)

label_status = ctk.CTkLabel(master=frame, text="")
label_status.pack(pady=12, padx=10)

console_frame = ctk.CTkFrame(master=root)
console_frame.grid(row=0, column=1)
console = ctk.CTkTextbox(master=console_frame, text_color="red", state="disabled", height=HEIGHT-100, width=WIDTH//2 + 150)
console.pack(pady=12, padx=10)

add_ffmpeg_to_path()

root.mainloop()