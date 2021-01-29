# MooseJuice
## How To Get started:

### Fix the enviroment
Install the python virtual enviroment package with pip:
$ python3 -m pip install --user virtualenv

Navigate to or create an empty repository.
Create a virtual enviroment:
$ python3 -m venv env

Activate the enviroment:
$ source env/bin/activate


### Clone this git repository to the folder

$ git clone https://github.com/s183922/MooseJuice.git

### Update the enviroment

$ python -m pip install -r MooseJuice/requirements.txt

### Start the server
Navigate to the cloned git repository MooseJuice
Open a python terminal:
$ python
>> from MooseJuice import db
>> db.drop_all()   # Deletes existing database
>> db.create_all() # Initialise new database

in python terminal:
>> run.py
in command prompt:
$ python MooseJuice/run.py
