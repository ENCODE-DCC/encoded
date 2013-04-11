========================
ENCODE Metadata Database
========================

|Build status|_

.. |Build status| image:: https://travis-ci.org/ENCODE-DCC/encoded.png?branch=master
.. _Build status: https://travis-ci.org/ENCODE-DCC/encoded


*Note: the default Mac python doesn't seem to work. You might want to install Python with Homebrew and you may need to sintall one of more of (using homebrew): libxml2 libxslt freetype openssl libjpeg.*

First run buildout::

    $ python2.7 bootstrap.py
    $ bin/buildout

To start the application::

    $ bin/pserve development.ini

Browse to the interface at http://localhost:6543/.

Run the Jasmine tests at http://localhost:6543/tests/js/test_runner.html.

Run the Pyramid tests with::

    $ bin/test -k -bdd

Run the Browser tests with::

    $ bin/test -k bdd -v -v

To run tests with postgresql::

    $ initdb encoded
    $ bin/test --engine-url postgresql:///encoded


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
