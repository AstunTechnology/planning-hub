;(function(){

    HubMap = window.HubMap || {};
    HubMap.BASE_URL = HubMap.BASE_URL || "http://planning-hub.surrey.gov.uk/";
    HubMap.PLAN_APP_INFO = HubMap.PLAN_APP_INFO || "<h2><a href='{caseurl}'>{casereference}</a></h2><p>{locationtext}</p><p>Status: {status}</p>";

    HubMap.map = function(elem, options) {

        var map = L.map(elem).setView([51.505, -0.09], 8);

        var mqAttr = 'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash; ';
        var osmAttr = 'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &mdash; ';
        var hubAttr = 'Planning Applications via <a href="#">Surrey Planning Hub</a>';

        var mqOpt = {
            url: 'http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.jpeg',
            options: {attribution: mqAttr + osmAttr + hubAttr, subdomains:'1234'}
        };
        var mq=L.tileLayer(mqOpt.url, mqOpt.options);

        mq.addTo(map);

        url = HubMap.BASE_URL + options.url;
        console.log(url);
        var jsonTest = new L.GeoJSON.AJAX([url], {
            onEachFeature: popUp, dataType: "jsonp"
        }).on('data:loaded', appsLoaded).addTo(map);

        function popUp(f, l){
            var content = L.Util.template(HubMap.PLAN_APP_INFO, f.properties);
            l.bindPopup(content);
        }

        function appsLoaded(e) {
            map.fitBounds(jsonTest.getBounds());
        }

        return map;

    };

    var maps = document.getElementsByClassName('hub-map');

    for (var i = 0, map; i < maps.length; i++) {
        map = maps[i];
        HubMap.map(map, {url: map.getAttribute("data-url")});
    }

})();
