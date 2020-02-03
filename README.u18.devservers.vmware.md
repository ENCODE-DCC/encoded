#steps to follow to install the encode on the vmware fusion.
1)insatll the vmware fusion.
## You should have installed the vmware fusion what ever is thr latest version.
link to install the version:-https://my.vmware.com/en/web/vmware/info/slug/desktop_end_user_computing/vmware_fusion/11_0

2)install the ubuntu 11.04.*
## get the iso ubuntu desktop version installed in the mac
link to insatll it https://ubuntu.com/download/desktop

After the installation is done please give the user name and password for setting up the new instance.

prerequsites for configuring the ubuntu on vmware.

1)Go to the virtualmachine on the top left hand side and go to hardware setting---> increase the size of the hard disk to atleaset 200G
2)Go to the virtualmachine on the top left hand side and click on the settings--->processors and memory--->processors(give 4 core cpus) and then in the same window increase the memory to 11g(which is ram the reson is elasticsearch uses 4G of ram and java uses another 3 to 4G to get redundant from the test case failure please increase the size)

incase if you see any kind of errors regarding the os insufficent memory/java memory is insuffcient(for xmx and xms) please shutdown your provisoned virtual machine and increase the hard-disk/Ram size accordingly.

give it some time to boot it up.

goodluck with your new provisoned new ubuntu machine.

pre requisets to be installed befor making the encoded to run.

Note i will be using the user test-encode for reference here please give your own user name.

1) add the user as elastic serach will not start using root.
  a) command to add the user is ---> sudo adduser test-encode (in place of test-encode please provide your own user name)

    then it will ask you some of the questions linke mentioned below just use the enter button to skip the info but please provide the password

    Adding user `test-encode' ...
    Adding new group `test-encode' (1001) ...
    Adding new user `test-encode' (1001) with group `encode-ubutnu' ...
    Creating home directory `/home/test-encode' ...
    Copying files from `/etc/skel' ...
    Enter new UNIX password: (please give your passwd)
    Retype new UNIX password: (please re enter your passwd)
    passwd: password updated successfully
    Changing the user information for encode-ubutnu
    Enter the new value, or press ENTER for the default
          Full Name []:
          Room Number []:
          Work Phone []:
          Home Phone []:
          Other []:
      Is the information correct? [Y/n] y (say y if you think yoiur are good ether give n)

  b) execute this commands to check weather the user is added or not.
        command 1) sudo cat /etc/passwd | grep test-encode   ( here you can see your user has been created  in place of test-encode please provide your own user name )
        command 2) sudo cat /etc/shadow | grep test-encode   ( here you can see user passwd has been created in place of test-encode please provide your own user name )


  c) you have to give the sudoers privilages to avoid some the blockers.
        command 1) sudo su ( it will take to the root user please give the password you have given while initial setup)
        command 2) sudo nano /etc/sudoers (please follow the below after enter this command )

                 you will see on the 19th or 20th line some thing linke this .

                 # User privilege specification
                   root    ALL=(ALL:ALL) ALL

                now please add your user some think like this with your user ( for exapmle test-encode )
                # User privilege specification
                  root    ALL=(ALL:ALL) ALL
                  test-encode    ALL=(ALL:ALL) ALL

          then save it and exit out

        command 3) exit (this will exit from the root user)
        command 4) sudo su - test-encode
2) please install curl and git
  a) command to install git is sudo apt-get install git -y
  b) command to install curl is sudo apt-get install curl -y


3)Download java manually and here the steps to insatll it manually on ubuntu machine.
  a) Link to install the jdk https://www.oracle.com/technetwork/java/javase/downloads/index.html
  b) Please select the version to be installed saying Oracle Jdk for example iam using here jdk-11.0.6.
  c) Please accept the license before downloading.
  d) It will ask to create an account to download the jdk please create the account and now please do not select the open option select the save file option.
  e) Now Do not select the open with option please select the save file and it will save in the /home/(your vm-ware user)/Downloads
  f) sudo mkdir /opt/encode
  g) sudo chown test-encode:test-encode /opt/encode
  h) sudo chmod 777 /opt/encode
  i) mv /home/(your user)/Downloads/jdk-11.0.6_linux-x64_bin.tar.gz /opt/encode/
  j) cd /opt/encode/
  k) sudo mkdir -p /usr/lib/jvm
  l) sudo chmod 777 /usr/lib/jvm
  m) sudo tar -xzvf /opt/encode/jdk-11.0.6_linux-x64_bin.tar.gz --directory /usr/lib/jvm/
  n) sudo chmod 755 /usr/lib/jvm
  o) sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk-11.0.6/bin/java 100

  to check the java version 

  a) java -version
  b) java

Java insatllation is done.

4) Download The elassticsearch manually using the below steps.

  a) cd /opt/encode/
  b) curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.6.16.tar.gz (if curl does not work please provide sudo)
  c) tar -xvzf elasticsearch-5.6.16.tar.gz
  d) chown -R test-encode:test-encode  elasticsearch-5.6.16
  e) cd /opt/encode/elasticsearch-5.6.16/bin/
  f) pwd (take the path add in the bashrc)
  g) sudo nano ~/.bashrc

  add some thing like this on the bashrc file
  export PATH="/opt/encode/elasticsearch-5.6.16/bin:$PATH" ###provide the binary pathg for the elasticsearch

  h) save the bashrc file and exit.
  i) now do source ~/.bashrc

Elasticsearch setup is done.

5) Add the dependencies for the Postgresql-11 for ubuntu 18.04. (please make sure you using test-encode user )
  a) sudo apt-get install curl ca-certificates gnupg
  b) curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
  c) sudo add-apt-repository 'deb http://apt.postgresql.org/pub/repos/apt bionic-pgdg main'
  d) sudo apt-get update

6) please insatll following dependecies for the python 3.6.9 and please make sure you are using test-encode.

  a) cd /opt/encode
  b) touch install.txt
  c) chmod 777 install.txt
  d) sudo nano install.txt (add the below following packages which are supposed to be installed using your file)

awscli
unattended-upgrades
apache2
apache2-utils
ssl-cert
libapache2-mod-wsgi-py3
bsdtar
libjpeg8-dev
zlib1g-dev
apt-transport-https
nodejs
g++
gcc
make
nginx
libpq-dev
daemontools
postgresql-11
build-essential
libffi-dev
libssl-dev
python3.7-dev
python3-pip
python3.7-venv
software-properties-common
redis-server
lzop
net-tools

##please use the following command to install all the above mentioned packages.
  e) cat install.txt | xargs sudo apt-get install -y

7)Add the binary path for postgresql-11

  a) sudo nano ~/.bashrc
  add the below line in the bashrc file.

export PATH="/usr/lib/postgresql/11/bin:$PATH" ###the binary path for the postgresql

  b) save and exit
  c) source ~/.bashrc
  d) pip3 install zope.deprecation


8)Install nvm,npm and node 10 (please make sure you using test-encode user)

  a) curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash

###please execute the following commands it will add the path in the ~/.bashrc file.
  b) export NVM_DIR="$HOME/.nvm"
     [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
     [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

  c) nvm install node v10.14.0
  d) nvm use 10.14.0

9) git clone the repository in to /opt/encode
  a) cd /opt/encode
  b) git clone the repo
  c) cd encoded
  d) pip3 install -U zc.buildout setuptools
  e) buildout bootstrap
  f) bin/buildout


10)To run the test cases using google chrome
  a) link to download the chrome driver https://chromedriver.chromium.org/downloads
  b) please do not open the file save the file.
  c) cd ~
  d) cd /home/(vm-ware-user)/Downloads
  e) sudo mv chromedriver_linux64.zip /opt/encode
  f) get back to your test-encode user
  g) cd /opt/encode
  h) sudo unzip chromedriver_linux64.zip
  i) mkdir -p bin
  j) mv chromedriver bin/
  k) sudo nano ~/.bashrc

     export PATH="/opt/encode/bin:$PATH" #the binary path for chrome driver which we have changed above

  l) save and exit it out
  m) source ~/.bashrc
   All the required packeges have been installed.

11) change some of the permisions.

  a) sudo chmod -R 777  /var/log/nginx/
  b) sudo chmod 777 /var/lib/nginx/
  c) sudo nano /etc/postgresql/11/main/pg_hba.conf

   change the content in the file from peer to trust in two places.


    # Database administrative login by Unix domain socket
     local   all             postgres                                trust

    # TYPE  DATABASE        USER            ADDRESS                 METHOD

    # "local" is for Unix domain socket connections only
     local   all             all                                     trust
    # IPv4 local connections:

    d) sudo service postgresql restart
    e) sudo ln -s /var/run/postgresql/.s.PGSQL.5432 /tmp/snovault/pgdata/.s.PGSQL.5432

12) Enabling and adding the user to XHOST as to make google-chrome running.
  a) sudo su
  b) xhost enable
  c) xhost +SI:localuser:test-encode
  d) sudo su test-encode
  e) google-chrome (test is is working or not you should see the google ui)

    All the changes have been done accordingly

13) build the dev server.
  a) bin/dev-servers development.ini --app-name app --clear --init --load

    if you see /run/ngnix.pid permision denaied please ignore.

14) open Another terminal 
  b) bin/pserve develo.ini
