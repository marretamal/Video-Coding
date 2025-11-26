import unittest
import numpy as np
from PIL import Image
import os
from unittest.mock import patch

from first_seminar import (
    ColorCoordsConverter,
    FFmpeg,
    serpentine,
    compress_to_grayscale,
    run_length_encoding_zeros,
    DCTTools,
    DWTTools
)


class TestColorCoordsConverter(unittest.TestCase):

    def test_rgb_to_yuv_and_back(self):
        r, g, b = 100, 150, 200
        y, u, v = ColorCoordsConverter.rgb_to_yuv(r, g, b)
        r2, g2, b2 = ColorCoordsConverter.yuv_to_rgb(y, u, v)

        self.assertAlmostEqual(r, r2, delta=1)
        self.assertAlmostEqual(g, g2, delta=1)
        self.assertAlmostEqual(b, b2, delta=1)


class TestFFmpeg(unittest.TestCase):

    @patch("ffmpeg.run")
    def test_resize_image_runs(self, mock_run):
        FFmpeg.resize_image("selfie2.jpeg", 100, 100, "out.jpg")
        mock_run.assert_called_once()

    @patch("ffmpeg.run")
    def test_compress_to_grayscale_runs(self, mock_run):
        compress_to_grayscale("selfie2.jpeg", "out.jpg")
        mock_run.assert_called_once()

class TestSerpentine(unittest.TestCase):

    def test_serpentine_hardcoded_image(self):
        # Create a 3x3 test image manually
        img = Image.new("RGB", (3, 3))

        # Fill the image with values 1-9 for clarity
        pixels = [
            [(1,1,1), (2,2,2), (3,3,3)],
            [(4,4,4), (5,5,5), (6,6,6)],
            [(7,7,7), (8,8,8), (9,9,9)]
        ]

        for y in range(3):
            for x in range(3):
                img.putpixel((x, y), pixels[y][x])

        # Save as PNG (lossless)
        temp_file = "test3_img.png"
        img.save(temp_file)

        try:
            # Run serpentine function
            result = serpentine(temp_file)

            # Expected left-to-right serpentine order
            expected = [
                (1,1,1), (2,2,2), (4,4,4), 
                (7,7,7), (5,5,5), (3,3,3), 
                (6,6,6), (8,8,8), (9,9,9)
            ]

            self.assertEqual(result, expected)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

class TestRunLengthEncoding(unittest.TestCase):

    def test_rle_zero_runs(self):
        data = [5, 0, 0, 0, 7, 0, 8]
        encoded = run_length_encoding_zeros(data)
        expected = [5, 0, 3, 7, 0, 1, 8]
        self.assertEqual(encoded, expected)


class TestDCT(unittest.TestCase):

    def test_dct_idct_reconstruction(self):
        block = np.full((8, 8), 150, dtype=float)

        d = DCTTools.dct_2d(block)
        r = DCTTools.idct_2d(d)

        # check reconstruction is nearly identical
        self.assertTrue(np.allclose(block, r, atol=1e-6))


class TestDWT(unittest.TestCase):

    def test_dwt_idwt_identity(self):
        block = np.random.randint(0, 255, (8, 8)).astype(float)

        coeffs = DWTTools.dwt_2d(block)
        restored = DWTTools.idwt_2d(coeffs)

        self.assertTrue(np.allclose(block, restored, atol=1e-6))


if __name__ == "__main__":
    unittest.main()

