
import time
import logging
from AppKit import NSPasteboard, NSStringPboardType, NSArray

# Makes all Dropbox shared links direct links. You get the raw files instead of all the Dropbox bloat.
# To do this it just changes the "dl=0" query arg into the rather obscure "raw=1" option.
# To do this automatically it polls the clipboard monitoring for changes.  In practice the polling cost seems quite minimal

class DropboxLinkFixer:
    def __init__(self, interval=1):
        self.pb = NSPasteboard.generalPasteboard()
        self.interval = interval

    def start(self):
        last_count = 0  # so we check the pasteboard when we start
        while True:
            if last_count != self.pb.changeCount():

                last_count = self.pb.changeCount()
                clip = self.read_from_clipboard()
                if '?dl=0' in clip and clip.lstrip().startswith('https://www.dropbox.com/s'):
                    print('updated clipboard has a dropbox shared link in it! Fixing the link.', flush=True)
                    clip = clip.replace('?dl=0', '?raw=1')
                    self.write_to_clipboard(clip)
                    time.sleep(3)

                else:
                    print('clipboard changed, but not a dropbox shared link', flush=True)
            time.sleep(self.interval)
        

    def read_from_clipboard(self):
        return self.pb.stringForType_(NSStringPboardType) 

    def write_to_clipboard(self, output):
        self.pb.clearContents()
        a = NSArray.arrayWithObject_(output)
        self.pb.writeObjects_(a)


print('starting Dropbox link fixer daemon.', flush=True)

d = DropboxLinkFixer()
d.start()


