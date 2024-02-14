ENCODE Metadata Database
========================


## Running the application locally using Docker

### Install

1. Download and install [Docker](https://docs.docker.com/get-docker/).

2. Start Docker

3. Open Docker preferences, find the `Advanced` tab under `Resources`. Make sure the engine has at least 8GB of memory.

### Build

All the following commands should be run in the root of this repository.

1. Clean up possible previous build artifacts.
```bash
$ make clean
````

2. Build the docker image (first time you run this it will take up to 15 minutes):
```bash
$ docker build -t encoded-devcontainer:latest -f .devcontainer/Dockerfile .
```
3. Start the container with the appropriate ports forwarded, and this directory mounted on `/workspaces/encoded` in the container.
```bash
$ docker run --rm -it -p 6378:6378 -p 6543:6543 -p 8000:8000 -p 9201:9201 -v $(pwd):/workspaces/encoded --workdir /workspaces/encoded --name encode-container encoded-devcontainer:latest bash
```

4. In the shell that opens within the container you started in step 3. run the following commands:
```bash
$ make devcontainer
$ dev-servers development.ini --app-name app --clear --init --load
```

5. In other terminal open a shell in the running container:
```bash
$ docker exec -it encode-container bash
```

6. In the shell that you opened in step 5. run:
```bash
$ pserve development.ini
```

7. Browse the app at `localhost:6543`

8. Closing both terminals will cause the container to exit. You do not need to do anything else to stop the app.


## Running the application in Github Codespaces

1. In this repository, click the green **Code** button, choose the **Codespaces** tab and then click the **...** to create a new Codespace.

2. In the options you can choose the branch (you can also check out your branch later), and the machine size (the second smallest with 4 cores and 8GB of memory is enough).

3. Click **Create** **codespace**

4. Building the image (and specifically the `npm ci` command) will take about 15 minutes. 

5. Once the build completes you will be take to a VSCode editor running in your browser. Wait for the `postCreateCommand` to finish.

6. Choose the branch you want to run the app from (if you did not do it in the step 2.)

7. In the terminal run `dev-servers development.ini --app-name app --clear --init --load`

8. Open a new terminal tab (the button with a **+** -symbol).

9. Run `pserve development.ini`.

10. You can now browse the app via the pop-up, or the address shown next to the `pserve(6543)` **Local** **Address** column in **ports** tab above the terminal window.

## Deploying an AWS demo

Building the application is not necessary to deploy a demo. All you need is a python virtual environment with `boto3` package installed.
In the root of this repository run:
```bash
$ python src/encoded/commands/deploy.py <options>
```


## System Installation (Deprecated method, using Docker or Codespaces recommended)
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


[Snovault OSX System Installation]: https://github.com/ENCODE-DCC/snovault/blob/dev/README.rst#system-installation-osx-catlina-10152
[Snovault OSX App Installation]: https://github.com/ENCODE-DCC/snovault/blob/dev/README.rst#application-installation
