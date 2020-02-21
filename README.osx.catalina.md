ENCODE Metadata Database
========================


## System Installation (OSX Catlina 10.15.2)
See System Installation in [Snovault](https://github.com/ENCODE-DCC/snovault/README.osx.catalina.rst)


## Application Installation
For issues see [Snovault](https://github.com/ENCODE-DCC/snovault/README.osx.catalina.rst) Appplication Install first.

1. Create a virtual env in your work directory
    ```
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    ```

1. Checkout repo and install requirements
    ```
    $ git clone https://github.com/ENCODE-DCC/snovault.git
    $ cd encoded
    $ pip install -r requirements.osx.catalina.txt
    ```

1. Build Application
    ```
    $ make clean && buildout bootstrap && bin/buildout
    ```

1. Run Application
    ```
    $ bin/dev-servers development.ini --app-name app --clear --init --load
    # In a separate terminal
    $ bin/pserve development.ini
    ```

1. Browse to the interface at http://localhost:6543

1. Run Tests
    * no argument runs indexing and non-indexing non bdd tests
    ```
    $ ./circle-tests.sh bdd
    $ ./circle-tests.sh not-bdd-indexing
    $ ./circle-tests.sh not-bdd-non-indexing
    $ ./circle-tests.sh npm
    $ ./circle-tests.sh
    ```
