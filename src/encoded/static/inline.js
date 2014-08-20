// ie8 compat.
(function(tags) {for (var i=0, l=tags.length; i<l; i++) document.createElement(tags[i]); })([
"article",
"aside",
"figcaption",
"figure",
"footer",
"header",
"hgroup",
"nav",
"section"]);

// Universal analytics snippet.
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

// Use a separate tracker for dev / test
if (({'www.encodeproject.org':1, 'www.encodedcc.org':1})[document.location.hostname]) {
    ga('create', 'UA-47809317-1', {'siteSpeedSampleRate': 100});
} else {
    ga('create', 'UA-47809317-2', {'cookieDomain': 'none', 'siteSpeedSampleRate': 100});
}
ga('send', 'pageview');


// Need to know if onload event has fired for safe history api usage.
window.onload = function () { window._onload_event_fired; }

$script.path('/static/build/');
$script('https://login.persona.org/include.js', 'persona');
