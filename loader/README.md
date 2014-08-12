## XML feed importer and aggregation

Command line script to import planning applications data from compliant XML feeds into PostgreSQL and make available to the planning-hub API.

### Installation

The loader is a Python app. It is assumed that you have first cloned the repository and changed into its directory.

The only database currently tested is PostgreSQL 9.3 with PostGIS 2.1.

* Install system dependencies: `sudo apt-get install libpq-dev python-pip python-dev postgresql 9.3 postgresql-9.3-postgis-2.1 `
* Create a database with the PostGIS extension, preferably with a dedicated user
  * `CREATE USER user;`
  * `ALTER ROLE user PASSWORD 'password';`
  * `CREATE DATABASE dbname OWNER user;`
  * Connect to the new database and: `CREATE EXTENSION postgis;`
* [Install `virtualenvwrapper`](http://virtualenvwrapper.readthedocs.org/en/latest/) 
* Create a new virtual environment project for the planning-hub loader and activate it:
  * `cd loader`
  * `mkproject loader`
* Install Python dependencies via `pip`: `pip install -r requirements.txt`

### Running

To run the loader on Linux, make the loader/app.py executable and:
```
./app.py
```
    
Alternatively:
```
python app.py
```

### Application settings
Application settings are picked up from environment variables (e.g. on Linux `export HUB_ADMIN=admin@example.org`)
#### PostgreSQL connection
A standard PSQL connection string, using the names and password set up previously.
`CONNECTION_STRING`: <tt>"user=_username_ password=_password_ dbname=_database_ port=_port_"</tt>
#### Email configuration
The loader assumes that you will be using STARTTLS for security, otherwise standard SMTP settings:
`SMTP_HOST`: DNS name or IP address of SMTP server
`SMTP_USER`: Username for access to server 
`SMTP_PASS`: Password for above user

The loader also requires an email address to send from and one to send administrative notifications to (e.g. import errors)
`HUB_ADMIN`: Email address of Planning Hub administrator
`HUB_EMAIL`: Email address that notifications are to be sent from.

### Feed settings
Planning application feed configuration resides in a `planning_applications_feeds.txt` file. This is a pipe (`|`) delimited file with each line of the format:
```
identifier|feed uri|feed admin email
```
* *identifier* - The GSS code of the organization publishing the feed
* *feed uri* - Full URI of the feed
* *feed admin uri* - email address of the person to be notified when there are errors with the feed import process
