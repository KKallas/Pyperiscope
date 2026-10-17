import os
import threading
import time
from PIL import Image, ImageFile

# Enable truncated image loading
ImageFile.LOAD_TRUNCATED_IMAGES = True

class FileWatcher:
    """Robust file watcher with write completion detection"""
    def __init__(self, binoculars, base_path):
        self.binoculars = binoculars
        self.base_path = base_path
        self.current_index = 0
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def get_current_path(self):
        return f"{self.base_path}-{self.current_index}.png"

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.monitor_sequence)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def monitor_sequence(self):
        self.current_index = self._find_lowest_index()
        last_processed_path = None  # Track last processed file
        
        while self.running:
            current_path = self.get_current_path()
            
            # Skip if we've already processed this file
            if current_path == last_processed_path:
                self.current_index += 1
                continue
                
            if os.path.exists(current_path):
                if self._wait_for_file(current_path):
                    try:
                        with self.lock:
                            self.binoculars._update_from_screenshot(current_path)
                            last_processed_path = current_path
                            self.current_index += 1
                            print(f"Processed {current_path}, waiting for {self.get_current_path()}")
                    except Exception as e:
                        print(f"Error processing {current_path}: {str(e)}")
                        self.current_index += 1  # Prevent blocking
            else:
                time.sleep(0.1)

    def _find_lowest_index(self):
        """Find the lowest index that needs processing."""
        index = 0
        while True:
            current_path = f"{self.base_path}-{index}.png"
            if not os.path.exists(current_path):
                return max(0, index - 1)  # Return previous index if files exist
            index += 1
        return 0
    
    def _wait_for_file(self, path, timeout=5):
        """Wait for file to stabilize and become readable"""
        start_time = time.time()
        last_size = -1
        stable_count = 0

        while time.time() - start_time < timeout:
            try:
                current_size = os.path.getsize(path)
                if current_size == last_size:
                    stable_count += 1
                    if stable_count > 3:  # 300ms stability
                        if self._validate_image(path):
                            return True
                else:
                    last_size = current_size
                    stable_count = 0
                time.sleep(0.1)
            except FileNotFoundError:
                time.sleep(0.1)

        return False

    def _validate_image(self, path):
        """Verify image can be loaded"""
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except Exception:
            return False