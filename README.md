## Dropbox Shared Link Fixer Service

I find that Dropbox shared links are filled with unnecessary distractions 99% of the time.  When I share a link to a file, I want only that file to be returned. This also has the advantage that you can hot-link images directly.

This service is a macOS daemon that sits in the background, observing pasteboard changes, and when it finds a Dropbox shared link, it fixes the link to make it a direct link.

- For example, it turns this URL: `https://www.dropbox.com/s/jg60xxxxxxxx/Some_Image.jpg?dl=0`
- Into this: `https://dl.dropboxusercontent.com/s/jg60xxxxxxxx/Some_Image.jpg`, which returns the content directly

### Instructions for Running

1. Make sure you have Python 3.6 or later installed on your macOS system.
2. Clone this repository or download the `dropbox-url-swap.py` file.
3. Open a terminal and navigate to the directory where the `dropbox-url-swap.py` file is located.
4. Run the following command to start the daemon:
5. The daemon will now run in the background, monitoring your clipboard for Dropbox shared links and automatically fixing them.
6. To stop the daemon, press `Ctrl+C` in the terminal where it's running.

Note: The daemon requires the `AppKit` module, which is specific to macOS. Make sure you have the necessary dependencies installed.

### TODO:
- Instructions for turning this into a macOS launchd service so that it always runs automatically.

<br/>
<br/>
<br/>
<hr/>

*Fun Fact:* The reason why all Dropbox shared links have '?dl=0' at the end is hilarious. It has no effect, since `dl` defaults to `0`. It was added as a quick hack to fix an issue with older versions of Microsoft Word assuming a URL's extension matches the file's type. Now it's returned forever on every Dropbox shared link and would no doubt be a pain to remove.
