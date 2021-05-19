Lattice Metadata Database
========================


## System Installation (OSX Catlina 10.15.2)
See [Snovault OSX System Installation][].  Lattice installs Snovault as it is a dependency.
The System Installation is the same for both.  However, you do not need to set up a running 
Snovault instance yourself.


## Application Installation
For issues see [Snovault OSX App Installation][] first.

1. Create a virtual environment. This example uses anaconda. Other options would also work, like venv or pyenv
    ```
    conda create --name lattice python=3.7
    ```
    You will need to be in this environment for the following instructions
    ```
    conda activate lattice
    ```

1. Clone the repo and install requirements
    ```
    git clone https://github.com/Lattice-Data/encoded.git
    ```
    ```
    cd encoded
    ```
    ```
    pip install -r requirements.osx.txt
    ```

1. Build Application
    ```
    make clean && buildout bootstrap && bin/buildout
    ```

1. Run Application
    ```
    bin/dev-servers development.ini --app-name app --clear --init --load
    ```
    In a separate terminal, make sure you are in the encoded directory and activate the lattice environment
    ```
    bin/pserve development.ini
    ```
    If working on static files
    ```
    npm run dev
    ```

1. Browse to the interface at http://localhost:6543

1. Run Tests (no argument runs indexing and non-indexing non bdd tests)
    ```
    ./circle-tests.sh bdd
    ```
    ```
    ./circle-tests.sh not-bdd-indexing
    ```
    ```
    ./circle-tests.sh not-bdd-non-indexing
    ```
    ```
    ./circle-tests.sh npm
    ```
    ```
    ./circle-tests.sh
    ```


[Snovault OSX System Installation]: https://github.com/ENCODE-DCC/snovault/blob/master/README.md#system-installation-osx-catlina-10152
[Snovault OSX App Installation]: https://github.com/ENCODE-DCC/snovault/blob/master/README.md#application-installation
