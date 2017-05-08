## Full-Page Rendering

People normally use React to make _part_ of the page dynamic in some way (imagine a live weather widget on an otherwise static page). _encoded_ uses full-page rendering, having React produce everything including the `<html>` tags. Facebook doesn’t [prefer](https://groups.google.com/forum/#!topic/reactjs/4jI5xe7TXzQ) full-page rendering, but has kept grudging support for it as long as you use server rendering.

## Server Rendering

_encoded_ uses React server rendering, so even before Javascript starts operating on your web browser, React has already rendered the HTML of the page on the server — except for anything that changes because of user input (e.g. dropping down a menu) or that gets loaded into the page after the page loads (e.g. data not built into the displayed ENCODE object itself, but needs display anyway) — and sent the completed HTML to your web browser.

After the page with the server-rendered HTML loads in the web browser, React Javascript running in the web browser treats the HTML on the page as if it had rendered the page itself — as React normally does without server rendering.

## Web Browser Startup Procedure

After the page loads in the web browser, the first code run exists in [browser.js](src/encoded/static/browser.js). This code does _not_ run during server rendering — it runs in the web browser only.