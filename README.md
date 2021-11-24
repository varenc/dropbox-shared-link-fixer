## Dropbox shared link fixer service


I find that Dropbox shared links are filled with useless crap 99% of the time.  When I share a link to a file, I want ONLY that file to be returned.  Also has advantages link now you can hot-link images directly.


This service is for macOS and just sits in the background, observing pasteboard changes, and when it finds one it fixes the Dropbox link so that it's now a direct link.

- For example it turns this URL: `https://www.dropbox.com/s/jg60xxxxxxxx/Some_Image.jpg?dl=0`
- Into this: `https://dl.dropboxusercontent.com/s/jg60xxxxxxxx/Some_Image.jpg`, which returns the content directly

TODO:
Instructions for running



<br/>
<br/>
<br/>
<hr/>

*Fun Fact:* The reason why all links have '?dl=0' at the ends is hilarious... It has no effect, since `dl` defaults to `0`.  It was added as a quick hack to fix an issue with older versions of Microsoft Word assuming a URL's extension matches the file's type. Now it's returned forever on every Dropbox shared link and would no doubt be a pain to remove.
