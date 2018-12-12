import subprocess
import time
import sys
#sys.stdout = open("/tmp/dropbox-link-service.txt", "w+")


def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))


def read_from_clipboard():
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')

old_clip = read_from_clipboard()
while True:
    clip = read_from_clipboard()
    if old_clip != clip:
        #print('clipboard changed!')
        if '?dl=0' in clip:
            print('clipboard has a dropbox url in it! swapping...', flush=True)
            clip = clip.replace('?dl=0', '?raw=1')
            write_to_clipboard(clip)
    old_clip = clip
    time.sleep(2)
    
