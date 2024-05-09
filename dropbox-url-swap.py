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



from distutils.log import error
import os
import time
from subprocess import run
import requests
import json
import datetime
import sh
    

from AppKit import NSArray, NSPasteboard, NSStringPboardType  # type: ignore

LINK_FETCHER='/Users/chris/Dropbox/workspace-defiant/dropbox-link-service/dbx_link_fetcher.sh'
LINK_FETCHER_IMAGE=[LINK_FETCHER]
LINK_FETCHER_CAPTURE=[LINK_FETCHER, "capture"]
#############
# with these extensions, we give an even better direct link that doesn't do a redirect.
# Sadly this only works for a whitelist of file types which Dropbox decides are safe to serve from a predictable URL.
# for example: .PDF files aren't served raw predictably because if they contain links, clicking a link to a 3rd party site
# could reveal the secret URL in the Referrer header.  (for old browsers that don't support "Referrer-Policy:")
extra_direct_extensions = ['jpg','png', 'mp3', 'mov', 'mp4', 'mkv','tiff','gif','sh','txt','md','jpeg','heic','toml','cfg','conf','ini','json','xml','yml','yaml','csv','tsv','zip','gz','tar','tgz','bz2','7z','rar','iso','dmg','exe','msi','deb','rpm','pkg','apk','ipa','app','jar','war','ear','class','py','html','htm','js','css','scss','less','sass','xml']
#############



class DropboxLinkFixer:
    def __init__(self, interval=1):
        self.pb = NSPasteboard.generalPasteboard()
        self.interval = interval

    def start(self):
        last_count = 0  # so we check the pasteboard when we start
        while True:
            if last_count != self.pb.changeCount():
                bonus_sleep_time = 3

                last_count = self.pb.changeCount()
                clip = self.read_from_clipboard()
                if (clip and
                        ('?dl=0' in clip and
                        clip.lstrip().startswith('https://www.dropbox.com/s') and '.' in clip.split("?dl=0")[0][-5:-2])
                    or
                        (clip and clip.lstrip().startswith('https://capture.dropbox.com/') and "?" not in clip and '?raw=' not in clip and "?dl=" not in clip)
                    ):
                    print('updated clipboard has a dropbox/capture shared link in it! Will now update this link: ', clip, flush=True)

                    if 'https://www.dropbox.com/s' in clip:
                        if any([f".{e}?dl=" in clip.lower() for e in extra_direct_extensions]):
                            clip = clip.replace('https://www.dropbox.com/s', 'https://dl.dropboxusercontent.com/s')
                            clip = clip.replace('?dl=0', '')
                        else:
                            clip = clip.replace('?dl=0', '?raw=1')
                    elif 'https://capture.dropbox.com/' in clip:
                        print("capture.dropbox.com link detected, adding '?raw=1' to the end of the URL... ",flush=True)
                        clip = f"{clip}?raw=1"
                        self.write_to_clipboard(clip)
                        print("Following capture link to get the real dropbox.com shared link...")
                        time.sleep(0)
                        clip=get_dbx_link_from_capture_link(clip)
                        print(f"Got this DBX link...writing to clipboard. DBX_LINK=",clip,flush=True)
                        self.write_to_clipboard(clip)

                        # print("sleeping, and then running 'dbx_get_latest'...",flush=True)
                        # time.sleep(2)

                        # error_count=0
                        # ERROR_LIMIT=6
                        # while True:
                        #     try:
                        #         clip = dbx_get_latest() 
                        #     except Exception as e:
                        #         error_count+=1
                        #         if error_count >= ERROR_LIMIT:
                        #             print(f"Fetch failed.. {error_count}, GIVING UP",flush=True)
                        #             raise e
                        #         print(f"Fetch failed.. {error_count}, sleeping... ",flush=True)
                        #         time.sleep(1+error_count*1.5)
                        #         continue
                        #     break
                                


                        # time.sleep(2)
                        # try:
                        #     clip = dbx_get_latest() 
                        # except Exception as e:
                        #     print("First link fetch failed, sleeping:",e,flush=True)
                        #     time.sleep(3)
                        #     try:
                        #         clip = dbx_get_latest() 
                        #     except Exception as e:
                        #         print("2nd link fetch failed, sleeping:",e,flush=True)
                        #         time.sleep(7)
                        #         try:
                        #             clip = dbx_get_latest() 
                        #         except Exception as e:
                        #             print("3rd link fetch failed, sleeping big time:",e,flush=True)
                        #             time.sleep(15)
                        #             clip = dbx_get_latest() 

                        # time.sleep(15)  ## need to sleep to give Dropbox API time to catch up
                        # clip = dbx_get_latest() 
                        print("new clipboard: ", clip)

                        # bonus_sleep_time = 0
                        # # os.system("/tmp/testo.sh")
                        # if "Recording" in clip:
                        #     TO_RUN=LINK_FETCHER_CAPTURE
                        # else:
                        #     TO_RUN=LINK_FETCHER_IMAGE
            
                        # p = run( TO_RUN, shell=True, capture_output=True )
                        # if p.returncode == 0:
                        #     print("ZSH RETURNS:",p.stdout.decode('utf-8'))
                        #     clip=p.stdout.decode('utf-8')


                    self.write_to_clipboard(clip)

                    if bonus_sleep_time:
                        time.sleep(bonus_sleep_time)
                    else:
                        print("immediately retrying loop without sleeping")
                        continue

                # elif (clip and '?src=ss' in clip and clip.lstrip().startswith('https://capture.dropbox.com/')):
                #     clip = clip.replace('?src=ss', '?raw=1')
                #     self.write_to_clipboard(clip)
                #     time.sleep(3)
                else:
                    print(f"clipboard changed, but not a dropbox shared link.  Change count={self.pb.changeCount()}", flush=True)
            time.sleep(self.interval)

    def read_from_clipboard(self):
        return self.pb.stringForType_(NSStringPboardType) 

    def write_to_clipboard(self, output):
        self.pb.clearContents()
        a = NSArray.arrayWithObject_(output)
        self.pb.writeObjects_(a)

def get_dbx_link_from_capture_link(capture_link):
    if '?raw=1' not in capture_link:
        raise Exception("capture link must have '?raw=1' in it")
    print("capture_link=",capture_link)
    redirect1=get_redirect_location(capture_link)
    print("redirect1=",redirect1)
    redirect2=get_redirect_location(redirect1)
    print("redirect2=",redirect2)
    return redirect2.replace('?dl=0&raw=1','?dl=0')

def get_redirect_location(url):
    r = requests.head(url, allow_redirects=False)
    if r.status_code != 302 and r.status_code != 301:
        raise Exception(f"When fetching '{url}' expected 302 redirect, got {r.status_code}")
    return r.headers['Location']

# def dbx_get_latest():




#     headers = {
#         "Authorization": "Bearer J1wRaRG0ZjsAAAAAAAG9d9rN63UttPaTnGz0Qsq5aebcg5Q4voN37HvsJq9ElYNM",
#         "Content-Type": "application/json"
#     }

#     r1 = requests.post("https://api.dropboxapi.com/2/files/list_folder", headers=headers, data=json.dumps({"path": "/Capture"}))
#     f1 = r1.json()['entries'][-1]

#     r2 = requests.post("https://api.dropboxapi.com/2/files/list_folder/continue", headers=headers, data=json.dumps({"cursor":"AAGX-GvodEqjwGlyx9Zod2gR1cLc9rhXvFO2pfhJA2soxnuPtTNJO7K6CXS8H57DvWz5pm9HFS49H7NF5ed09Bq2IiYpjyBy3uc124OCBGawsgKeyShTEiNCuzznNL_oyMXlq4T3Spf5WZ0_ECXTwbN-ccyKrhc-Hv3A8yLgivY8hOmz9UkrYED904z4l7WsJ_7eGhYBXON_a6IoHIrybpwrBHaPk0yhbjgWGrP-95h9MQ"}))
#     f2 = r2.json()['entries'][-1]

#     d1=datetime.datetime.strptime(f1['server_modified'], '%Y-%m-%dT%H:%M:%SZ')
#     d2=datetime.datetime.strptime(f2['server_modified'], '%Y-%m-%dT%H:%M:%SZ')

#     if d1>d2:
#         LINK_PATH=f1['path_lower']
#     else:
#         LINK_PATH=f2['path_lower']
    
#     print("new link_path", LINK_PATH)

#     r=requests.post("https://api.dropboxapi.com/2/sharing/list_shared_links", headers=headers, data=json.dumps({"path": LINK_PATH}))
#     print(r.json())

#     return r.json()['links'][0]['url']



if __name__ == "__main__":
    # execute only if run as a script
    print('starting Dropbox link fixer daemon.', flush=True)

    d = DropboxLinkFixer()
    d.start()
