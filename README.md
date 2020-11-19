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

2. Clone the repo and `cd` into it
    ```
    $ git clone git@github.com:ENCODE-DCC/encoded.git
    $ cd encoded
    ```

3. Build Application
    ```
    $ make clean && pip install -e '.[dev]' && buildout
    ```

If you need to develop `snovault` side by side you can use the following commands instead, assuming `encoded` and `snovault` are present at the same level in your filesystem.
    ```
    $ cd .. && pip install -e snovault
    $ cd encoded && make clean && pip install -e '.[dev]' && buildout
    ```

4. Run Application
    ```
    $ dev-servers development.ini --app-name app --clear --init --load
    # In a separate terminal, make sure you are in the encoded-venv
    $ pserve development.ini
    ```

5. Browse to the interface at http://localhost:6543

6. Run Tests
    ```
    # Make sure you are in the encoded-venv
    $ ./circle-tests.sh bdd
    $ ./circle-tests.sh indexing
    $ ./circle-tests.sh indexer
    $ ./circle-tests.sh not-bdd-non-indexing
    $ ./circle-tests.sh npm
    ```

You can also invoke `pytest` directly if you need more granular control over which Python tests to run.
    ```bash
    # Make sure you are in your venv
    # Run a specific test in a specific file
    $ pytest TEST_FILE_PATH::TEST_NAME
    # Run tests with a name matching the expression
    $ pytest -k $EXPRESSION
    # Run tests with the given mark
    $ pytest -m $PYTEST_MARK
    ```

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


[Snovault OSX System Installation]: https://github.com/ENCODE-DCC/snovault/blob/master/README.md#system-installation-osx-catlina-10152
[Snovault OSX App Installation]: https://github.com/ENCODE-DCC/snovault/blob/master/README.md#application-installation
