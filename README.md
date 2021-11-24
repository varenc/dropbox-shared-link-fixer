## Dropbox shared link fixer service


I find that Dropbox shared links are filled with useless crap 99% of the time.  When I share a link to a file, I want ONLY that file to be returned.  Also has advantages link now you can hot-link images directly.


This service is for macOS and just sits in the background, observing pasteboard changes, and when it finds one it fixes the Dropbox link so that it's now a direct link.

- For example it turns this: `https://www.dropbox.com/s/jg60xxxxxxxx/Some_Image.jpg`
- Info this: `https://dl.dropboxusercontent.com/s/jg60xxxxxxxx/Some_Image.jpg`, which returns the content directly

TODO:
Instructions for running
