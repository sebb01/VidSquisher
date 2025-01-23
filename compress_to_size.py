# Adapted by BinaryCounter from Sebb's batch script
# Adapted again by Sebb

import argparse
import sys
import os
import ffmpeg
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Compress a video file using FFmpeg.")
    parser.add_argument("in_file", help="File name (including extension)")
    parser.add_argument("-s","--size", default=10, type=float, help="Target file size in MB. Default: 10 (for discord)")
    parser.add_argument("-a","--audio", default=None, type=int, help="Audio Bitrate in Kbits. Default: 128 (possibly lower to satisfy size limit)")
    parser.add_argument("-p", "--preset", default='fast', type=str, help="Encoding preset. Default: 'fast'")
    parser.add_argument("--safe", action='store_false', help="Add some overhead to avoid overshooting size limit. Default: True")
    parser.add_argument("--ss", help="Set a start time for trimming, in format HH:MM:SS.msecs")
    parser.add_argument("--to", help="Set a stop time for trimming, in format HH:MM:SS.msecs")
    parser.add_argument("--out_file", type=str, help="Output file path. Default: 'Original_path (size)mb.mp4'")
    parser.add_argument("--divisor", type=int, default=1, help="Divisor for resolution. Default: 1")

    args = parser.parse_args()

    in_file = Path(args.in_file)
    size = args.size
    audio = args.audio
    preset = args.preset
    safe = args.safe
    start_time = args.ss
    stop_time = args.to
    out_file = args.out_file

    compress(in_file, size, audio, preset, safe, start_time, stop_time, out_file, args.divisor)
    
def compress(inFile, size=10, audio=None, preset='fast', safe=True, start_time=None, stop_time=None, out_file=None, divisor=1):
    length = float(ffmpeg.probe(inFile, cmd='ffprobe')["format"]["duration"]) # Get length from video metadata
    # Compute length after trimming
    if stop_time is not None:
        length = string_to_seconds(stop_time)
    if start_time is not None:
        length = length - string_to_seconds(start_time)
    
    # Handle default audio bitrate
    audioSpecified = audio is not None
    if not audioSpecified:
        audio = 128
    
    if safe:
        length += 2

    kb_with_audio = 8192 * size         # Convert to kilobytes
    kb = kb_with_audio - audio*length   # Subtract audio bitrate
    if kb < 0 and audioSpecified:
        print("Compression not possible, audio alone takes up size limit. Consider passing a lower or no audio bitrate.")
        sys.exit(1)
    while kb < 0 and audio > 16:        # Find lower audio bitrate that satisfies size constraints; set to 16 if it does not exist
        audio = max(audio - 8, 16)
        kb = kb_with_audio - audio*length
    kbs = kb // length
    
    if out_file is None:
        inFileNameNoExt = Path(inFile).with_suffix('') # Remove extension from input file name
        out_file = Path(f'{inFileNameNoExt} {size}mb.mp4') # Append size to name
    
    # If outFile exists, append a unique number to prevent overwriting
    i = 1
    outFileOriginal = Path(out_file).with_suffix('')
    while (os.path.exists(out_file)):
        out_file = Path(f'{outFileOriginal} ({i}).mp4')
        i+=1

    # Pass 1
    output_args = {
        'c:v': 'libx264',
        'preset': preset,
        'b:v': f'{kbs}k',
        'pass': 1,
        'vf':"format=yuv420p",
        'b:a': str(audio)+'k',
        'f': 'mp4',
        # Disable audio in the first pass
        'an': None,
        'vf': f'scale=iw/{divisor}:ih/{divisor}',
    }
    if start_time is not None:
        output_args['ss'] = start_time
    if stop_time is not None:
        output_args['to'] = stop_time
    print(output_args)

    out, err = ffmpeg.input(inFile).output('NUL', **output_args).global_args('-y').run()   # Save first pass to NUL and skip overwrite prompt

    # Pass 2
    output_args['pass'] = 2
    if audio > 0:
        del output_args["an"]
    print(output_args)
    ffmpeg.input(inFile).output(str(out_file), **output_args).run()

    print(f"Saved new file as: {out_file}")

    # Clean up temporary files
    os.remove('ffmpeg2pass-0.log')
    os.remove('ffmpeg2pass-0.log.mbtree')

    return (out, err)

# Convert "HH:MM:SS" to seconds
def string_to_seconds(string):
    hours = int(string[0:2])
    minutes = int(string[3:5])
    seconds = float(string[6:])
    return hours*60*60 + minutes*60 + seconds

if __name__ == "__main__":
    main()