import unittest
import numpy as np
from PIL import Image
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
        # create 3x3 test image manually
        img = Image.new("RGB", (3, 3))

        # row 0
        img.putpixel((0, 0), (1, 1, 1))
        img.putpixel((1, 0), (2, 2, 2))
        img.putpixel((2, 0), (3, 3, 3))

        # row 1
        img.putpixel((0, 1), (4, 4, 4))
        img.putpixel((1, 1), (5, 5, 5))
        img.putpixel((2, 1), (6, 6, 6))

        # row 2
        img.putpixel((0, 2), (7, 7, 7))
        img.putpixel((1, 2), (8, 8, 8))
        img.putpixel((2, 2), (9, 9, 9))

        img.save("test3_img.jpg")

        result = serpentine("test3_img.jpg")

        # expected serpentine (zigzag) order: 1,2,4,7,5,3,6,8,9
        expected = [(1,1,1), (2,2,2), (4,4,4), (7,7,7), (5,5,5),
                    (3,3,3), (6,6,6), (8,8,8), (9,9,9)]

        self.assertEqual(result, expected)


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

