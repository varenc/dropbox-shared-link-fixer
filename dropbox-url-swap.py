####### Dropbox shared link fixer for macOS ########
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
#
# 2024 updates!
# Dropbox has no, for reasons beyond me, added an 'rlkey=' key to the shared link. Guess it's more secure if the bits of entropy are in the query args not the URL? 🤷‍♂️
# - Update to handle the 'rlkey=' key in the shared link.
# - Handling capture.dropbox.com links and there many redirects
# - Do direct link redirection for many file types (but not PDF, which Dropbox forbids on predictable URLs to protect from referer leakage)
#


from AppKit import NSArray, NSPasteboard, NSStringPboardType  # type: ignore
import requests
import time

extra_direct_extensions = ['jpg', 'png', 'mp3', 'mov', 'mp4', 'mkv', 'tiff', 'gif', 'sh', 'txt', 'md', 'jpeg', 'heic', 'toml', 'cfg', 'conf', 'ini', 'json', 'xml', 'yml', 'yaml', 'csv', 'tsv', 'zip', 'gz', 'tar', 'tgz', 'bz2', '7z', 'rar', 'iso', 'dmg', 'exe', 'msi', 'deb', 'rpm', 'pkg', 'apk', 'ipa', 'app', 'jar', 'war', 'ear', 'class', 'py', 'html', 'htm', 'js', 'css', 'scss', 'less', 'sass', 'xml']

class DropboxLinkFixer:
    def __init__(self, interval=1):
        self.pb = NSPasteboard.generalPasteboard()
        self.interval = interval

    def start(self):
        last_count = 0
        while True:
            if last_count != self.pb.changeCount():
                bonus_sleep_time = 3
                last_count = self.pb.changeCount()
                clip = self.read_from_clipboard()

                if self.is_dropbox_shared_link(clip):
                    print('updated clipboard has a dropbox shared link in it! Will now update this link: ', clip, flush=True)

                    if self.has_extra_direct_extension(clip):
                        clip = self.convert_to_direct_link(clip)
                    else:
                        clip = self.convert_to_raw_link(clip)

                    if 'https://capture.dropbox.com/' in clip:
                        print("capture.dropbox.com link detected, adding '?raw=1' to the end of the URL... ", flush=True)
                        clip = f"{clip}?raw=1"
                        self.write_to_clipboard(clip)
                        print("Following capture link to get the real dropbox.com shared link...")
                        time.sleep(0)
                        clip = get_dbx_link_from_capture_link(clip)
                        print(f"Got this DBX link...writing to clipboard. DBX_LINK=", clip, flush=True)
                        self.write_to_clipboard(clip)

                    self.write_to_clipboard(clip)

                    if bonus_sleep_time:
                        time.sleep(bonus_sleep_time)
                    else:
                        print("immediately retrying loop without sleeping")
                        continue
                else:
                    print(f"clipboard changed, but not a dropbox shared link.  Change count={self.pb.changeCount()}", flush=True)
            time.sleep(self.interval)

    def read_from_clipboard(self):
        return self.pb.stringForType_(NSStringPboardType)

    def write_to_clipboard(self, output):
        self.pb.clearContents()
        a = NSArray.arrayWithObject_(output)
        self.pb.writeObjects_(a)

    def is_dropbox_shared_link(self, clip):
        return (clip and
                (('?dl=0' in clip or ('?rlkey=' in clip and '&dl=0' in clip))
                 and clip.lstrip().startswith('https://www.dropbox.com/s')
                 and ('.' in clip.split("?dl=0")[0][-5:-2] or '.' in clip.split("?rlkey=")[0][-5:-2]))
                or
                (clip
                 and clip.lstrip().startswith('https://capture.dropbox.com/')
                 and "?" not in clip))

    def has_extra_direct_extension(self, clip):
        lowercase_clip = clip.lower()
        return any(f".{e}?dl=" in lowercase_clip or f".{e}?rlkey=" in lowercase_clip for e in extra_direct_extensions)

    def convert_to_direct_link(self, clip):
        clip = clip.replace('https://www.dropbox.com/s', 'https://dl.dropboxusercontent.com/s')
        clip = clip.replace('?dl=0', '')
        clip = clip.replace('&dl=0', '')
        return clip

    def convert_to_raw_link(self, clip):
        clip = clip.replace('?dl=0', '?raw=1')
        clip = clip.replace('&dl=0', '&raw=1')
        return clip

def get_dbx_link_from_capture_link(capture_link):
    if '?raw=1' not in capture_link:
        raise Exception("capture link must have '?raw=1' in it")
    print("capture_link=", capture_link)
    redirect1 = get_redirect_location(capture_link)
    print("redirect1=", redirect1)
    redirect2 = get_redirect_location(redirect1)
    print("redirect2=", redirect2)
    return redirect2.replace('?dl=0&raw=1', '?dl=0')

def get_redirect_location(url):
    r = requests.head(url, allow_redirects=False)
    if r.status_code != 302 and r.status_code != 301:
        raise Exception(f"When fetching '{url}' expected 302 redirect, got {r.status_code}")
    return r.headers['Location']

if __name__ == "__main__":
    print('starting Dropbox link fixer daemon.', flush=True)
    d = DropboxLinkFixer()
    d.start()