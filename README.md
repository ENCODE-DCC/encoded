ENCODE Metadata Database
========================


## System Installation (OSX Catlina 10.15.2)
See [Snovault OSX System Installation][].  ENCODE installs Snovault as it is a dependency.
The System Installation is the same for both.  However, you do not need to set up a running 
Snovault instance yourself.


## Application Installation
For issues see [Snovault OSX App Installation][] first.

1. Create a virtual env in your work directory.

   This example uses the python module venv. Other options would also work, like conda or pyenv.
   Please note that older versions of `pip` may cause issues when updating the application.
   On MacOS `pip` `21.0.1` is known to work.
    ```bash
    $ cd your-work-dir
    $ python3 -m venv encoded-venv
    $ source encoded-venv/bin/activate
    $ pip install -U pip==21.0.1
    ```

2. Clone the repo and `cd` into it
    ```bash
    git clone git@github.com:ENCODE-DCC/encoded.git
    cd encoded
    ```

3. Build Application
    ```bash
    make clean && make install
    ```

    If you need to develop `snovault` side by side you can use the following commands instead, assuming `encoded` and `snovault` are present at the same level in your filesystem and virtual environment is activated.

    ```bash
    $ cd .. && pip install -e snovault
    $ cd encoded && make clean && make install
    ```

4. Run Application
    ```bash
    $ dev-servers development.ini --app-name app --clear --init --load
    # In a separate terminal, make sure you are in the encoded-venv
    $ pserve development.ini
    ```

5. Browse to the interface at http://localhost:6543

6. Run Tests
    ```bash
    # Make sure you are in the encoded-venv
    ./circle-tests.sh bdd
    ./circle-tests.sh indexing
    ./circle-tests.sh indexer
    ./circle-tests.sh not-bdd-non-indexing
    ./circle-tests.sh npm
    ```

    You can also invoke `pytest` directly if you need more granular control over which Python tests to run.

    ```bash
    # Make sure you are in your venv
    # Run a specific test in a specific file
    $ pytest TEST_FILE_PATH::TEST_NAME
    # Run tests with the given mark
    $ pytest -m $PYTEST_MARK
    ```

## Working on the Pyramid configuration
The Pyramid INI files are templated out using [Jsonnet](https://jsonnet.org/). To update
these configurations, install the `jsonnet` executable with `brew install jsonnet`.
Running `make config` will generate the new configuration and format the jsonnet files,
make sure to run this before pushing or CircleCI will fail.

The Jsonnet files and generated config are located in `conf/pyramid/`. The file
[sections.libsonnet](conf/pyramid/sections.libsonnet) is a library of functions that
each returns a representation of a single section of an INI file. The file
[config.jsonnet](conf/pyramid/config.jsonnet) assembles these sections and outputs a
concrete INI file.

## Configuration Installation (In Progress)
    The configuration repo is set by 'conf_dir = ./cloud-config' in the 'demo-config.ini' file.  The
    'deploy.py' compiles yaml files from 'cloud-config' for use with aws instances.  There is a
    very specific file structure at the moment.  We are working to generalize the use case.

    To use a different directory for cloud configuration copy 'demo-config.ini' to '.dev-config.ini'.
    Then change the 'conf_dir=../your-conf-repo/cloud-config' in the hidden file to your 
    configuration directory.

    'deploy.py' uses configuration in 'demo-config.ini:deployment' section.  Those are overwritten
    by '.dev-config.ini:deployment' if it exists.  Currently command line arguments will be
    overwritten by the ini files.  Eventaully that may be swtiched so the command line arguments
    overwrite ini files.

    For temporary backwards compatibility the default config repo is set to this repos cloud-config.
    Eventually, the demo-config.ini will default to a demonstration configuration


[Snovault OSX System Installation]: https://github.com/ENCODE-DCC/snovault/blob/dev/README.rst#system-installation-osx-catlina-10152
[Snovault OSX App Installation]: https://github.com/ENCODE-DCC/snovault/blob/dev/README.rst#application-installation
