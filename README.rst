========================
ENCODE Metadata Database
========================

|Build status|_

.. |Build status| image:: https://travis-ci.org/ENCODE-DCC/encoded.png?branch=master
.. _Build status: https://travis-ci.org/ENCODE-DCC/encoded


Step 1: Verify that homebrew is working properly::

    $ brew doctor


Step 2: Install or update dependencies::

    $ brew install libevent libmagic libxml2 libxslt elasticsearch openssl postgresql graphviz
    $ brew install freetype libjpeg libtiff littlecms webp  # Required by Pillow

Note: For Mac < 10.9, the system python doesn't work. You should install Python with Homebrew::

    $ brew install python3

Install Node 0.10 from homebrew/versions::

    $ brew tap homebrew/versions
    $ brew install node010

If you need to update dependencies::

    $ brew update
    $ brew upgrade
    $ rm -rf encoded/eggs


Step 3: Run buildout::

    $ python3.4 bootstrap.py -v 2.3.1 --setuptools-version 15.2
    $ bin/buildout

If you see a clang error like this::

    clang: error: unknown argument: '-mno-fused-madd' [-Wunused-command-line-argument-hard-error-in-future]

You can try::

    $ ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future bin/buildout

If it does not exist, set a session key::

    $ cat /dev/urandom | head -c 256 | base64 > session-secret.b64

Step 4: Start the application locally

In one terminal startup the database servers with::

    $ bin/dev-servers development.ini --app-name app --clear --init --load

This will first clear any existing data in /tmp/encoded.
Then postgres and elasticsearch servers will be initiated within /tmp/encoded.
The servers are started, and finally the test set will be loaded.

In a second terminal, run the app in with::

    $ bin/pserve development.ini

Indexing will then proceed in a background thread similar to the production setup.

Browse to the interface at http://localhost:6543/.

Step 5: Tests

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

    $ bin/test -m bdd -v -v

Run the Javascript tests with::

    $ npm test

Or if you need to supply command line arguments::

    $ ./node_modules/.bin/jest

Step 6: Database modifications

If you wish a clean db wipe for DEVELOPMENT::
    
    $ dropdb encoded
    ...
    $ createdb encoded
    $ pg_ctl -D /usr/local/var/postgres -l pg.log start

Database setup on VMs::

    # service postgresql-9.3 initdb
    # service postgresql-9.3 start
    # sudo -u postgres createuser --createdb encoded

Then as the encoded user::

    $ createdb encoded

To dump a postgres database:
    pg_dump -Fc encoded > FILE_NAME  (as user encoded on demo vm)
    (FILE_NAME for production is ~/encoded/archive/encoded-YYYYMMDD.dump)

To restore a postgres database:
    pg_restore -d encoded FILE_NAME (as user encoded on demo vm)

Create ElasticSearch mapping for ENCODE data::

    $ bin/create-mapping production.ini

Notes on SASS/Compass
=====================

`SASS <http://sass-lang.com/>`_ and `Compass <http://compass-style.org/>`_ are being used. Before running to app, you need to builld the css files by starting 'compass watch' or doing a 'compass compile' (see below).

Installing
----------

Both can be installed via Ruby gems::

    $ gem install sass
    $ gem install compass

Compiling "on the fly"
----------------------

Compass can watch for any changes made to .scss files and instantly compile them to .css. To start this, from the root of the project (where config.rb is) do::

    $ compass watch

You can specify whether the compiled CSS is minified or not in config.rb. (Currently, it is set to minify.)

Force compiling
---------------

::

    $ compass compile

Again, you can specify whether the compiled CSS is minified or not in config.rb.

Also see the `Compass Command Line Documentation <http://compass-style.org/help/tutorials/command-line/>`_ and the `Configuration Reference <http://compass-style.org/help/tutorials/configuration-reference/>`_.

And of course::

    $ compass help


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
