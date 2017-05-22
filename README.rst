========================
ENCODE Metadata Database
========================

|Build status|_

.. |Build status| image:: https://travis-ci.org/ENCODE-DCC/encoded.png?branch=master
.. _Build status: https://travis-ci.org/ENCODE-DCC/encoded

Step 0: (Mac) Verify that homebrew is working properly::

    $ sudo brew doctor


Step 1: Encoded requires a UNIX based system (Mac or Linux) and Python 3.4.x or 3.5.x::

    For a mac, follow steps 0/1/2/3.  For Linux use apt-get or yum as your Linux flavor demands.  You can consult
    cloud-config.yml for other steps.
    Note:  Python 3.6 is NOT compatible with this version of encoded but 3.5.x works on OS X.
    Production is currently 3.4 so these notes suggest that installation
    Linux: apt-get install python3.4-dev or equivalent
    
    Mac OSX install instructions
    If you already have a python3 from homebrew:
    $ brew uninstall --force python3
    
 
    $ brew install pyenv
    $ pyenv install 3.4.3
    $ pyenv global 3.4.3
    $ ln -sf /Users/${USER}/.pyenv/shims/python3 /usr/local/bin/python3
    
Step 2: (Mac) Install or update dependencies::

    $ brew install libevent libmagic libxml2 libxslt openssl postgresql graphviz nginx python3
    $ brew install freetype libjpeg libtiff littlecms webp chromedriver # Required by Pillow
    $ brew install node@6
    $ brew tap garrow/homebrew-elasticsearch17
    $ brew install elasticsearch@1.7
    
    # for Mac OSX Sierra
    $ brew cask install Caskroom/cask/xquartz
    $ xcode-select --install

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
    $ bin/test -k test_load_schema

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

Creating a demo machine
========================

After buildout you (if you have the correct permissions) can run for a single-node "cluster":

    $ bin/deploy --instance-type c4.8xlarge

To initiate a server in the AWS cloud with the current branch, and with a computed nameserver alias based on the branch and AWS username.  Note that this retrieves a Postgres database from the current backup, so "as is" only applies specifically to the ENCODE Project (forkers beware!).   There are options to use a different branch and/or different name and also AWS spotinstnaces.  

      $ bin/deploy --help 
      
For all options, including setting up ES clusters (needed for full production).  After indexing (currently 8+hrs) the machine can be downsized at AWS to an m4.2xlarge, unless you are planning to submit significant data to it.

Linting your code within your code editor
=========================================

To set up linting with Sublime Text 3 or Visual Studio Code, first install the linters::

    $ easy_install-2.7 flake8
    $ npm install -g eslint
    $ npm install -g eslint-plugin-react

Sublime Text 3
--------------
After first setting up `Package Control`_ (follow install and usage instructions on site), use it to install the following packages in Sublime Text 3:

    * sublimelinter
    * sublimelinter-flake8
    * SublimeLinter-contrib-eslint (`instructions <https://github.com/roadhump/SublimeLinter-eslint#plugin-installation>`_)
    * babel (`instructions <https://github.com/babel/babel-sublime#setting-as-the-default-syntax>`_)

.. _`Package Control`: https://sublime.wbond.net/

Visual Studio Code
------------------
Go to the Visual Studio Code marketplace and install these extensions:

    * ESLint
    * Python
    * Sass
