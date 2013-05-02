/******************************************************************************
uri_funcs.js - URI functions based on STD 66 / RFC 3986

  Author (original): Mike J. Brown <mike at skew.org>
  Version: 2007-01-04

  License: Unrestricted use and distribution with any modifications permitted,
  so long as:
  1. Modifications are attributed to their author(s);
  2. The original author remains credited;
  3. Additions derived from other code libraries are credited to their sources
  and used under the terms of their licenses.

*******************************************************************************/

/*
uriRefIsAbsolute(uriRef)

This function determines whether the given URI reference is absolute
(has a scheme).
*/
var absoluteUriRefRegex = /^[A-Z][0-9A-Z+\-\.]*:/i;
function uriRefIsAbsolute(uriRef) {
	return absoluteUriRefRegex.test(uriRef);
}

/*
splitUriRef(uriRef)

This function splits a URI reference into an Array of its principal components,
[scheme, authority, path, query, fragment] as per STD 66 / RFC 3986 appendix B.
*/
var splitUriRefRegex = /^(([^:\/?#]+):)?(\/\/([^\/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?$/;
var reMissingGroupSupport = (typeof "".match(/(a)?/)[1] != "string");
function splitUriRef(uriRef) {
	var parts = uriRef.match(splitUriRefRegex);
	parts.shift();
	var scheme=parts[1], auth=parts[3], path=parts[4], query=parts[6], frag=parts[8];
	if (!reMissingGroupSupport) {
		var undef;
		if (parts[0] == "") scheme = undef;
		if (parts[2] == "") auth = undef;
		if (parts[5] == "") query = undef;
		if (parts[7] == "") frag = undef;
	}
	parts = [scheme, auth, path, query, frag];
	return parts;
}

/*
unsplitUriRef(uriRefSeq)

This function, given an Array as would be produced by splitUriRef(),
assembles and returns a URI reference as a string.
*/
function unsplitUriRef(uriRefSeq) {
    var uriRef = "";
    if (typeof uriRefSeq[0] != "undefined") uriRef += uriRefSeq[0] + ":";
    if (typeof uriRefSeq[1] != "undefined") uriRef += "//" + uriRefSeq[1];
    uriRef += uriRefSeq[2];
    if (typeof uriRefSeq[3] != "undefined") uriRef += "?" + uriRefSeq[3];
    if (typeof uriRefSeq[4] != "undefined") uriRef += "#" + uriRefSeq[4];
    return uriRef;
}

/*
uriPathRemoveDotSegments(path)

This function supports absolutizeURI() by implementing the remove_dot_segments
function described in RFC 3986 sec. 5.2.  It collapses most of the '.' and '..'
segments out of a path without eliminating empty segments. It is intended
to be used during the path merging process and may not give expected
results when used independently.

Based on code from 4Suite XML:
http://cvs.4suite.org/viewcvs/4Suite/Ft/Lib/Uri.py?view=markup
*/
function uriPathRemoveDotSegments(path) {
	// return empty string if entire path is just "." or ".."
	if (path == "." || path == "..") {
		return "";
	}
	// remove all "./" or "../" segments at the beginning
	while (path) {
		if (path.substring(0,2) == "./") {
			path = path.substring(2);
		} else if (path.substring(0,3) == "../") {
			path = path.substring(3);
		} else {
			break;
		}
	}
	// We need to keep track of whether there was a leading slash,
	// because we're going to drop it in order to prevent our list of
	// segments from having an ambiguous empty first item when we call
	// split().
	var leading_slash = false;
	if (path.charAt(0) == "/") {
		path = path.substring(1);
		leading_slash = true;
	}
	// replace a trailing "/." with just "/"
	if (path.substring(path.length - 2) == "/.") {
		path = path.substring(0, path.length - 1);
	}
	// convert the segments into a list and process each segment in
	// order from left to right.
	var segments = path.split("/");
	var keepers = [];
	segments = segments.reverse();
	while (segments.length) {
		var seg = segments.pop();
		// '..' means drop the previous kept segment, if any.
		// If none, and if the path is relative, then keep the '..'.
		// If the '..' was the last segment, ensure
		// that the result ends with '/'.
		if (seg == "..") {
			if (keepers.length) {
				keepers.pop();
			} else if (! leading_slash) {
				keepers.push(seg);
			}
			if (! segments.length) {
				keepers.push("");
			}
		// ignore '.' segments and keep all others, even empty ones
		} else if (seg != ".") {
			keepers.push(seg);
		}
	}
	// reassemble the kept segments
	return (leading_slash && "/" || "") + keepers.join("/");
}

/*
absolutizeURI(uriRef, baseUri)

This function resolves a URI reference to absolute form as per section 5 of
STD 66 / RFC 3986. The URI reference is considered to be relative to the
given base URI.

It is the caller's responsibility to ensure that the base URI matches
the absolute-URI syntax rule of RFC 3986, and that its path component
does not contain '.' or '..' segments if the scheme is hierarchical.
Unexpected results may occur otherwise.

Based on code from 4Suite XML:
http://cvs.4suite.org/viewcvs/4Suite/Ft/Lib/Uri.py?view=markup
*/
function absolutizeURI(uriRef, baseUri) {
	// Ensure base URI is absolute
	if (! baseUri || ! uriRefIsAbsolute(baseUri)) {
		 throw Error("baseUri '" + baseUri + "' is not absolute");
	}
	// shortcut for the simplest same-document reference cases
	if (uriRef == "" || uriRef.charAt(0) == "#") {
		return baseUri.split('#')[0] + uriRef;
	}
	var tScheme, tAuth, tPath, tQuery;
	// parse the reference into its components
	var parts = splitUriRef(uriRef);
	var rScheme=parts[0], rAuth=parts[1], rPath=parts[2], rQuery=parts[3], rFrag=parts[4];
	// if the reference is absolute, eliminate '.' and '..' path segments
	// and skip to the end
	if (typeof rScheme != "undefined") {
		var tScheme = rScheme;
		var tAuth = rAuth;
		var tPath = uriPathRemoveDotSegments(rPath);
		var tQuery = rQuery;
	} else {
		// the base URI's scheme, and possibly more, will be inherited
		parts = splitUriRef(baseUri);
		var bScheme=parts[0], bAuth=parts[1], bPath=parts[2], bQuery=parts[3], bFrag=parts[4];
		// if the reference is a net-path, just eliminate '.' and '..' path
		// segments; no other changes needed.
		if (typeof rAuth != "undefined") {
			tAuth = rAuth;
			tPath = uriPathRemoveDotSegments(rPath);
			tQuery = rQuery;
		// if it's not a net-path, we need to inherit pieces of the base URI
		} else {
			// use base URI's path if the reference's path is empty
			if (! rPath) {
				tPath = bPath;
				// use the reference's query, if any, or else the base URI's,
				tQuery = (typeof rQuery != "undefined" && rQuery || bQuery);
			// the reference's path is not empty
			} else {
				// just use the reference's path if it's absolute
				if (rPath.charAt(0) == "/") {
					tPath = uriPathRemoveDotSegments(rPath);
				// merge the reference's relative path with the base URI's path
				} else {
					if (typeof bAuth != "undefined" && ! bPath) {
						tPath = "/" + rPath;
					} else {
						tPath = bPath.substring(0, bPath.lastIndexOf("/") + 1) + rPath;
					}
					tPath = uriPathRemoveDotSegments(tPath);
				}
				// use the reference's query
				tQuery = rQuery;
			}
			// since the reference isn't a net-path,
			// use the authority from the base URI
			tAuth = bAuth;
		}
		// inherit the scheme from the base URI
		tScheme = bScheme;
	}
	// always use the reference's fragment (but no need to define another var)
	//tFrag = rFrag;
	// now compose the target URI (RFC 3986 sec. 5.3)
	var result = unsplitUriRef([tScheme, tAuth, tPath, tQuery, rFrag]);
	return result;
}
