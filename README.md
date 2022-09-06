# CCOM-logger
Writes data from CCOM messages published to a MQTT broker to a database.

TimescaleDB used as default.
Support for other databases can be added, e.g. document databases like InfluxDB.

The service is recommended to access MQTT broker and database locally.

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

### (Optional) Set Poetry to store environments within project folder.  
This will create the .venv file during install to the project root folder which is easier for editors like VSCode to detect automatically.
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

## Configuration
Configuration is done with environment variables or in .env at project root folder:
```
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=postgres
DATABASE_USER=user
DATABASE_PASSWORD=password

MQTT_CLIENT_ID=ccom-logger
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

BUFFER_MAX_SIZE=10000
```

## Run service
Configure the environment variables before running.

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