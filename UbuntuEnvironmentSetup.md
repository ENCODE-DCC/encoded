# Setting up pandisease environment under Ubuntu system 

## Environment needed

These are the primary software versions used in production, and you should be able to use them locally:
- Python 3.4.3
- Node 10
- Elasticsearch 5.4 
- Java VM 1.8
- Ubuntu 14.04


### **1. Install Ubuntu system**
- Install [Ubuntu14.04LTS(Trusty Tahr)](http://releases.ubuntu.com/14.04/) from the website under [VirtualBox](https://www.virtualbox.org/), make sure you leave 20-40GB for the VM system.
  
### **2. Set proxy (Optional)**
If you are working behind a proxy, you need to set the proxy in .conf file. Set proxy in terminal with the following commands, then restart VM to make it work.
```bash
sudo vi /etc/profile.d/proxy.sh
export http_proxy=http://myproxy.server:port
export https_proxy=http://myproxy.server:port
sudo vi /etc/apt/apt.conf.d/proxy.conf
Acquire::http::Proxy "http_proxy=http://myproxy.server:port";
Acquire::https::Proxy "http_proxy=http://myproxy.server:port";
```

### **3.Install and update dependencies:**
```bash
sudo apt-get install apt-transport-https software-properties-common
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list
curl -sSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo apt-key add -
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get update
```
>:stop_sign: _Note_: ```
sudo add-apt-repository -y ppa:openjdk-r/ppa``` might not work:, run
```bash
sudo apt-get install --reinstall ca-certificates
``` 
If doesn't work then run
```bash
sudo -E add-apt-repository -y ppa:openjdk-r/ppa
```
"sudo -E " preserves the user environment, including any proxy config.

### **4. Continue installation of other dependencies.**
```bash
sudo apt-get install -y \
            bsdtar \
            elasticsearch \
            graphviz \
            nodejs \
            openjdk-11-jdk \
            postgresql-9.3
sudo chown -R usrname /etc/elasticsearch
```
### **5. Set environment variables**
Set environment in .bashrc file.
```bash
vi ~/.bashrc
export PATH=/usr/share/elasticsearch/bin:/usr/lib/postgresql/9.3/bin:$PATH
export BASH_ENV=~/.bashrc
```
### **6. Continue installation and environment setting**
```bash
sudo apt-get install -y python3.4-dev python3-pip
sed -i '1s;^;alias python=python3\n;' $BASH_ENV
source ~/.bashrc
sudo apt-get update
```
### **7. Install git, pull code and prepare for buildout.**
```bash
sudo apt-get install git
git clone https://github.com/utsw-bicf/pandiseased 
```
### **8. Running buildout**
```bash
cd ~/pandiseased
sudo pip3 install -U zc.buildout setuptools
sudo apt-get install libjpeg-dev zlib1g-dev
sudo pip3 install pillow==3.1.1
sudo apt-get install nginx
sudo apt-get update
buildout bootstrap
bin/buildout
```
>:stop_sign: _Note_: if you are working behind a proxy, you might need to install setuptools with 
```bash
sudo pip3 install -U --proxy http://myproxy.server:port zc.buildout setuptools
```

>:stop_sign: _Note_: There will be a error when running bin/buildout:
```bash
While:
  Installing encoded.
  Getting distribution for 'Pillow==3.1.1'.

  An internal error occurred due to a bug in either zc.buildout or in a recipe being used:
  Uninstalling the global version (or using a virtualenv) should work.
  The 'problem' is that buildout first installs the recipes and afterwards it installs all the other dependencies. The second step has no problem with globally installed packages, but the recipe-installing step does. And djangorecipe has a direct dependency on django (to make sure it is installed)...
  Anyway, not a buildout problem.
  Best solution: remove the globally installed django.
```
The following packages needed to be installed to solve this error,
```bash
sudo apt-get install libjpeg-dev zlib1g-dev
sudo pip3 install pillow==3.1.1
```
Can continue with `bin/buildout`.
### **9. Start the application locally**
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

### **10. :tada: Check out the app! :tada:**
- Browse to the interface at http://localhost:6543/.

## Linting your code within your code editor
### Visual Studio Code

Go to the Visual Studio Code marketplace and install these extensions:

 - ESLint
 - Python
 - Sass

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
