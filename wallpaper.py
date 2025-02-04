# wallpaper.py
import os
import requests
import ctypes
import json

# Replace 'your_access_key_here' with your actual Unsplash Access Key
UNSPLASH_ACCESS_KEY = ''

def fetch_wallpaper(categories, cache_dir, usage_counts):
    query = ','.join(categories)

    url = 'https://api.unsplash.com/photos/random'
    headers = {
        'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}',
    }
    params = {
        'query': query,
        'orientation': 'landscape',
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            image_url = data['urls']['full']
            image_id = data['id']

            # Check usage counts
            if usage_counts.get(image_id, 0) >= 5:
                return fetch_wallpaper(categories, cache_dir, usage_counts)

            # Download the image
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_path = os.path.join(cache_dir, f"{image_id}.jpg")
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                return image_path, image_id
        else:
            print("Failed to fetch image from Unsplash:", response.status_code)
    except Exception as e:
        print("Error fetching image:", e)

    return None, None

def set_wallpaper(image_path):
    try:
        # Set wallpaper on Windows
        SPI_SETDESKWALLPAPER = 20
        abs_image_path = os.path.abspath(image_path)
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, abs_image_path, 3)
    except Exception as e:
        print("Error setting wallpaper:", e)
