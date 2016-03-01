========================
ENCODE Metadata Database
========================

|Build status|_

.. |Build status| image:: https://travis-ci.org/ENCODE-DCC/encoded.png?branch=master
.. _Build status: https://travis-ci.org/ENCODE-DCC/encoded


Step 1: Verify that homebrew is working properly::

    $ sudo brew doctor


Step 2: Install or update dependencies::

    $ brew install libevent libmagic libxml2 libxslt openssl postgresql graphviz nginx python3 node
    $ brew install freetype libjpeg libtiff littlecms webp  # Required by Pillow
    $ brew tap homebrew/versions
    $ brew install elasticsearch17

If you need to update dependencies::

    $ brew update
    $ brew upgrade
    $ rm -rf encoded/eggs


Step 3: Run buildout::

    $ python3 bootstrap.py --buildout-version 2.4.1 --setuptools-version 18.1
    $ bin/buildout

    NOTE:  If you have issues with postgres or the python interface to it (psycogpg2) you probably need to install postgresql 
    via homebrew (as above)


Step 4: Start the application locally

In one terminal startup the database servers and nginx proxy with::

    $ bin/dev-servers development.ini --app-name app --clear --init --load

This will first clear any existing data in /tmp/encoded.
Then postgres and elasticsearch servers will be initiated within /tmp/encoded.
An nginx proxy running on port 8000 will be started.
The servers are started, and finally the test set will be loaded.

In a second terminal, run the app with::

    $ bin/pserve development.ini

Indexing will then proceed in a background thread similar to the production setup.

Browse to the interface at http://localhost:8000/.


Running tests
=============

To run specific tests locally::
    
    $ bin/test -k test_name
    
To run with a debugger::
    
    $ bin/test --pdb 

Specific tests to run locally for schema changes::

    $ bin/test -k test_load_workbook
    $ bin/test -k test_edw_sync

Run the Pyramid tests with::

    $ bin/test -m "not bdd"

Run the Browser tests with::

    $ bin/test -m bdd -v --splinter-webdriver chrome

Run the Javascript tests with::

    $ npm test

Or if you need to supply command line arguments::

    $ ./node_modules/.bin/jest


Notes on SASS/Compass
=====================

We use the `SASS <http://sass-lang.com/>`_ and `Compass <http://compass-style.org/>`_ CSS preprocessors.
The buildout installs the SASS and Compass utilities and compiles the CSS.
When changing the SCSS source files you must recompile the CSS using one of the following methods:

Compiling "on the fly"
----------------------

Compass can watch for any changes made to .scss files and instantly compile them to .css.
To start this, from the root of the project (where config.rb is) do::

    $ bin/compass watch

You can specify whether the compiled CSS is minified or not in config.rb. (Currently, it is set to minify.)

Force compiling
---------------

::

    $ bin/compass compile

Again, you can specify whether the compiled CSS is minified or not in config.rb.

Also see the `Compass Command Line Documentation <http://compass-style.org/help/tutorials/command-line/>`_ and the `Configuration Reference <http://compass-style.org/help/tutorials/configuration-reference/>`_.

And of course::

    $ bin/compass help


SublimeLinter
=============

To setup SublimeLinter with Sublime Text 3, first install the linters::

    $ easy_install-2.7 flake8
    $ npm install -g jshint
    $ npm install -g jsxhint

After first setting up `Package Control`_ (follow install and usage instructions on site), use it to install the following packages in Sublime Text 3:

    * sublimelinter
    * sublimelinter-flake8
    * sublimelinter-jsxhint
    * jsx
    * sublimelinter-jshint

.. _`Package Control`: https://sublime.wbond.net/
