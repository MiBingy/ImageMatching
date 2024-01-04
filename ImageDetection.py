import cv2
import os
import concurrent.futures
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import imghdr
import numpy as np


def resize_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            pil_image = Image.open(image_path)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return cv2.resize(image, (100, 100))
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None


def find_matching_image(screenshot_path, main_folder):
    try:
        screenshot = cv2.imread(screenshot_path)

        if screenshot is None:
            print("Error: Unable to read the screenshot image.")
            return

        screenshot = cv2.resize(screenshot, (100, 100))  # Resize the screenshot image to a common size

        best_match_path = None
        best_match_score = 0.0

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(resize_image, os.path.join(root, file)): os.path.join(root, file) for
                       root, dirs, files in os.walk(main_folder) for file in files if
                       imghdr.what(os.path.join(root, file))}

            for future in concurrent.futures.as_completed(futures):
                image_path = futures[future]
                try:
                    image = future.result()
                    if image is not None:
                        _, diff = ssim(image, screenshot, win_size=3, full=True)
                        similarity_score = diff.mean()

                        # debug to print scores
                        # print(f"Image: {image_path}, Similarity Score: {similarity_score}")

                        # You can experiment with different similarity thresholds
                        if similarity_score > 0.8 and similarity_score > best_match_score:
                            best_match_score = similarity_score
                            best_match_path = image_path

                except Exception as e:
                    print(f"Error processing image {image_path}: {e}")

        if best_match_path:
            print("Best Match found!")
            print("Image Path:", best_match_path)
        else:
            print("No matching image found.")
    except Exception as e:
        print(f"Error processing screenshot image: {e}")


if __name__ == "__main__":
    while True:
        # Define the main folder to search through
        main_folder = r"C:\your\path\here"
        # main_folder = = input("Enter the path of the main directory (type 'kill' to end): ")

        # Get the screenshot path from the user
        screenshot_path = input("Enter the path of the screenshot image (type 'kill' to end): ")

        if screenshot_path.lower() == 'kill':
            print("Program terminated.")
            break

        try:
            # Call the function to find the matching image
            find_matching_image(screenshot_path, main_folder)
        except Exception as e:
            print(f"Error: {e}")
