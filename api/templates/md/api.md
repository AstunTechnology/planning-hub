{% filter markdown %}
## Publishing API

Web API to retrieve applications in [GeoJSON](http://geojson.org/) format optionally [filtering](#toc_6) and [sorting](#toc_19) on one of the fields described below.

### Endpoints

The API is versioned to allow changes in future, requests should always be made against a specific version of the API.

All endpoints allow the results to be filtered and sorted via query string parameters.

Endpoints for the current version of the API are shown below:

#### Search

Search for applications passing [filter parameters](#toc_6) via the query string:

    {{ url_for('.search') }}?

#### Single Authority

Applications published by a given authority identified by [GSS code](http://en.wikipedia.org/wiki/ONS_coding_system#Current_GSS_coding_system):

    /developmentcontrol/0.1/applications/gss_code/<code>?

#### Single status code

Applications with a given application status code:

    /developmentcontrol/0.1/applications/status/<status>?

### Response

The response of the API will be a list of applications containing all fields in the national planning schema in GeoJSON format (with the mime-type `application/json`) or an error response with appropriate HTTP status code.

### Filter by

#### Application status

Parameter name: `status`

One or more application status constants. When specified via the query string multiple status values are comma separated.

##### Values

The national planning schema provides a fixed set of application status values listed below together with the constant value used with this API:

    API Parameter value | National Planning Schema value
    --------------------|-------------------------------------------------------------------------------
    live                | Live - in the process of being decided
    withdrawn           | Withdrawn
    decided             | Decided
    appeal              | Appeal - in the process of being decided via a non-determination appeal
    called_in           | Called in - in the process of being considered by the Secretary of State
    referred_to_sos     | Referred to SoS - in the process of being considered by the Secretary of State
    invalid             | Invalid - requires something to happen to it before it can be decided
    not_ours            | Not ours - belong to other planning authorities
    registered          | Registered - received but not yet been processed and validated

##### Query string

Live and decided applications

    status=live,decided


#### GSS code

Parameter name: `gss_code`

One or more GSS codes. When specified via the query string multiple GSS code values are comma separated.

Each authority has a unique (Government Statistical Service) GSS code assigned by the [ONS (Office for National Statistics)](http://www.ons.gov.uk/). A complete list of GSS codes can be found here via the [ONS Geoportal](https://geoportal.statistics.gov.uk).

##### Values

A nine character GSS code.

Current Districts and Borough codes within Surrey County:

    GSS Code  | Authority
    ----------|----------------------
    E07000207 | Elmbridge
    E07000208 | Epsom and Ewell
    E07000209 | Guildford
    E07000210 | Mole Valley
    E07000211 | Reigate and Banstead
    E07000212 | Runnymede
    E07000213 | Spelthorne
    E07000214 | Surrey Heath
    E07000215 | Tandridge
    E07000216 | Waverley
    E07000217 | Woking

##### Query string

Surrey Heath and Mole Valley

    gss_code=E07000214,E07000210

#### Date range

Parameter names: `case_date`, `decision_target_date`, `decision_notice_date`, `public_consultation_start_date`, `public_consultation_end_date`

##### Values


    Value        | Description
    -------------|---------------------------------------
    last_7_days  | Last 7 days including the current day
    last_14_days | Last 14 days including the current day
    last_30_days | Last 30 days including the current day

##### Query string

Applications with a case date with in the last 7 days:

    case_date=last_7_days

Applications with a public_consultation_start_date within the last 30 days:

    public_consultation_start_date=last_30_days

#### Bounding box

The bounding box for search for applications in WGS84 format.

Parameter name: `bbox`

##### Values

A bounding box is of the form: `xmin, ymin, xmax, ymax`

##### Query string

Surrey Heath District

    bbox=-0.78,51.25,-0.53,51.4

### Order by

Results can be ordered by one of the following fields:

    Field     | Description
    ----------|-----------------------------------------
    status    | Application status code (alphabetically)
    case_date | Case date (on date)

An optional sort order can also be specified:

    Value | Description
    ------|--------------------------------
    asc   | Sort assending (a to z, 9 to 0)
    desc  | Decending (z to a, 9 to 0)

#### Query string

Order by case date most recent first:

    order_by=status&sort_order=desc

### Example API requests

All of the following requests return live and decided applications for Surrey Heath District ordered by case date:

    {{ url_unquote_plus(url_for('.search', status='live,decided', gss_code='E07000214', orderby='case_date')) }}

    /developmentcontrol/0.1/applications/gss_code/E07000214?status=live,decided&orderby=case_date

    /developmentcontrol/0.1/applications/status/live?gss_code=E07000214&orderby=case_date

{% endfilter %}
