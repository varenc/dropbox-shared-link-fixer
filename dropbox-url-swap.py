import subprocess
import time
import sys
#sys.stdout = open("/tmp/dropbox-link-service.txt", "w+")

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler  

import logging
import threading



def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))


def read_from_clipboard():
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


class MyHandler(PatternMatchingEventHandler):
    def on_created(self, event):
        print('handling new event!!!!!', flush=True)
        ethread = threading.Thread(target=event_handler, args=(event,))
        ethread.start()
        #event_handler(event)

def event_handler(event):
    if any(x in event.src_path.lower() for x in ['screen shot', 'screenshot']):
        print('SCREEN SHOT MATCH!!!!!!!!!', event.src_path, flush=True)
    else:
        print('faaillll', event.src_path, flush=True)
        return

    for i in range(15): # give dropbox 15 * 0.3 seconds
        clip = read_from_clipboard()
        if '?dl=0' in clip:
            print('clipboard has a dropbox url in it! swapping...', flush=True)
            clip = clip.replace('?dl=0', '?raw=1')
            write_to_clipboard(clip)
            return
        else:
            print('failed on', clip, flush=True)
        time.sleep(0.3)
    return
    


print('starting up!!!!!', flush=True)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
path = "/Users/chris/Desktop"
observer = Observer()
#event_handler = LoggingEventHandler()
#event_handler = MyHandler()
observer.schedule(MyHandler(), path, recursive=False)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()

