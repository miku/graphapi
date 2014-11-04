# coding: utf-8

from flask import Flask
import requests
import json

app = Flask(__name__)
app.config['SPARQL_ENDPOINT'] = 'http://localhost:18890/sparql'

QUERY = """

CONSTRUCT {{ 
    <http://d-nb.info/gnd/{gnd}> <http://xmlns.com/foaf/0.1/depiction> ?c .

    <http://d-nb.info/gnd/{gnd}> <http://example.org/kg#bornIn> ?e .
    <http://d-nb.info/gnd/{gnd}> <http://example.org/kg#diedIn> ?g .

    <http://d-nb.info/gnd/{gnd}> <http://example.org/kg#born> ?h .
    <http://d-nb.info/gnd/{gnd}> <http://example.org/kg#died> ?i .

    <http://example.org/kg#diedIn> <rdfs:label> "gestorben in"@de . 
    <http://example.org/kg#diedIn> <rdfs:label> "died in"@en . 

    <http://d-nb.info/gnd/{gnd}> <rdfs:label> ?j .
    <http://d-nb.info/gnd/{gnd}> <http://example.org/kg#cityCluster> ?k .
    ?k <rdfs:label> ?klabel .
    ?k <http://xmlns.com/foaf/0.1/depiction> ?k_dbp .

    <http://d-nb.info/gnd/{gnd}> <http://example.org/kg#profession> ?l .
    <http://d-nb.info/gnd/{gnd}> <http://www.w3.org/2000/01/rdf-schema#abstract> ?comment .
}}
WHERE {{ 
    GRAPH <http://d-nb.info/gnd/> {{
        OPTIONAL {{
            <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#placeOfBirth> ?d .
            ?d <http://d-nb.info/standards/elementset/gnd#preferredNameForThePlaceOrGeographicName> ?e .
        }}

        OPTIONAL {{
            <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#placeOfDeath> ?f .
            ?f <http://d-nb.info/standards/elementset/gnd#preferredNameForThePlaceOrGeographicName> ?g .
        }}

        OPTIONAL {{
            <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#dateOfBirth> ?h .
        }}

        OPTIONAL {{
            <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#dateOfDeath> ?i .
        }}

        OPTIONAL {{
            <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#preferredNameForThePerson> ?j .
        }}


        OPTIONAL {{
            <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#professionOrOccupation> ?l .
        }}

        {{ SELECT ?k ?klabel ?kpic ?k_dbp WHERE {{
            OPTIONAL {{ 
                <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#placeOfBirth> ?d .
                <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#professionOrOccupation> ?l .

                ?k <http://d-nb.info/standards/elementset/gnd#placeOfBirth> ?d .
                ?k <http://d-nb.info/standards/elementset/gnd#preferredNameForThePerson> ?klabel . 

                ?k <http://d-nb.info/standards/elementset/gnd#professionOrOccupation> ?l .
                ?k <http://d-nb.info/standards/elementset/gnd#preferredNameForThePerson> ?klabel . 

                # Getting the picture
                # This will blow up the query too much
                # OPTIONAL {{
                #     GRAPH <http://d-nb.info/gnd/> {{
                #         ?k <http://www.w3.org/2002/07/owl#sameAs> ?k_dbp .
                #         FILTER(regex(?k_dbp, 'dbpedia'))
                #     }}
                #
                #     GRAPH <http://dbpedia.org/resource/> {{
                #         ?k_dpb <http://xmlns.com/foaf/0.1/depiction> ?kpic .
                #     }}
                # }}
            }}
           }} LIMIT 6
        }}

    }}

    OPTIONAL {{
        GRAPH <http://d-nb.info/gnd/> {{
            <http://d-nb.info/gnd/{gnd}> <http://www.w3.org/2002/07/owl#sameAs> ?b .
        }}

        GRAPH <http://dbpedia.org/resource/> {{
            ?b <http://xmlns.com/foaf/0.1/depiction> ?c .

            OPTIONAL {{
                ?b_german <http://www.w3.org/2002/07/owl#sameAs> ?b .
                ?b_german <http://www.w3.org/2000/01/rdf-schema#comment> ?comment .
            }}
        }}
    }}
}}

"""

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/gnd/<gnd>")
def q(gnd):
    r = requests.get(app.config['SPARQL_ENDPOINT'],
                     headers={'accept': 'application/json'},
                     params={'query': QUERY.format(gnd=gnd)})
    #j = json.loads(r.text)
    #print("%s" % j)
    #return "<pre>%s</pre>" % r.text
    return r.text

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
