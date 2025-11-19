import ffmpeg
from os import remove
from PIL import Image
import numpy as np


class ColorCoordsConverter:

    def rgb_to_yuv(r, g, b): #this first method converts RGB to YUV
        y = 0.257 * r + 0.504 * g + 0.098 * b + 16
        u = -0.148 * r - 0.291 * g + 0.439 * b + 128
        v = 0.439 * r - 0.368 * g - 0.071 * b + 128
        return y, u, v

    def yuv_to_rgb(y, u, v): #this second method converts YUV to RGB
        r = 1.164 * (y - 16) + 1.596 * (v - 128)
        g = 1.164 * (y - 16) - 0.813 * (v - 128) - 0.391 * (u - 128)
        b = 1.164 * (y - 16) + 2.018 * (u - 128)

        r = max(0, min(255, round(r))) #we ensure that the values are in the range [0, 255] after rounding them to the nearest integer
        g = max(0, min(255, round(g)))
        b = max(0, min(255, round(b)))

        return r, g, b

class FFmpeg:

    def resize_image(path, new_width, new_height, output_path):
        try:
            remove(output_path)
        except FileNotFoundError:
            pass

        (
            ffmpeg
            .input(path)
            .filter("scale", new_width, new_height)
            .output(output_path)
            .run()
        )
        print(f"Image resized and saved to: {output_path}")

def serpentine(file):
    img = Image.open(file).convert("RGB")
    width, height = img.size
    pixels = img.load()
    serp = []

    for diagonal in range(width + height - 1):

        #if we are in even diagonals we go up to the right
        if diagonal % 2 == 0:
            y = min(diagonal, height - 1)
            x = diagonal - y
            while y >= 0 and x < width:
                serp.append(pixels[x, y])
                x += 1
                y -= 1

        # if we are in odd diagonals we go down to the left
        else:
            x = min(diagonal, width - 1)
            y = diagonal - x
            while x >= 0 and y < height:
                serp.append(pixels[x, y])
                x -= 1
                y += 1

    return serp #return the list of pixels coordinates in serpentine order


def compress_to_grayscale(input_path, output_path):
        try:
            remove(output_path)
        except FileNotFoundError:
            pass
        (
            ffmpeg
            .input(input_path)
            .filter("format", "gray")     # convert to black & white
            .output(output_path, vcodec='mjpeg', qscale=31)  # maximum compression with a quality scale of 31
            .run()
        )
        print("Grayscale compressed image saved to:", output_path)

# following the example from class, we apply RLE to compress zero runs only

def run_length_encoding_zeros(byte_list):
    encoded = []
    i = 0
    while i < len(byte_list):
        if byte_list[i] == 0: # we found a zero, we count the run length
            count = 1
            i += 1
            while i < len(byte_list) and byte_list[i] == 0:
                count += 1
                i += 1

            encoded.extend([0, count]) # we store the zero and its count
        else:
            encoded.append(byte_list[i]) # non-zero byte, we store it normally (not compressed)
            i += 1

    return encoded


# TESTING EXERCISE 2
R, G, B = 100, 150, 200
print("RGB:", (R, G, B))

y, u, v = ColorCoordsConverter.rgb_to_yuv(R, G, B)
print("YUV:", (y, u, v))

r2, g2, b2 = ColorCoordsConverter.yuv_to_rgb(y, u, v)
print("Back to RGB:", (r2, g2, b2))



# TESTING EXERCISE 3
# FFmpeg.resize_image(
#     path="/Users/marretamal/Desktop/video_coding/S1-JPEG-JPEG2000-and-FFMpeg/selfie2.jpeg",
#     new_width=320,
#     new_height=240,
#     output_path="/Users/marretamal/Desktop/video_coding/S1-JPEG-JPEG2000-and-FFMpeg/output_coding.png"
# )

# # TESTING EXERCISE 4
# pixels_serpentine = serpentine("selfie2.jpeg")
# for i in range(20):
#     print(pixels_serpentine[i])

# # TESTING EXERCISE 5
# compress_to_grayscale("selfie2.jpeg", "selfie3_gray_compressed.png")
# print("Done. Output:", "selfie3_gray_compressed.png")

# # TESTING EXERCISE 5 b)
# data = [17, 8, 54, 0, 0, 0, 97, 5, 16, 0, 45, 23, 0, 0, 0, 67, 0, 8]
# encoded = run_length_encoding_zeros(data)
# print("Original: ", data)
# print("Encoded : ", encoded)