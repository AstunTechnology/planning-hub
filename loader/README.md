## XML feed importer and aggregation

Command line script to import planning applications data from compliant XML feeds into PostgreSQL and make available to the planning-hub API.

## Installation

The loader is a Python app. It is assumed that you have first cloned the repository and changed into its directory.

    # Install system dependencies
    sudo apt-get install libpq-dev python-pip python-dev

    # [Install `virtualenvwrapper`](http://virtualenvwrapper.readthedocs.org/en/latest/)

    # Create a new virtual environment project for the planning-hub loader and activate it
    cd loader
    mkproject loader

    # Install Python dependencies via `pip`
    pip install -r requirements.txt

## Running

To run the loader on Linux, make the loader/app.py executable and:
    ./app.py
    
Alternatively:
    python app.py
