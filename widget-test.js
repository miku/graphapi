(function() {
    //LOKALER TEST mit jsondaten.txt
    //GLOBAL_GND = ['http://d-nb.info/gnd/118540238','http://d-nb.info/gnd/118525239'];

    //Funktion lädt, je nach Anzahl der darzustellenden GNDS, eine bestimmte CSS. Zudem fragt sie die gesuchten
    //GNDS von der API ab.
    window.onload = function() {
        var stores = {};
        if (typeof(GLOBAL_GND) != "undefined") {
            for (var c = 0; c < GLOBAL_GND.length; c++) {
                if (c == 0) {
                    //Für Test auf Alpha
                    //loadCSS("/vufind2/de_15/themes/knowledgegraph/css/singleItem.css", "singleItem");
                    loadCSS("/themes/knowledgegraph/css/singleItem.css", "singleItem");
                } else if (c == 1) {
                    var oldCSS = document.getElementById("singleItem");
                    if (oldCSS) {
                        oldCSS.parentNode.removeChild(oldCSS);
                    }
                    //loadCSS("/vufind2/de_15/themes/knowledgegraph/css/multiItem.css", "multiItem");
                    loadCSS("/themes/knowledgegraph/css/multiItem.css", "multiItem");
                }
                var gnd_number = splitIdentifier(GLOBAL_GND[c]);

                // prepare skeleton for GND
                if (document.getElementById('subject_' + gnd_number) === null) {
                    newSubject(gnd_number);
                    newLiteralContainer(gnd_number);
                    newButtonText(gnd_number);
                    newButton(gnd_number, "uri");
                    newUriContainer(gnd_number);
                }
                //newHeadContainer(gnd_number);
                //newHeadDepiction(gnd_number);
                if (document.getElementById('h_label_' + gnd_number) === null) {
                    newHeadLabel(gnd_number);
                    fillHeadLabel(gnd_number, gnd_number);
                }

                //debugger;

                console.log("Getting data");

                //LOKALER TEST
                //$.get("/themes/knowledgegraph/js/jsondaten.txt", splitJSON(GLOBAL_GND[c], gnd_number));

                //ALPHA
                //$.get("https://alpha.finc.info/knowledgegraph/" + GLOBAL_LANG + "/" + gnd_number, splitJSON(GLOBAL_GND[c], gnd_number));

                //BLADE6
                // $.get("http://localhost:5000/gnd/"+gnd_number, splitJSON(GLOBAL_GND[c], gnd_number));

                stores[gnd_number] = new MinStore();
                // node im Widget einfügen, die Daten zur GND enthält
                var jsonStream = new EventSource('http://localhost:5000/stream/' + gnd_number);
                jsonStream.onmessage = function (gnd_uri, gnd_number) { return function (e) {
                    if (e.data != "END") {
                        stores[gnd_number].addJSON(e.data);
                        splitJSON(gnd_uri, gnd_number)(stores[gnd_number]);
                    }
                    else {
                        jsonStream.close();
                        console.log("All done. Closing stream.");
                    }
                }}(GLOBAL_GND[c], gnd_number)

                break;
            }
        }
    }

    /// ...
    /// ...
    /// ...
    /// ...
    /// ...
    /// ... splitJSON (render and substitute widget part)
    /// ...
    /// ...
    /// ...
    /// ...
    /// ...

    function MinStore () {
        // usage: var store = new MinStore();
        //        store.addJSON(data);
        //        ...
        //        splitJSON(store.triples);
        this.triples = {};
    }

    MinStore.prototype = {
        addJSON: function (triples) {
            for(var s in triples) {
                for(var p in triples[s]) {
                    var l = triples[s][p].length;
                    for(var i = 0; i < l; i++) {
                        this.addTriple(s, p, triples[s][p][i]);
                    }
                }
            }
            return this;
        },

        addTriple: function (s, p, o) {
            if (s in this.triples) {
                if (p in this.triples[s]) {
                    this.triples[s][p].push(o);
                }
                else {
                    this.triples[s][p] = [o];
                }
            }
            else {
                this.triples[s] = {};
                this.triples[s][p] = [o];
            }
        },

        getTriples: function() {
            return this.triples;
        }
    };

})();
