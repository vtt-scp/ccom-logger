# ccom-logger
Write data from CCOM messages to database

## Dependencies

- Python >=3.8
- Poetry

### Poetry (Python package/environment manager)
As instructed in https://python-poetry.org/docs/#installation  
Download and run poetry installation script:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```
You may need to add poetry to PATH manually. The following should add Poetry automatically to PATH on login:
```
echo $'\n# Export Poetry to PATH\nexport PATH=$PATH:$HOME/.poetry/bin' >> ~/.bashrc
```
May require relogin to terminal (or reboot).


## Developer environment setup

(Optional) Set Poetry to store environments within project folder.  
This will create the .venv file during install to the project folder which is easier for VSCode to detect automatically.
```
poetry config virtualenvs.in-project true
```

Install dependencies and generate a virtual environment:
```
poetry install
```

If you run into issues with installing psycopg2, you can try to install this dependency (Ubuntu):
´´´
sudo apt install libpq-dev
´´´


## Activate virtual environment
```
poetry shell
```