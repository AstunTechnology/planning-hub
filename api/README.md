## Publishing API and Embedded Maps

Web API to retrieve applications in [GeoJSON](http://geojson.org/) format optionally filtering and sorting on one of the fields described below. API usage can be found in [./templates/md/api.md](./templates/md/api.md).

## Installation

The publishing API is a Python Flask web app. It is assumed that you have first cloned the repository and changed into it's directory.

    # Install system dependencies
    sudo apt-get install libpq-dev python-pip python-dev

    # Install `virtualenv` via `pip`
    sudo pip install virtualenv

    # Create a new virtual environment for the planning-hub api and activate it
    cd api
    mkvirtualenv env
    source env/bin/activate

    # Install Python dependencies via `pip`
    pip install -r requirements.txt

## Running

To run a development server activate the virtual environment then run:

    python app.py

## Development

### Embedded Maps (HubMap)

HubMap uses Node npm together with Browserify and npm-css to build and bundle it's assets.

    # Install NodeJS and npm
    sudo apt-get install npm

    # Install dependencies
    cd api/static/hubmap/
    npm install

    # Build HubMap (assets output in ./dist directory)
    npm run build

    # Optionally use `nodenom` to build when files change
    nodemon --ignore ./dist --ext js,css --exec "npm run build"
