# S1-JPEG-JPEG2000-and-FFMpeg

**Task 1**
Before working on multimedia processing, we needed to install the latest version of FFmpeg as requested in the seminar instructions. We installed FFmpeg with all the required libraries and verified the installation by running: ffmpeg -version:
<img width="1123" height="130" alt="image" src="https://github.com/user-attachments/assets/e392e474-179e-4ee6-981f-53a06ef6e810" />

**Task 2**
We created a class called ColorCoordsConverter, containing: rgb_to_yuv(r, g, b) and yuv_to_rgb(y, u, v) methods. This implements the color transform described in the JPEG standard, as we have in the slides.

**Task 3**
We implemented a class FFmpeg with a method: resize_image(path, new_width, new_height, output_path). This method automatically calls FFmpeg from Python to reduce the size (and the quality) of any image. We tested this method and saved the result as selife2_320x240.png (320x240 are the new dimensions chosen). We can see how the output image is smaller and has less quality. 

**Task 4**
We implemented a function: serpentine (file), which reads image pixels in the diagonal zig-zag serpentine pattern seen in the JPEG DCT coefficient scan shown in the slides.

**Task 5**
We added: compress_to_grayscale(input_path, output_path). This uses FFmpeg to convert the input image to grayscale, and apply maximum JPEG compression using vcodec='mjpeg', qscale=31. We chose the quality scale to be 31 since doing some research we found that it is  the highest compression and lowest quality allowed. We tested the method and saved the output as selfie2.png.

**Task 5.b**
We added a function: run_length_encoding_zeros(byte_list). This compresses runs of zeros, as shown in the example from the slides. 

**Task 6**
We implemented a class DCTTools containing: dct_2d(block), idct_2d(block), image_to_blocks(img_path), blocks_to_image(...). This applies the 2D Discrete Cosine Transform to 8×8 blocks and reconstructs them using IDCT. The reconstructed image is saved as reconstructed_ex6.png. 

**Task 7**
We added a class DWTTools with: dwt_2d(block), idwt_2d(coeffs). This implements the 2D Haar wavelet transform, basis of JPEG2000. The reconstructed image is saved as reconstructed_dwt_ex7.png. 

**Task 8**
Finally, we created a full test suite in: test_seminar1.py. Using AI, we have created unit tests for all the methods. After some adjustments and running the file we passed all the tests: 
<img width="890" height="132" alt="image" src="https://github.com/user-attachments/assets/a6c86602-68f0-4a0f-ae6e-ebe4e1bc189d" />

