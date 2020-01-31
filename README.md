# ENCODE Metadata Database
-------------------------------------------------------


[![CircleCI](https://circleci.com/gh/ENCODE-DCC/encoded/tree/dev.svg?style=svg)](https://circleci.com/gh/ENCODE-DCC/encoded/tree/dev)

## Setting Up Your Environment

These are the primary software versions used in production, but many of them are out of date for local Mac installs:
- Python 3.4.3 (no longer works on OSX 10.15.x "Catalina")
- Node 10
- Elasticsearch 5.x (debian stable)
- Java VM 11 (also works on 1.8)
- Ubuntu 14.04

### **0. Xcode for Mac OS build tools**  
- Install [Xcode](https://developer.apple.com/xcode/) from the website or Mac App store because the local build will use some of Xcode's compilation tools.
- Install the Xcode commandline tools (the commandline tools may need to be reinstalled after OS and Xcode updates)
  - `xcode-select --install` 

>:star: _Note_: You will need to open Xcode to accept the end-user agreement from the application, or from the commandline run:_  
>- `sudo xcodebuild -license accept`


### **1. Homebrew for Mac OS package management**  
- Verify that [Homebrew](https://brew.sh/) is installed and working properly:  
  - `brew doctor`


### **2. (Mac) Install or update other dependencies:**

#### **2.1 Low level dependencies: (tested on 10.15 Catalina)**

```bash
brew install libevent libmagic libxml2 libxslt openssl graphviz nginx
brew install freetype libjpeg libtiff littlecms webp libyaml zlib
```
#### **2.2 Higher level dependencies (tested on 10.15 Catalina) **
```bash
brew install postgresql@11 
brew tap homebrew/cask-versions
brew cask install chromedriver (can also get from https://chromedriver.chromium.org/downloads)
brew cask install adoptopenjdk/openjdk/adoptopenjdk8
brew cask install java8
brew install elasticsearch@5.6
```
>:warning: _Note_: In most cases with brew options you will need to export the correct versions in your path as instructed by homebrew; e.g.:
`  echo 'export PATH="/usr/local/opt/elasticsearch@5.6/bin:$PATH"' >> ~/.bash_profile `

>:star: _Note_: Note you must be pretty careful with prior installs of Elasticsearch as they share config directories.

>:star: _Note_: This additional step is required for new macOS Sierra installations
>- `brew cask install Caskroom/cask/xquartz`

>:star: _Note_: **Node version mangement with nvm**: If you need to easily switch between **node** versions you may wish to use [nvm](https://github.com/creationix/nvm) instead (not required for most users)
>- `npm install -g nvm`
>- `nvm install 10`
>- `nvm use 10`
>
>:star: _Note_: **Node version mangement with n**: 
>- `brew install n (node version manager)`
>- `n 10.14.0 (set node version to 10.14.0)`
>- `node --version`

>:warning: _Note_: If you need to update Python dependencies (do not do this randomly as you may lose important brew versions of packages you need):
>- `rm -rf encoded/eggs` (then re-run buildout below)
> and possibly
>- `brew update`
>- `brew upgrade`


### **3. Python**  
Encoded requires a UNIX based system (Mac or Linux) and **Python 3.4.3 or 3.5.x** :
>:warning: _Note_: Mac OS X 10.15.x Catalina does not work well with 3.4, we recommend 3.5.x

 - For local development on a Mac, follow the steps below.  For Linux SEE NEW README

- _Note_: Production is currently using Python 3.4.3!
- Linux: apt-get install python3.4-dev or equivalent
    
**Mac OSX Python install instructions**  

The Python version management tool `pyenv` is very useful. 

>:warning: _Note: If you have previously installed python3 from homebrew, you may possibly wish to uninstall it (not required):_  
> - `brew uninstall --force python3`


    
**Install `pyenv` and set the default versions:**
```bash 
brew install pyenv
pyenv install 3.4.3 // or pyenv install 3.5.9
pyenv install 2.7.13
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
echo 'eval "pyenv shell 2.7.13 3.4.3"' >> ~/.bash_profile  // or echo 'eval "pyenv shell 2.7.13 3.5.9"' >> ~/.bash_profile
. ~/.bash_profile
```

>:star: _Note: Migrating `pyenv` Python packages_  
>
>_If you have previously installed a Python version from `pyenv`, and want to quickly migrate all your pypi packages to a new version (Python 2 to 2, and Python 3 to 3 only):_
>  - `brew install pyenv-pip-migrate`  
>    
>Example if you previously installed `2.7` which really is _`2.7.0`_:  
>  - `pyenv install 2.7.13`  
>  - `pyenv migrate 2.7 2.7.13`

>:star: _Note: `pyenv` install fails with "ERROR: The Python ssl extension was not compiled. Missing the OpenSSL lib?" for MAC OS High Sierra
>
>Uninstall and re-install openssl using the following command when you install pyenv
>- `brew uninstall --ignore-dependencies openssl && brew install openssl && CFLAGS="-I$(brew --prefix openssl)/include" LDFLAGS="-L$(brew --prefix openssl)/lib" pyenv install <VERSION>`

**Set the correct Python for the current directory:**
```bash
pyenv local 3.4.3 // or pyenv local 3.5.9
```

#### **3.1 Mac OSX 10.15 Catalina issues:**
see: (https://holgr.com/python-3-in-macos-catalina-fixing-the-abort-trap/):
```bash
ln -s /usr/local/Cellar/openssl@1.1/1.1.1d/lib/libcrypto.dylib /usr/local/lib/libcrypto.dylib
ln -s /usr/local/Cellar/openssl@1.1/1.1.1d/lib/libssl.dylib /usr/local/lib/libssl.dylib
```

### **4. Run buildout: in git cloned directory**

- `pip3 install -U zc.buildout setuptools`
- `pyenv rehash`
- `buildout bootstrap`
- `bin/buildout`

> :star: _Note_: If you have issues with postgres or the python interface to it (psycogpg2) you probably need to install postgresql via homebrew (as above)  

>:star: _Note_: If you have issues with Pillow you may need to install new xcode command line tools:
> Update or Install [Xcode](https://developer.apple.com/xcode/) from the Mac AppStore (reboot may be required) and re-run:  
> - `xcode-select --install`  


>:star: _Note_: **Clean ALL the Things!** If you wish to **completely rebuild** the application or **cleanly reload** dependencies (:warning: long re-build time!):  
>- `make clean && buildout bootstrap && bin/buildout`


### **5. Start the application locally**


- **Terminal window 1**:  
  In one terminal window startup the database servers and nginx proxy with:

  - `bin/dev-servers development.ini --app-name app --clear --init --load`

  This will first clear any existing data in `/tmp/encoded`.
  Then postgres and elasticsearch servers will be initiated within `/tmp/encoded`.
  An nginx proxy running on port 8000 will be started.
  The servers are started, and finally the test set will be loaded.

- **Terminal window 2**:  
  In a second terminal, run the app with:

  - `bin/pserve development.ini`

Indexing will then proceed in a background thread similar to the production setup.

>:star: _Note_: If you run into a java stack trace when you run the app, it is worth checking if /usr/local/etc/elasticsearch/elasticsearch.yml *might* have the line: ‘path.plugins: /usr/local/var/lib/elasticsearch/plugins’. If it does, it needs to be commented out.

### **6. :tada: Check out the app! :tada:**
- Browse to the interface at http://localhost:8000/.


## Running tests

- To run specific tests locally:
    
  `bin/test -k test_name`
    
- To run with a debugger:
    
  `bin/test --pdb`

- Specific tests to run locally for schema changes:

  `bin/test -k test_load_workbook`  
  `bin/test -k test_load_schema`

- Run the Pyramid tests with:

  `bin/test -m "not bdd"`

- Run the Browser tests with:

  `bin/test -m bdd -v --splinter-webdriver chrome`

- Run the Javascript tests with:

  `npm test`

- Or if you need to supply command line arguments:

  `./node_modules/.bin/jest`

> :star: _Note_: homebrew elasticsearch@5.6 on Mac OSX 10.15 (Catalina) seems to (sometimes) require 4g of RAM; edit the HEAP section of /usr/local/etc/elasticsearch/jvm.options with:
> -Xms4g
> -Xmx4g


- **Test ALL the things!**
  
  `bin/test -v -v --splinter-webdriver chrome && npm test`


## Building Javascript and CSS


Our Javascript is written using ES6 and JSX, so needs to be compiled using babel and webpack. Our CSS is written in the SCSS variant of [Sass](http://sass-lang.com/) and also needs compilation using webpack.

- To re-build **production-ready** bundles, do:

  `npm run build`

  (This is also done as part of running buildout.)

- To build **development** bundles and continue updating them as you edit source files, run:

  `npm run dev`

The development bundles are not minified, to speed up building. The above command runs continually in your terminal window and watches for changes in Javascript and SCSS files, rebuilding the bundles as you make changes.

## Creating a demo machine


- After buildout you (if you have the correct permissions) can run for a single-node "cluster":

  `bin/deploy`
  
  
- The script above will spin up a server in the AWS cloud with the current branch, and with a computed nameserver alias based on the branch and your username.  Note that this retrieves a Postgres database from the current backup, so "as is" applies specifically to the ENCODE Project (_if you have forked the repo you will not have permission to retrieve the db_).   There are options to use a different branch and/or different instance name and also if you want to use AWS spot instances...and you can specify which AWS profile you want to use.   

  
- Deploy script help (how to specify name, instance size, etc):

  `bin/deploy --help`
      
For all options, including setting up ES clusters (needed for full production).  After indexing (currently 8+hrs) the machine can be downsized at AWS to an m4.2xlarge, unless you are planning to submit significant data to it.


## Linting your code within your code editor

To set up linting with [Sublime Text 3](https://www.sublimetext.com/3) or [Visual Studio Code](https://code.visualstudio.com/), first install the linters:

```bash
pip3 install flake8
npm install -g eslint
npm install -g eslint-plugin-react
```
>:warning: _Note_: You don't have to use Sublime Text 3 but you *must* insure that linting in your editor behaves as it does in Sublime Text 3.



### Sublime Text 3

After first setting up [Package Control](https://packagecontrol.io/) (follow install and usage instructions on site), use it to install the following linting packages in Sublime Text 3:

 - `sublimelinter`
 - `sublimelinter-flake8`
 - `SublimeLinter-contrib-eslint` ([Sublime linter eslint instructions](https://github.com/roadhump/SublimeLinter-eslint#plugin-installation))
 - `babel` ([Babel instructions](https://github.com/babel/babel-sublime#setting-as-the-default-syntax))

**Sublime Linting with `pyenv`**   
To get Sublime to lint Python code using `pyenv` you must add the python version and paths and python_paths to your Sublime Linter Preferences. In **Sublime Text**, navigate to the user linter preferences:  

- Sublime Preferences  -> Package Settings -> Sublime Linter -> Settings-User

- Add the following (modify existing preference settings file or add this entire JSON object below if the file is blank):

```json
{
    "user": {
        "@python": 3.4,
        
        "paths": {
            "linux": [],
            "osx": [
                "/Users/YOURUSERNAME/.pyenv/versions/3.4.3/bin/",
                "/Users/YOURUSERNAME/.pyenv/versions/2.7/bin/"
            ],
            "windows": []
        },
        "python_paths": {
            "linux": [],
            "osx": [
                "/Users/YOURUSERNAME/.pyenv/versions/3.4.3/bin/python3",
                "/Users/YOURUSERNAME/.pyenv/versions/2.7/bin/python"
            ],
            "windows": []
        }
    }
}
```

 - Restart Sublime

### Visual Studio Code

Go to the Visual Studio Code marketplace and install these extensions:

 - ESLint
 - Python
 - Sass



## Check versions and linting

**Versions**

- `python3 --version` _returns `Python 3.4.3` (or variant like  3.4.x, or 3.5)_
- `node --version`  _returns `v10.15.0`  (or variant like  v10.x.y)_
- `elasticsearch -v` _returns `Version: 5.6.16` (or variant like  Version: 5.6.x)_
- `postgres --version` _returns `postgres (PostgreSQL) 11.6` (or variant like 11.x.y, 9.3 is also supported)_ 


**Linting check**

- **Python**: Open Sublime, make a change to a Python file, make an intentional syntax error (no `:` at the end an `if` evaluation). Warnings and errors should show on the left side of the line.    
  
  
- **JavaScript**: Make a syntax error, or style error, in a JS file. Warnings and errors should show on the left side of the line.  

