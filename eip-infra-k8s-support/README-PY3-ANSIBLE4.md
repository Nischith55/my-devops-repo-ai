#### Introduction

Source repository and inventory for hosting all K8S clusters. Please **make sure you have your development<br>
environment setup before working or making any changes**.

#### Setting up the development environment (Ansible and Python)

- ** You must setup Python Virtual Enviroment so everything is isolated and helps with working with <br>
  specific version of python, 3rd-party libraries and Ansible itself. **

- Note: if you are on Windows it is strongly encouraged to use WSL1 or WSL2. (NOTE: is using WSL2 <br>
  extra precautions needs to be taken.

- Ensure the source code is checked out in **WSL filesystem** NOT in Windows FileSystem

##### Installing different python version on Ubuntu/debian based distros

If you are using a different distribution, u can always compile the python distribution but prefer the
distribution approach.

###### Python 3.8.x and ansible 4.x.x (note ansible 4.x.x will select ansible-core-2.11.x)

- Setup python 3.8 venv and installation ubuntu

```sh
# just a safe bet
$ sudo apt install software-properties-common

# add the apt repository for python 3.8 or 2.7
$ sudo add-apt-repository ppa:deadsnakes/ppa

# install python  3.8
$ sudo apt install python3.8

# install everything neededd for virtualenv
$ sudo apt install python3.8-dev python3.8-distutils python3.8-venv

# Most important, install the virtualenv module (REMEMBER, Python 3.x uses venv)
$ sudo apt install virtualenv
# At this point we are ready to create virtual environment for Ansible

# if using ubuntu distro install python3-testresources package
$ sudo apt install python3-testresources
```

- Create virtual environment(s)

It is better to create a dedicated virtual environment folder in your home directory (WSL) so we <br>
can place all the virtual environments there and switch between.

```sh
# create a virtual environment folder (you can name it whatever u want
$ mkdir -p ~/venv

# Now create one folder where we will have ansible 2.9.11 and Python 3.8 virtual environment
# python27-ansible29 you can name it whattever is intuitive to you
$ mkdir -p ~/venv/python38-ansible211

# Now we are ready to create the virtual environment.
$ python3.8 -m venv ~/venv/python38-ansible211

# Now you can activate the virtual environment so everything is installed and done in this version
# of python. (tip: if using bash create an alias)
$ source ~/venv/python38-ansible211/bin/activate

```

- Install ansible-core 2.11.x and ansible 4.x.x

  - IMPORTANT: activate the virtual environment

```sh

# now use the py38-ansible4-requirements.txt file in this folder to install Ansible and anything else we 
# need for this project.
# IMPORTANT make sure python3.8 is from your virtual environment or change it

$ python3 -m pip install -r py38-ansible4-requirements.txt

```

#### Ansible Galaxy Collections

Before installing Ansible Galaxy Collections make sure you have activate the virtual environment

- we are going to use Python 3.8 and ansible 4.x.x

##### community.general

```sh
 $ ansible-galaxy collection install -vv community.general
```

##### community.crypto

```sh
 $ ansible-galaxy collection install -vv community.crypto
```
