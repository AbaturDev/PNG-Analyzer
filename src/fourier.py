import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def display_fourier_spectrum(image_path):
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)

    fft_result = np.fft.fft2(img_array)
    fft_shifted = np.fft.fftshift(fft_result)

    magnitude_spectrum = np.abs(fft_shifted)
    log_magnitude = np.log1p(magnitude_spectrum)

    plt.figure(figsize=(8, 8))
    plt.imshow(log_magnitude, cmap='gray')
    plt.title('Fourier Spectrum (magnitude)')
    plt.axis('off')
    plt.show()

def test_fourier_transformation(image_path):
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)

    fft_result = np.fft.fft2(img_array)
    
    ifft_result = np.fft.ifft2(fft_result)
    
    recovered_image = np.real(ifft_result)

    difference = np.abs(img_array - recovered_image)

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

    mse = np.mean(difference**2)
    print(f"MSE: {mse:.10f}")

    if mse < 1e-5:
        print("Transformation works correctly")
    else:
        print("There is a problem with transformation")
