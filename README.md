# ccom-logger
Writes data from CCOM messages published to a MQTT broker to TimescaleDB database.

CCOM types supported:
- SingleDataMeasurement

## Dependencies

- Python >=3.8
- Poetry
- TimeScaleDB running separately
- Docker

### Install Poetry (Python package/environment manager)
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

(Optional) Set Poetry to store environments within project folder.  
This will create the .venv file during install to the project folder which is easier for VSCode to detect automatically.
```
poetry config virtualenvs.in-project true
```


## Developer environment setup
Install dependencies and generate a virtual environment:
```
poetry install
```

If you run into issues with installing psycopg2, you can try to install this dependency (Ubuntu):
´´´
sudo apt install libpq-dev
´´´

Activate virtual environment
```
poetry shell
```

## Run service

### In terminal for local development
```
python main.py
```

### In Docker container for production
Export requirements
```
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

Build Docker image
```
docker build -t ccom-logger .
```

Start Docker container from image
```
docker run --network host ccom-logger
```