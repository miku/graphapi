# coding: utf-8

from flask import Flask
import json
import requests

app = Flask(__name__)

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

    <http://d-nb.info/gnd/{gnd}> <http://example.org/kg#profession> ?l .
}}
WHERE {{ 
    GRAPH <http://d-nb.info/gnd/> {{
        OPTIONAL {{
            <http://d-nb.info/gnd/{gnd}> <http://www.w3.org/2002/07/owl#sameAs> ?b .
        }}

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

        {{ SELECT ?k ?klabel ?kpic WHERE {{
            OPTIONAL {{ 
                <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#placeOfBirth> ?d .
                <http://d-nb.info/gnd/{gnd}> <http://d-nb.info/standards/elementset/gnd#professionOrOccupation> ?l .

                ?k <http://d-nb.info/standards/elementset/gnd#placeOfBirth> ?d .
                ?k <http://d-nb.info/standards/elementset/gnd#preferredNameForThePerson> ?klabel . 

                ?k <http://d-nb.info/standards/elementset/gnd#professionOrOccupation> ?l .
                ?k <http://d-nb.info/standards/elementset/gnd#preferredNameForThePerson> ?klabel . 
            }} }} LIMIT 5 
        }}
    }}

    GRAPH <http://dbpedia.org/resource/> {{
        ?b <http://xmlns.com/foaf/0.1/depiction> ?c .
    }}
}}
"""

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/gnd/<gnd>")
def q(gnd):
    r = requests.get('http://localhost:18890/sparql', headers={'accept': 'application/json'}, params={'query': QUERY.format(gnd=gnd)})
    return "<pre>%s</pre>" % r.text

if __name__ == "__main__":
    app.run(debug=True)
