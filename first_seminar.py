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


#we test the code

R, G, B = 100, 150, 200
print("RGB:", (R, G, B))

y, u, v = ColorCoordsConverter.rgb_to_yuv(R, G, B)
print("YUV:", (y, u, v))

r2, g2, b2 = ColorCoordsConverter.yuv_to_rgb(y, u, v)
print("Back to RGB:", (r2, g2, b2))