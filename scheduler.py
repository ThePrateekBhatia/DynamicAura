# scheduler.py
import time
import threading
import wallpaper
import os

def change_wallpapers(stop_event, interval, categories, cache_dir, usage_counts, save_usage_counts_func):
    while not stop_event.is_set():
        image_path, image_id = wallpaper.fetch_wallpaper(categories, cache_dir, usage_counts)
        if image_path:
            wallpaper.set_wallpaper(image_path)

            # Update usage counts
            usage_counts[image_id] = usage_counts.get(image_id, 0) + 1
            save_usage_counts_func()

            # Remove image if used 5 times
            if usage_counts[image_id] >= 5:
                os.remove(image_path)
                del usage_counts[image_id]
                save_usage_counts_func()
        else:
            print("Failed to change wallpaper.")

        for _ in range(interval):
            if stop_event.is_set():
                break
            time.sleep(1)
