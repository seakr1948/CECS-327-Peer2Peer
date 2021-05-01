import time
import os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class Watcher():
    def __init__(self, path):
        self.complete_path = path
        self.relative_path = os.path.relpath(path)
        self.event_handler = PatternMatchingEventHandler("*", "", False, True)
        
        self.event_handler.on_created = self.on_created
        self.event_handler.on_deleted = self.on_deleted
        self.event_handler.on_modified = self.on_modified
        self.event_handler.on_moved = self.on_moved

        self.my_observer = Observer()
        self.my_observer.schedule(self.event_handler, self.complete_path, recursive=True)
    
    def start_Watching(self):
        self.my_observer.start()

    def stop_Watching(self):
        self.my_observer.stop()
        self.my_observer.join()

    def on_created(self, event):
        print(f"{event.src_path} has been created.")

    def on_deleted(self, event):
        print(f"{event.src_path} has been deleted.")

    def on_modified(self, event):
        print(f"{event.src_path} has been modified.")

    def on_moved(self, event):
        print(f"{event.src_path} has been moved to {event.dest_path}.")


if __name__ == "__main__":
    #path = os.path.join(os.getcwd(),"TestFolder")
    path = os.getcwd()
    print("Path: " + path)
    watch = Watcher(path)
    watch.start_Watching()

    time.sleep(20)
    watch.stop_Watching()
    
    print("done")