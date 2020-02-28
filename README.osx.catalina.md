ENCODE Metadata Database
========================


## System Installation (OSX Catlina 10.15.2)
See [Snovault OSX System Installation][].  Snovault is a dependecy of the Encoded application.
Installing Snovault is not a requirement to run the this application, however, the
system installation is the same.


## Application Installation
For issues see [Snovault OSX App Installation][] first.

1. Create a virtual env in your work directory.
    Here we use python3 venv module.  Use venv, like conda, if you please
    ```
    $ cd your-work-dir
    $ python3 -m venv encoded-venv
    $ source encoded-venv/bin/activate
    ```

1. Clone the repo and install requirements
    ```
    $ cd encoded
    # Make sure you are in the encoded-venv
    $ pip install -r requirements.osx.catalina.txt
    ```

1. Build Application
    ```
    # Make sure you are in the encoded-venv
    $ make clean && buildout bootstrap && bin/buildout
    ```

1. Run Application
    ```
    # Make sure you are in the encoded-venv
    $ bin/dev-servers development.ini --app-name app --clear --init --load
    # In a separate terminal, make sure you are in the encoded-venv
    $ bin/pserve development.ini
    ```

1. Browse to the interface at http://localhost:6543

1. Run Tests
    * no argument runs indexing and non-indexing non bdd tests
    ```
    # Make sure you are in the encoded-venv
    $ ./circle-tests.sh bdd
    $ ./circle-tests.sh not-bdd-indexing
    $ ./circle-tests.sh not-bdd-non-indexing
    $ ./circle-tests.sh npm
    $ ./circle-tests.sh
    ```


[Snovault OSX System Installation]: https://github.com/ENCODE-DCC/snovault/blob/master/README.osx.catalina.md#system-installation-osx-catlina-10152
[Snovault OSX App Installation]: https://github.com/ENCODE-DCC/snovault/blob/master/README.osx.catalina.md#application-installation
