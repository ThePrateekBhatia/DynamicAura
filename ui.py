# ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
import scheduler
import wallpaper

class WallpaperApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Dynamic Wallpaper Changer")
        self.geometry("600x500")
        self.configure(bg='#F0F0F0')  # Soft background color

        # Categories and settings
        self.categories = ['Nature', 'Technology', 'Abstract', 'Space', 'Animals']
        self.selected_categories = {cat: tk.BooleanVar() for cat in self.categories}
        self.change_interval = tk.IntVar(value=60)  # Default interval in seconds

        # Initialize cache and usage counts
        self.cache_dir = 'cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        self.usage_counts = {}
        self.load_usage_counts()

        # Create UI elements
        self.create_widgets()

        # Load settings if they exist
        self.load_settings()

        # Thread control
        self.stop_event = threading.Event()
        self.wallpaper_thread = None

        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Title Label
        title_label = ttk.Label(self, text="Dynamic Wallpaper Changer", font=("Helvetica", 18))
        title_label.pack(pady=20)

        # Categories Frame
        categories_frame = ttk.LabelFrame(self, text="Select Wallpaper Categories:")
        categories_frame.pack(pady=10, padx=20, fill='x')

        for cat in self.categories:
            cb = ttk.Checkbutton(categories_frame, text=cat, variable=self.selected_categories[cat])
            cb.pack(anchor='w')

        # Time Interval Frame
        interval_frame = ttk.LabelFrame(self, text="Set Wallpaper Change Interval (seconds):")
        interval_frame.pack(pady=10, padx=20, fill='x')

        interval_entry = ttk.Entry(interval_frame, textvariable=self.change_interval)
        interval_entry.pack(pady=5, padx=5)

        # Start and Stop Buttons
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(pady=20)

        start_button = ttk.Button(buttons_frame, text="Start", command=self.start_changing_wallpapers)
        start_button.pack(side='left', padx=10)

        stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop_changing_wallpapers)
        stop_button.pack(side='left', padx=10)

    def start_changing_wallpapers(self):
        self.save_settings()
        selected = [cat for cat, var in self.selected_categories.items() if var.get()]
        if not selected:
            messagebox.showwarning("No Category Selected", "Please select at least one category.")
            return

        if self.wallpaper_thread and self.wallpaper_thread.is_alive():
            messagebox.showinfo("Already Running", "The wallpaper changer is already running.")
            return

        self.stop_event.clear()
        interval = self.change_interval.get()
        categories = selected
        self.wallpaper_thread = threading.Thread(
            target=scheduler.change_wallpapers,
            args=(self.stop_event, interval, categories, self.cache_dir, self.usage_counts, self.save_usage_counts)
        )
        self.wallpaper_thread.start()
        messagebox.showinfo("Started", "Wallpaper changer has started.")

    def stop_changing_wallpapers(self):
        if self.wallpaper_thread and self.wallpaper_thread.is_alive():
            self.stop_event.set()
            self.wallpaper_thread.join()
            messagebox.showinfo("Stopped", "Wallpaper changer has been stopped.")
        else:
            messagebox.showinfo("Not Running", "The wallpaper changer is not running.")

    def save_settings(self):
        settings = {
            'selected_categories': {k: v.get() for k, v in self.selected_categories.items()},
            'change_interval': self.change_interval.get(),
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            for k, v in settings.get('selected_categories', {}).items():
                self.selected_categories[k].set(v)
            self.change_interval.set(settings.get('change_interval', 60))

    def save_usage_counts(self):
        with open('usage_counts.json', 'w') as f:
            json.dump(self.usage_counts, f)

    def load_usage_counts(self):
        if os.path.exists('usage_counts.json'):
            with open('usage_counts.json', 'r') as f:
                self.usage_counts = json.load(f)
        else:
            self.usage_counts = {}

    def on_closing(self):
        self.stop_changing_wallpapers()
        self.destroy()
