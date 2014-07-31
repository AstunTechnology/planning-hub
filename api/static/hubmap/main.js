var L = require('leaflet').noConflict();
var reqwest = require('reqwest');

HubMap = window.HubMap || {};
HubMap.BASE_URL = HubMap.BASE_URL || "{{ url_for('.index', _external=True).rstrip('/') }}";
HubMap.PLAN_APP_INFO = HubMap.PLAN_APP_INFO || "<h2><a href='{caseurl}'>{casereference}</a></h2><p>{locationtext}</p><p>Status: {status}</p>";

L.Icon.Default.imagePath = HubMap.BASE_URL + "{{ url_for('.embed', path='images') }}";

HubMap.map = function(elem, options) {

    var map = L.map(elem).setView([51.505, -0.09], 8);

    var mqAttr = 'Tiles: <a href="http://www.mapquest.com/">MapQuest</a> - ';
    var osmAttr = 'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors - ';
    var hubAttr = 'Planning Applications: <a href="#">Surrey Planning Hub</a>';

    var mqOpt = {
        url: 'http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.jpeg',
        options: {attribution: mqAttr + osmAttr + hubAttr, subdomains:'1234'}
    };
    var mq = L.tileLayer(mqOpt.url, mqOpt.options);

    mq.addTo(map);

    var apps = L.geoJson(null, {onEachFeature: popUp}).addTo(map);

    url = HubMap.BASE_URL + options.url;
    reqwest({url: url, type: 'jsonp'}).then(function (data) {
        map.fitBounds(apps.addData(data).getBounds());
    });

    function popUp(f, l){
        var content = L.Util.template(HubMap.PLAN_APP_INFO, f.properties);
        l.bindPopup(content);
    }

    return map;

};

var maps = document.getElementsByClassName('hub-map');

for (var i = 0, map; i < maps.length; i++) {
    map = maps[i];
    HubMap.map(map, {url: map.getAttribute("data-url")});
}
