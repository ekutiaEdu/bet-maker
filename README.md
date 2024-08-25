# bet-maker

## Description
A simple betting service created according to the requirements of a test technical assignment. It consists of a web service using FastAPI and a PostgreSQL database.


## Installation

### Running in сontainers
1. Copy the contents of `.env.example` to `.env`.
2. Run the following command:
   ```bash
   docker compose up --build
   ```
3. Go to the Swagger page at: [http://localhost:5001/docs](http://localhost:5001/docs).

### Running Locally
1. Install Poetry by following the instructions [here](https://python-poetry.org/docs/#installation).
2. Install all dependencies using the command:
   ```bash
   poetry install
   ```
3. Update the variables in `.env` to match your database connection settings.
4. Start the application using the command:
   ```bash
   fastapi dev app/main.py
   ```
   Swagger will be available at: [http://localhost:8000/docs](http://localhost:8000/docs).


## Issues
e2e test does not work in GitHub Actions, marked it as ignored.

Since there is no persistent event storage as required:
1. It is possible to place a bet on an event that has already had its result set, meaning the event has already concluded.
2. It is possible to change the outcome of an event twice.
