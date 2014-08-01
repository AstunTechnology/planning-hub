!function (name, context, definition) {
    if (typeof module != 'undefined' && module.exports) {
        module.exports = definition(require('leaflet').noConflict(), require('reqwest'));
    } else {
        context[name] = definition(L, reqwest);
    }
}('HubMap', this, function (L, reqwest) {

    HubMap = this.HubMap || {};
    HubMap.BASE_URL = HubMap.BASE_URL || "{{ url_for('.index', _external=True).rstrip('/') }}";
    HubMap.PLAN_APP_INFO = HubMap.PLAN_APP_INFO || "<h2><a href='{caseurl}'>{casereference}</a></h2><p>{locationtext}</p><p>Status: {status}</p>";

    HubMap.map = function(elem, options) {

        L.Icon.Default.imagePath = HubMap.BASE_URL + "/embed/images";

        var map = L.map(elem).setView([51.23, -0.32], 9);

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

        data_url = HubMap.BASE_URL + options.data_url;
        reqwest({url: data_url, type: 'jsonp'}).then(function (data) {
            if (data.features && data.features.length) {
                map.fitBounds(apps.addData(data).getBounds());
            } else {
                HubMap.warn('No results returned for data_url: ', data_url);
            }
        });

        function popUp(f, l){
            var content = L.Util.template(HubMap.PLAN_APP_INFO, f.properties);
            l.bindPopup(content);
        }

        return map;

    };

    HubMap.createMaps = function() {

        var elems = document.getElementsByClassName('hub-map'),
            maps = [];

        if (elems.length === 0) {
            HubMap.warn('No elements found with the "hub-map" class at this time. You may need to call HubMap.createMaps when the page has loaded or create a map manually with HubMap.map.');
        }

        for (var i = 0, elem, data_url; i < elems.length; i++) {
            elem = elems[i];
            data_url = elem.getAttribute("data-url");
            if (data_url) {
                maps.push(HubMap.map(elem, {data_url: data_url}));
            } else {
                HubMap.warn('No data URL passed, skipping creating map. Element: ', elem);
            }
        }

        return maps;

    };

    HubMap.warn = function() {
        if (console && console.warn) console.warn.apply(console, Array.prototype.slice.call(arguments));
    };

    // Attempt to create maps for elements with a "hub-map" class
    HubMap.createMaps();

    return HubMap;

});
