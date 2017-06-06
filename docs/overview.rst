===============================
Overview of encoded Application
===============================

This document does not contain installation or operating instructures.  See the main README_ for that.

Encoded is a python/javascript application for storing, modifying, retrieving and displaying the metadata (as JSON objects) for the ENCODE_ project.
The application was designed specifically to store metadata for high-throughput genomics experiments, but the overall architecture is suitable for any set of highly linked objects.

The "deep" backend is a simple Postgres object database.  The relational database does not store any specific information about the objects but simply tracks transactions and keys.   CRUD (Create/Read/Update/Delete) in this database is governed by a python Pyramid_ app.   This python app can stand alone and provide JSON objects via GET directly from the database.

Elasticsearch_ is used to deeply and robustly index the entire object store and provide extremely fast read access and powerful search capability.

The Browser accessible frontend is written in ReactJS_ and uses the same Pyramid_ URL dispatch as the backend, but converts the GET request JSON into XHTML for viewing in a Web Browser.

SOURCE CODE ORGANIZATION
------------------------

	*** WARNING THIS IS OUT OF DATE SINCE snovault SPLIT OFF -- REWRITE WHEN IT'S TOTALLY DIVORCED ***

	* Root - the root directory contains configuration files and install scripts along with other accessory directories
		- *bin* - command line excutables (see src/commmands) from buildout (see PyramidDocs_)
		- *develop* & *develop-eggs* - source and python eggs (created by buildout)
		- *docs* - documentation (including this file)
		- *eggs* - Python dependencies from PyPi (created by buildout)
		- *etc* - apache config and other admin files
		- *node_modules* - JS (Node) dependencies from npm (created by buildout)
		- *parts* - wsgi interfaces and ruby dependencies (gems) (created by buildout)
		- *scripts* - cron jobs

	* src directory - contains all the python and javascript code for front and backends
		- *commands* - the python source for command line scripts used for synching, indexing and other utilities independent of the main Pyramid application
		- *schemas* - JSON schemas (JSONSchema_, JSON-LD_) describing allowed types and values for all metadata objects
		- *static* - Frontend JS (components), SCSS/CSS (HTML styling), images, fonts and frontend JS libraries
		- *tests* - Unit and integration tests
		- *upgrade* - python instructions for upgrading old objects stored to the latest schema
		- *views* - business logic for dispatching URLs and producing the correct JSON

**BACKEND**
-----------
	* Application (responds to web requests) - the main config files are *.ini in the root encoded directory.

Guts
----
views
-----
	The guts of the web application are in the views package.  Views.views defines the Item and Collection classes that the web app will respond to via URLs like /{things}/ (returns a Collection of Things) and /{things}/{id} (retuns a Thing).

	Other modules in the views package correspond to non-core views that the app will respond to.
		user.py - special user objects are special
		access_key.py - generation/modification of access keys for programatic access
		search.py - constructs ES query and passes though to :9200

snovault.py
--------------
	snovault.py defines the core Collection and Item classes which are the python representation of linked JSON objects and groups (collections) of linked JSON objects.   It contains the business logic for updating JSON objects via PATCH and the recursive GETs necessary for embedded objects.

AuthZ
-----
	- *authentication.py*
	- *authorization.py*
	- *persona.py*

	* JSON data schema
		definition
			Each object type has a .json schema file in /schemas.  The objects are linked and embedded within each other by reference, forming a graph structure.   "Mixins" are sub-schemas included in more than one object type definition.  Each schema file is *versioned* and mapping an object from an older schema to a new one is called *upgrading*
		validation
			Objects are validated as they are POSTed or PATCHed to the application (via HTTP).  Not sure when/how the validation is hooked in
		upgrading
			No idea
		linked and embedded objects
			Sorcery
	* Postgres Storage
		* Loading
	* Elasticsearch & Indexing

**FRONTEND**
------------

	The pyramid app handles all URL dispatch and fetches JSON objects from Elasticsearch (or optionally, the database directly).  These can be either individual objects or Collections (arrays) of objects.  The objects can either be "flat" with no linked objects embedded, or with some or all linked objects embedded in the response.

	* renderers.py - code that determines whether to return HTML or JSON based on request, as well as code for starting the node subprocess renderer.js which converts the ReactJS pages into XHTML.

Use of NodeJS
-------------

About ReactJS
-------------

Component Pages
---------------
	HTML pages are written in Javascript using JSX_ and ReactJS_.  These files are in src/static/components.
	Each object type has a component which describes how both the individual item and the collection pages are rendered.  Other pages include home and search.  JSX_ allows the JS file itself to serve like an HTML template, similar to other web frameworks.

Boilerplate and Parent Classes
------------------------------
		* app.js
		* globals.js
		* mixins.js
		* errors.js
		* home.js
		* item.js
		* collection.js
		* fetched.js
		* edit.js
		* testing.js

User Pages (Templates)
----------------------
		* index.js
		* antibody.js
		* biosample.js
		* dataset.js
		* experiment.js
		* platform.js
		* search.js
		* target.js

Views and Sections (Templates)
------------------------------
		* dbxref.js
		* navbar.js
		* footer.js


**API**

Parameters (to be supplied in POST object or via GET url parameters):
---------------------------------------------------------------------
	* datastore=(database|elasticsearch) default: elasticsearch
	* format=json  Return JSON objects instead of XHTML from browser.
	* limit=((int)|all) return only some or all objects in a collection
	* Searching
		*


.. _Pyramid: http://www.pylonsproject.org/
.. _ENCODE: http://www.encodeproject.org/
.. _JSONSchema: http://json-schema.org/
.. _JSON-LD:  http://json-ld.org/
.. _Elasticsearch: http://www.elasticsearch.org/
.. _ReactJS: http://facebook.github.io/react/
.. _PyramidDocs: http://docs.pylonsproject.org/en/latest/
.. _JSX: http://jsx.github.io
.. _README: https://github.com/ENCODE-DCC/encoded/
