import subprocess
import time
import sys
import os
#sys.stdout = open("/tmp/dropbox-link-service.txt", "w+")

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler  

import logging
# import threading



def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))


def read_from_clipboard():
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


class MyHandler(PatternMatchingEventHandler):
    def on_created(self, event):
        super(MyHandler, self).on_created(event)

        print('handling new event!!!!!', flush=True)
        # ethread = threading.Thread(target=thing_created, args=(event,))
        # ethread.start()
        thing_created(event)

def thing_created(event):
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
            # print('exiting myself...', flush=True)
            # observer.stop()
            # os._exit(0)
            # raise ExitCommand()
            # exit(1)
            return

        else:
            print('failed to find ?dl=0 in clipboard..', clip, flush=True)
        time.sleep(0.3)
    return
    


print('starting up!', flush=True)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
path = "/Users/chris/Desktop"


observer = None

def setup_observer():
    observer = Observer()
    #event_handler = LoggingEventHandler()
    #event_handler = MyHandler()
    event_handler = PatternMatchingEventHandler(patterns=["*Screen Shot*.png"],
                    ignore_patterns=[],
                    ignore_directories=True)
    event_handler.on_created = thing_created
    # observer.schedule(MyHandler(), path, recursive=False)
    observer.schedule(event_handler, path, recursive=False)
    observer.daemon=False
    observer.start()
    return observer

try:
    observer_old = None
    for x in range(0,600):
        observer = setup_observer()
        time.sleep(20)
        observer.unschedule_all()
        observer.stop()
        observer.join()
        del observer
        print('restarting watcher...', flush=True)
except:
    import traceback
    traceback.print_exc()
finally:
    print('exiting!')
    if observer:
	    observer.unschedule_all()
	    observer.stop()
    os._exit(1)

