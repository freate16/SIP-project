import numpy as np
import rasterio
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def apply_filters(input_path, k_nearest_output_path, avg_output_path, kernel_size, k_value):
    with rasterio.open(input_path) as src:
        image = src.read()  
        original_crs = src.crs  
        transform = src.transform  
        profile = src.profile

    bands, height, width = image.shape

    if kernel_size % 2 == 0:
        kernel_size += 1
    pad_size = kernel_size // 2
    k_nearest_image = np.zeros_like(image)
    avg_image = np.zeros_like(image)


    for band in range(bands):
        padded_band = np.pad(image[band], ((pad_size, pad_size), (pad_size, pad_size)), mode="edge")

        for i in range(height):
            for j in range(width):
                roi = padded_band[i:i + kernel_size, j:j + kernel_size]
                roi_center_pixel = padded_band[i + pad_size, j + pad_size]
                roi_list = roi.flatten()
                diffs = [(abs(x - roi_center_pixel), x) for x in roi_list]
                diffs.sort(key=lambda x: x[0])
                neighbours = [x[1] for x in diffs[:k_value + 1]]  
                k_nearest_image[band, i, j] = np.mean(neighbours)
                avg_image[band, i, j] = np.mean(roi)

    with rasterio.open(
        k_nearest_output_path, 
        'w', 
        height=height,
        width = width,
        count = bands,
        dtype=image.dtype,
        crs=original_crs,
        transform=transform) as dst:
         dst.write(k_nearest_image)

   
    with rasterio.open(
        avg_output_path, 
        'w',height=height,
        width = width,
        count = bands,
        dtype=image.dtype,
        crs=original_crs,
        transform=transform) as dst:
         dst.write(avg_image)

    messagebox.showinfo("Success", "Filtered images saved successfully!")


def open_file():
    return filedialog.askopenfilename(filetypes=[("TIFF files", "*.tif"), ("All files", "*.*")])


def save_file():
    return filedialog.asksaveasfilename(defaultextension=".tif", filetypes=[("TIFF files", "*.tif")])


def main():

    root = tk.Tk()
    root.title("Image Filtering")

    tk.Label(root, text="Input TIFF File:").grid(row=0, column=0, padx=10, pady=10)
    input_path_var = tk.StringVar()
    tk.Entry(root, textvariable=input_path_var, width=40).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=lambda: input_path_var.set(open_file())).grid(row=0, column=2, padx=10, pady=10)

 
    tk.Label(root, text="K-nearest Output File:").grid(row=1, column=0, padx=10, pady=10)
    k_nearest_output_var = tk.StringVar()
    tk.Entry(root, textvariable=k_nearest_output_var, width=40).grid(row=1, column=1, padx=10, pady=10)
    tk.Button(root, text="Save As", command=lambda: k_nearest_output_var.set(save_file())).grid(row=1, column=2, padx=10, pady=10)

    tk.Label(root, text="Average Output File:").grid(row=2, column=0, padx=10, pady=10)
    avg_output_var = tk.StringVar()
    tk.Entry(root, textvariable=avg_output_var, width=40).grid(row=2, column=1, padx=10, pady=10)
    tk.Button(root, text="Save As", command=lambda: avg_output_var.set(save_file())).grid(row=2, column=2, padx=10, pady=10)

    tk.Label(root, text="Kernel Size:").grid(row=3, column=0, padx=10, pady=10)
    kernel_size_var = tk.IntVar(value=3)
    tk.Entry(root, textvariable=kernel_size_var, width=10).grid(row=3, column=1, padx=10, pady=10, sticky="w")

    tk.Label(root, text="K Value:").grid(row=4, column=0, padx=10, pady=10)
    k_value_var = tk.IntVar(value=3)
    tk.Entry(root, textvariable=k_value_var, width=10).grid(row=4, column=1, padx=10, pady=10, sticky="w")


    def run_filter():
        input_path = input_path_var.get()
        k_nearest_output_path = k_nearest_output_var.get()
        avg_output_path = avg_output_var.get()
        kernel_size = kernel_size_var.get()
        k_value = k_value_var.get()

        if not input_path or not k_nearest_output_path or not avg_output_path:
            messagebox.showerror("Error", "Please specify all file paths.")
            return

        try:
            apply_filters(input_path, k_nearest_output_path, avg_output_path, kernel_size, k_value)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    tk.Button(root, text="Run", command=run_filter).grid(row=5, column=1, pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()

