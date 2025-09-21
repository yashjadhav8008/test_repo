from PIL import Image
import imagehash
import os
import io
import subprocess

base_path = r"D:/frame_extracter/extracted_frames/video_2_frames"
os.makedirs(base_path, exist_ok=True)

# threshold for similarity
THRESHOLD = 28

ffmpeg_cmd = [
    "ffmpeg",
    "-i", "video_2.mp4",
    "-f", "image2pipe",
    "-vcodec", "png",   # tell ffmpeg to output PNGs
    "pipe:1",
]

process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE,bufsize=10**8)
png_signature = b"\x49\x45\x4E\x44\xAE\x42\x60\x82"
prev_phash = None
frame_count = 0
buffer = b""
while True:
    chunk = process.stdout.read(4096)
    if not chunk:
        break
    buffer += chunk

    # check if we have a full PNG
    while True:
        end_idx = buffer.find(png_signature)
        if end_idx == -1:
            break  # not a full image yet

        end_idx += len(png_signature)  # include signature
        frame_data = buffer[:end_idx]
        buffer = buffer[end_idx:]  # keep rest for next frame

        # Decode image
        image = Image.open(io.BytesIO(frame_data)).convert("RGB")

        curr_hash = imagehash.phash(image)

        if prev_phash == None or (curr_hash - prev_phash) > THRESHOLD:
            image.save(f"{base_path}/2_frame_{frame_count}.png")

        frame_count += 1
        prev_phash = curr_hash
