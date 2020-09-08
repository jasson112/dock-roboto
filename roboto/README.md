pip install --editable .

you must to instal virtualenv and later do this command to install dependencies:

pip install -r ./requirements.txt

if you want to update the dependencies yu must to do this command:

pip freeze > ./requirements.txt

if yoou facing problems with dependencies do this:

% rm -r venv/ # Nukes the old environment % python3 -m venv venv/ # Makes a blank new one % pip install -r ./requirements.txt # Re-installs dependencies 