ENCODE Metadata Database
========================


## System Installation (OSX Catlina 10.15.2)
See [Snovault OSX System Installation][].  ENCODE installs Snovault as it is a dependency.
The System Installation is the same for both.  However, you do not need to set up a running 
Snovault instance yourself.


## Application Installation
For issues see [Snovault OSX App Installation][] first.

1. Create a virtual env in your work directory.
    This example uses the python module venv. Other options would also work, like conda or pyenv
    ```
    $ cd your-work-dir
    $ python3 -m venv encoded-venv
    $ source encoded-venv/bin/activate
    ```

1. Clone the repo and install requirements
    ```
    # Make sure you are in the encoded-venv
    $ cd encoded
    $ pip install -r requirements.osx.txt
    ```

1. Build Application
    ```
    $ make clean && buildout bootstrap && bin/buildout
    ```

1. Run Application
    ```
    $ bin/dev-servers development.ini --app-name app --clear --init --load
    # In a separate terminal, make sure you are in the encoded-venv
    $ bin/pserve development.ini
    ```

1. Browse to the interface at http://localhost:6543

1. Run Tests
    ```
    # Make sure you are in the encoded-venv
    $ ./circle-tests.sh bdd
    $ ./circle-tests.sh indexing
    $ ./circle-tests.sh indexer
    $ ./circle-tests.sh not-bdd-non-indexing
    $ ./circle-tests.sh npm
    ```


[Snovault OSX System Installation]: https://github.com/ENCODE-DCC/snovault/blob/master/README.md#system-installation-osx-catlina-10152
[Snovault OSX App Installation]: https://github.com/ENCODE-DCC/snovault/blob/master/README.md#application-installation
