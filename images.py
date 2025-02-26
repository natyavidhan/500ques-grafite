import re
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from PIL import Image
import numpy as np

class WatermarkRemover:
    def __init__(self, images_dir="images/pyq/jee_main"):
        self.images_dir = images_dir
        self.output_dir = images_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.rmse_threshold = 75  # Threshold for considering pixels as "near white"

    def process_single_image(self, input_path: str, output_path: str) -> bool:
        """
        Process a single image by:
        1. Converting near-white pixels to pure white using RMS threshold
        2. Converting remaining non-white pixels to black
        3. Optimizing for web
        """
        try:
            # Open image and handle RGBA conversion
            with Image.open(input_path) as img:
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                # Create white background and composite
                background = Image.new("RGBA", img.size, (255, 255, 255, 255))
                combined = Image.alpha_composite(background, img)

                # Convert to numpy array
                img_array = np.array(combined.convert("RGB"))

                # Step 1: Convert near-white pixels to pure white using RMS
                target_color = np.array([255, 255, 255])
                
                # Optimize: Calculate diff_squared directly without intermediate array
                diff_squared = np.sum((img_array - target_color) ** 2, axis=-1) / 3
                mask = np.sqrt(diff_squared) < self.rmse_threshold
                
                # Convert near-white pixels to pure white
                img_array[mask] = target_color

                # Step 2: Convert all non-white pixels to black
                non_white_mask = np.any(img_array != 255, axis=-1)
                img_array[non_white_mask] = [0, 0, 0]

                # Convert back to PIL Image
                processed_img = Image.fromarray(img_array)

                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save with optimization
                processed_img.save(output_path, optimize=True, quality=95)
                return True

        except Exception as e:
            print(f"Error processing {input_path}: {str(e)}")
            return False

def download_images_from_html(html_content):
    """Downloads images from HTML content."""

    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')
    watermark_remover = WatermarkRemover()

    for i, img_tag in enumerate(img_tags):
        src = img_tag.get('src')

        if src:
            try:
                if not src.startswith("http"):
                    base_url = img_tag.find_parent().get('href')
                    if base_url:
                        src = urljoin(base_url, src)
                    else:
                        print(f"Skipping relative URL without base URL: {src}")
                        continue

                response = requests.get(src, stream=True)
                response.raise_for_status()

                filename = os.path.basename(src)
                filename = re.sub(r'[^\w\s.-]', '', filename)
                if "." not in filename:  # Add an extension if not present
                    content_type = response.headers.get('content-type')
                    if content_type and 'image/' in content_type:
                        extension = content_type.split('/')[-1].split(';')[0]
                        filename += f".{extension}"  # Add content type as extension
                    else:
                        filename += ".jpg"  # Default to .jpg if content type is not an image.

                filepath = os.path.join("images/pyq/jee_main", filename)

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Downloaded image {i+1}/{len(img_tags)}: {filename}")

                # Remove watermark from the downloaded image
                cleaned_filepath = os.path.join(watermark_remover.output_dir, filename)
                watermark_remover.process_single_image(filepath, cleaned_filepath)

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {src}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing image {src}: {e}")
        else:
            print("Image tag has no 'src' attribute.")

files = ["data/physics_cleaned.json", "data/chemistry_cleaned.json", "data/maths_cleaned.json"]

for file in files:
    data = json.load(open(file))
    for i, item in enumerate(data):
        download_images_from_html(item['text'])
        for j, option in enumerate(item['options']):
            download_images_from_html(option['text'])