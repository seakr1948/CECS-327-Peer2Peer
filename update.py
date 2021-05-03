import os

def update(event, file = None, meta = None):
    watcher.stop_Watching() #stop the watcher so we don't loop updates

    event_type = event["EVENT_TYPE"]
    #which event will determine next steps
    if event_type == "deleted": 
        deletion(event)
    elif event_type == "created":
        creation(event, file, meta)
    elif event_type == "modified": 
        deletion(event)
        creation(event, file, meta)
    elif event_type == "moved":
        rename(event)
    
    watcher.start_Watching()

#rename event
def rename(event):
    os.rename(event[PATH_SRC, event[PATH_DEST]])

#deletion event
def deletion(event):
    if even[IS_DIRECTORY]:
        os.rmdir(event[PATH_SRC])
    else:
        os.remove(event[PATH_SRC])

#creation event
def creation(event, file, meta):
    #create the new file
    file_path = event[PATH_SRC]
    file_name = os.path.basename(file_path)
    with open(file_path, 'w') as f:
        pass

    #####
    #USING 'file' AND 'meta', SET THE FILE file_name
    #####
    
    

if __name__ == "__main__":
    path = r"C:\Users\Daniel\Desktop\CECS-327-Peer2Peer-update-function\CECS-327-Peer2Peer-update-function\fileSystemHelpers"
    print(path)
    print(os.path.basename(path))
    with open(path + r"\test.txt", 'w') as fp:
        pass