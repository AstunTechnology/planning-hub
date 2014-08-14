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
* `CONNECTION_STRING`: <tt>"user=_username_ password=_password_ dbname=_database_ port=_port_"</tt>
#### Email configuration
The loader assumes that you will be using STARTTLS for security, otherwise standard SMTP settings:

* `SMTP_HOST`: DNS name or IP address of SMTP server
* `SMTP_USER`: Username for access to server 
* `SMTP_PASS`: Password for above user

The loader also requires an email address to send from and one to send administrative notifications to (e.g. import errors)
* `HUB_ADMIN`: Email address of Planning Hub administrator
* `HUB_EMAIL`: Email address that notifications are to be sent from.

### Feed settings
Planning application feed configuration resides in a `planning_applications_feeds.txt` file. This is a pipe (`|`) delimited file with each line of the format:
```
identifier|feed uri|feed admin email
```
* *identifier* - The GSS code of the organization publishing the feed
* *feed uri* - Full URI of the feed
* *feed admin uri* - email address of the person to be notified when there are errors with the feed import process

### Data requirements
The feed must have a single root element, each child node of this corresponds to a planning application record and must be named `planning_hub_feed`.
The fields for each planning application record correspond to the ones defined in the [Local Open Data Incentive Scheme Planning Applications Schema](http://schemas.opendata.esd.org.uk/PlanningApplications/LocalOpenDataIncentiveSchemePlanningApplicationsSchemaGuidance.pdf), but field names must be lowercase. 

#### Fields
The following fields **must** be present in every record and have a valid value: `'extractdate', 'publisherlabel', 'casereference', 'caseurl', 'locationtext'`

The following fields are optional: `'extractdate', 'publisherlabel', 'casereference', 'caseurl', 'servicetypelabel', 'casetext', 'locationtext'`

All field values should be valid according to the Schema, although dates in `YYYY/MM/DD` or `YYYY-MM-DD` or ISO datetime format will also be accepted.


#### Sample
```xml
<NewDataSet>
  <planning_hub_feed>
    <extractdate>2014/08/12</extractdate>
    <publisheruri>http://opendatacommunities.org/id/PATH/TO/COUNCIL</publisheruri>
    <publisherlabel>COUNCIL_NAME</publisherlabel>
    <organisationuri>http://opendatacommunities.org/id/PATH/TO/COUNCIL</organisationuri>
    <organisationlabel>COUNCIL_NAME</organisationlabel>
    <casereference>REFERENCE</casereference>
    <caseurl>URL_TO_APPLICATION_DETAILS</caseurl>
    <casedate>2001/12/11</casedate>
    <servicetypeuri>http://id.esd.org.uk/service/487</servicetypeuri>
    <servicetypelabel>Full planning applications</servicetypelabel>
    <classificationuri />
    <classificationlabel />
    <casetext>CASE_TEXT</casetext>
    <locationtext>LOCATION_TEXT</locationtext>
    <decisiontargetdate />
    <status>Live</status>
    <coordinatereferencesystem>WGS84</coordinatereferencesystem>
    <geox>X</geox>
    <geoy>Y</geoy>
    <geopointlicensingurl>http://www.ordnancesurvey.co.uk/business-and-government/public-sector/mapping-agreements/end-user-licence.html</geopointlicensingurl>
    <decisiondate />
    <decision />
    <decisiontype />
    <decisionnoticedate />
    <appealref />
    <appealdecisiondate>2001/12/11</appealdecisiondate>
    <appealdecision />
    <geoareauri>http://statistics.data.gov.uk/doc/statistical-geography/GSS_CODE</geoareauri>
    <geoarealabel>COUNCIL_NAME</geoarealabel>
    <groundarea>1000</groundarea>
    <agent />
    <publicconsultationstartdate />
    <publicconsultationenddate />
    <responsesfor>0</responsesfor>
    <responsesagainst>0</responsesagainst>
  </planning_hub_feed>
</NewDataSet>
```

