FROM python:3.8-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy project to image
COPY . .

# Install dependencies for psycopg2
RUN apt update && apt install -y libpq-dev gcc

# Install python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Start service
ENTRYPOINT ["python", "main.py"]