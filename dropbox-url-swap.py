####### Dropbox link fixers for macOS ########
# This daemon converts all Dropbox shared links in the clipboard to direct links. The url provide the raw files instead of all the Dropbox bloat/previews.
# To run, just do
# $ python3 ./dropbox-url-swap.py
#
# (requires python3.6+ with f-string support)
# To fix the Dropbox links it usually just changes the "dl=0" query arg into the rather obscure "raw=1" option. 
# Though for certain type it provides an even more direct link that isn't delayed by an instant redirect.
#
# To provide this we have to poll the clipboard to monitor for changes, but by using the Darwin NSPasteboard
# API directly this ends up being very efficient. Vastly more efficient than constantly calling out to 
# the `pbpaste` and reading the STDIN.



import time
import logging
from AppKit import NSPasteboard, NSStringPboardType, NSArray


#############
# with these extensions, we give an even better direct link that doesn't do a redirect.
# Sadly this only works for a whitelist of file types which Dropbox decides are safe to serve from a predictable URL.
# for example: .PDF files aren't served raw predictably because if they contain links, clicking a link to a 3rd party site
# could reveal the secret URL in the Referrer header.  (for old browsers that don't support "Referrer-Policy:")
extra_direct_extensions = ['jpg','png', 'mp3', 'mov', 'mp4', 'mkv','tiff','gif','sh','txt','md','jpeg']
#############



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
                if (clip and
                    '?dl=0' in clip and
                    clip.lstrip().startswith('https://www.dropbox.com/s') and '.' in clip.split("?dl=0")[0][-5:-2]):
                    print('updated clipboard has a dropbox shared link in it! Fixing the link.', flush=True)
                    if any([f".{e}?dl=" in clip for e in extra_direct_extensions]):
                        clip = clip.replace('https://www.dropbox.com/s', 'https://dl.dropboxusercontent.com/s')
                        clip = clip.replace('?dl=0', '')
                    else:
                        clip = clip.replace('?dl=0', '?raw=1')
                    self.write_to_clipboard(clip)
                    time.sleep(3)

                else:
                    print(f"clipboard changed, but not a dropbox shared link.  Change count={self.pb.changeCount()}", flush=True)
            time.sleep(self.interval)

    def read_from_clipboard(self):
        return self.pb.stringForType_(NSStringPboardType) 

    def write_to_clipboard(self, output):
        self.pb.clearContents()
        a = NSArray.arrayWithObject_(output)
        self.pb.writeObjects_(a)


if __name__ == "__main__":
    # execute only if run as a script
    print('starting Dropbox link fixer daemon.', flush=True)

    d = DropboxLinkFixer()
    d.start()
