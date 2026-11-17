#### Introduction

- Source repository and inventory for hosting all K8S clusters. Please **make sure you have<br>
  your development environment setup before working or making any changes**.

- IMPORTANT: This is deprecated but remains here for completeness.

#### Setting up the development environment (Ansible and Python)

- ** You must setup Python Virtual Enviroment so everything is isolated and helps with working with <br>
  specific version of python, 3rd-party libraries and Ansible itself. **

- Note: if you are on Windows it is strongly encouraged to use WSL1 or WSL2. (NOTE: is using WSL2 <br>
  extra precautions needs to be taken.

- Ensure the source code is checked out in **WSL filesystem** NOT in Windows FileSystem

##### Installing different python version on Ubuntu/debian based distros

If you are using a different distribution, u can always compile the python distribution but prefer the
distribution approach.

###### Python 2.7.x and Ansible 2.9.x (DEPRECATED) Please migrate to python 3.8.x and ansible-core 2.11.x and ansible 4.x.x

NOTE: Using python 2.7 is deprecated and should only be used in situations where we need to go back to certain branch, it is documented here for completeness.

- Python 2.7.x in ubuntu bionic

```sh
# just a safe bet
$ sudo apt install software-properties-common
# install latest python 2.7
$ sudo apt install python2.7
# install pip since we will be using  pip to install everything in virtualenv
$ sudo apt install python-pip
# Most important, install the virtualenv module (REMEMBER, Python 3.x uses venv)
$ sudo apt install virtualenv
# At this point we are ready to create virtual environment for Ansible
```

- Create virtual environment(s)

It is better to create a dedicated virtual environment folder in your home directory (WSL) so we can place all the virtual environments there and switch between.

```sh
# create a virtual environment folder (you can name it whatever u want
$ mkdir -p ~/venv

# Now create one folder where we will have anible 2.9.x and Python 2.x virtual environment
# python27-ansible29 you can name it whattever is intuitive to you
$ mkdir -p ~/venv/python27-ansible29

# Now we are ready to create the virtual environment.
$ virtualenv --python=$(which python2) ~/venv/python27-ansible29

# Now you can activate the virtual environment so everything is installed and done in this version
# of python. (tip: if using bash create an alias)
$ source ~/venv/python27-ansible29/bin/activate

```

- Install Ansible 2.9.24 (currently tested with this project)

  - IMPORTANT: activate the virtual environment

```sh
# Assuming u are in the virtual environment. Let's install all required modules (including ansible)
$ cd <to this project root directory>

# now use the py2-a29-requirements.txt file in this folder to install Ansible and anything else we need for this
# project
$ pip install -r py2-a29-requirements.txt

```

#### Ansible Galaxy Collections

Ansible should already be installed and in your path ($HOME/.local/bin). Please
refer to [Galaxy User Guide](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html)
for more information in locking down a version or upgrade

##### community.crypto

```sh
 $ ansible-galaxy collection install -vv community.crypto
```
