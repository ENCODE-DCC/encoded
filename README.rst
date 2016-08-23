========================
ENCODE Metadata Database
========================

|Build status|_

.. |Build status| image:: https://travis-ci.org/ENCODE-DCC/encoded.png?branch=master
.. _Build status: https://travis-ci.org/ENCODE-DCC/encoded


Step 1: Verify that homebrew is working properly::

    $ sudo brew doctor


Step 2: Install or update dependencies::

    $ brew install libevent libmagic libxml2 libxslt openssl postgresql graphviz nginx python3
    $ brew install freetype libjpeg libtiff littlecms webp  # Required by Pillow
    $ brew tap homebrew/versions
    $ brew install elasticsearch17 node4-lts

If you need to update dependencies::

    $ brew update
    $ brew upgrade
    $ rm -rf encoded/eggs


Step 3: Run buildout::

    $ python3 bootstrap.py --buildout-version 2.4.1 --setuptools-version 18.5
    $ bin/buildout

    NOTE:  
    If you have issues with postgres or the python interface to it (psycogpg2) you probably need to install postgresql 
    via homebrew (as above)
    If you have issues with Pillow you may need to install new xcode command line tools:
    - First update Xcode from AppStore (reboot)
    $ xcode-select --install 
    


If you wish to completely rebuild the application, or have updated dependencies:
    $ make clean

    Then goto Step 3.

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


Building Javascript and CSS
===========================

Our Javascript is written using ES6 and JSX, so needs to be compiled using babel and webpack. Our
CSS is written in the SCSS variant of `Sass <http://sass-lang.com/>`_ and also needs compilation
using webpack.

To build production-ready bundles, do::

    $ npm run build

(This is also done as part of running buildout.)

To build development bundles and continue updating them as you edit source files, run::

    $ npm run dev

The development bundles are not minified, to speed up building. The above command runs continually
in your terminal window and watches for changes in Javascript and SCSS files, rebuilding the
bundles as you make changes.


SublimeLinter
=============

To setup SublimeLinter with Sublime Text 3, first install the linters::

    $ easy_install-2.7 flake8
    $ npm install -g eslint
    $ npm install -g eslint-plugin-react

After first setting up `Package Control`_ (follow install and usage instructions on site), use it to install the following packages in Sublime Text 3:

    * sublimelinter
    * sublimelinter-flake8
    * SublimeLinter-contrib-eslint (`instructions <https://github.com/roadhump/SublimeLinter-eslint#plugin-installation>`_)
    * babel (`instructions <https://github.com/babel/babel-sublime#setting-as-the-default-syntax>`_)

.. _`Package Control`: https://sublime.wbond.net/
