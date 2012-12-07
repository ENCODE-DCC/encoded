========================
ENCODE Metadata Database
========================

To run the front end:

    $ cd src/encoded
    $ python -m SimpleHTTPServer 8080

Browse to the interface at http://localhost:8080/.

Run the Jasmine tests at http://localhost:8080/test_runner.html.


Notes on SASS/Compass
---------------------------------
`SASS <http://sass-lang.com/>`_ and `Compass <http://compass-style.org/>`_ are being used.

**Installing**

Both can be installed via Ruby gems:

    $ gem install sass

    $ gem install compass

**Compiling "on the fly"**

Compass can watch for any changes made to .scss files and instantly compile them to .css. To start this, from the root of the project (where config.rb is) do:

    $ compass watch
    
You can specify whether the compiled CSS is minified or not in config.rb. (Currently, it is set to minify.)

**Force compiling**

    $ compass compile

Again, you can specify whether the compiled CSS is minified or not in config.rb.

Also see the `Compass Command Line Documentation <http://compass-style.org/help/tutorials/command-line/>`_ and the `Configuration Reference <http://compass-style.org/help/tutorials/configuration-reference/>`_.

And of course:

    $ compass help