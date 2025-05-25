import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def display_fourier_spectrum(image_path):
    # Open image and convert to grayscale
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)

    # Apply 2D Fourier Transform
    fft_result = np.fft.fft2(img_array)
    # Shift zero frequency component to the center    
    fft_shifted = np.fft.fftshift(fft_result)

    # Compute magnitude spectrum and apply logarithmic scaling for visibility
    magnitude_spectrum = np.abs(fft_shifted)
    log_magnitude = np.log1p(magnitude_spectrum)

    # Display the spectrum
    plt.figure(figsize=(8, 8))
    plt.imshow(log_magnitude, cmap='gray')
    plt.title('Fourier Spectrum (magnitude)')
    plt.axis('off')
    plt.show()

def test_fourier_transformation(image_path):
    # Open image and convert to grayscale
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)

    # Forward 2D Fourier Transform
    fft_result = np.fft.fft2(img_array)

    # Inverse 2D Fourier Transform
    ifft_result = np.fft.ifft2(fft_result)
    
    # Extract real part of the result (imaginary part should be negligible)
    recovered_image = np.real(ifft_result)

    # Compute pixel-wise absolute difference between original and recovered image
    difference = np.abs(img_array - recovered_image)

    # Display original, recovered, and difference images
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    axs[0].imshow(img_array, cmap='gray')
    axs[0].set_title('Original Image')
    axs[0].axis('off')

    axs[1].imshow(recovered_image, cmap='gray')
    axs[1].set_title('Recovered image (after iFFT)')
    axs[1].axis('off')

    axs[2].imshow(difference, cmap='hot')
    axs[2].set_title('Difference Image')
    axs[2].axis('off')

    plt.show()
