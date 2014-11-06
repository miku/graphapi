# coding: utf-8

from flask import Flask
from flask.ext.cors import CORS
import requests
import json

app = Flask(__name__)
app.config['SPARQL_ENDPOINT'] = 'http://localhost:18890/sparql'
cors = CORS(app)

QUERY = """
DEFINE input:same-as "yes"
DEFINE input:inference <gndrules>

PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX gndo: <http://d-nb.info/standards/elementset/gnd#>
PREFIX gnd: <http://d-nb.info/gnd/>

CONSTRUCT {{ 
    gnd:{gnd} <http://xmlns.com/foaf/0.1/depiction> ?c .

    gnd:{gnd} <http://example.org/kg#bornIn> ?e .
    gnd:{gnd} <http://example.org/kg#diedIn> ?g .

    gnd:{gnd} <http://example.org/kg#born> ?h .
    gnd:{gnd} <http://example.org/kg#died> ?i .

    <http://example.org/kg#diedIn> <http://www.w3.org/2000/01/rdf-schema#label> "gestorben in"@de . 
    <http://example.org/kg#diedIn> <http://www.w3.org/2000/01/rdf-schema#label> "died in"@en . 

    gnd:{gnd} <http://www.w3.org/2000/01/rdf-schema#label> ?j .
    gnd:{gnd} <http://example.org/kg#cityCluster> ?k .
    ?k <http://www.w3.org/2000/01/rdf-schema#label> ?klabel .
    ?k <http://xmlns.com/foaf/0.1/depiction> ?kpic .

    gnd:{gnd} <http://example.org/kg#profession> ?l .
    ?l <http://www.w3.org/2000/01/rdf-schema#label> ?l_label .
    gnd:{gnd} <http://www.w3.org/2000/01/rdf-schema#abstract> ?comment .
}}
WHERE {{ 
    GRAPH <http://d-nb.info/gnd/> {{
        OPTIONAL {{
            gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#placeOfBirth> ?d .
            ?d rdfs:label ?e .
        }}

        OPTIONAL {{
            gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#placeOfDeath> ?f .
            ?f rdfs:label ?g .
        }}

        OPTIONAL {{
            gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#dateOfBirth> ?h .
        }}

        OPTIONAL {{
            gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#dateOfDeath> ?i .
        }}

        OPTIONAL {{
            gnd:{gnd} rdfs:label ?j .
        }}


        OPTIONAL {{
            gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#professionOrOccupation> ?l .
            OPTIONAL {{
                ?l rdfs:label ?l_label .
            }}
        }}

        {{ SELECT ?k ?klabel
           WHERE {{
               OPTIONAL {{ 
                    gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#placeOfBirth> ?d .
                    gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#professionOrOccupation> ?l .

                    ?k <http://d-nb.info/standards/elementset/gnd#placeOfBirth> ?d .
                    ?k rdfs:label ?klabel .

                    ?k <http://d-nb.info/standards/elementset/gnd#professionOrOccupation> ?l .
                    ?k rdfs:label ?klabel .

                }}
           }} LIMIT 6
        }}


    }}

    OPTIONAL {{
        ?k foaf:depiction ?kpic .
    }}

    OPTIONAL {{
        gnd:{gnd} foaf:depiction ?c .
    }}

    OPTIONAL {{
        gnd:{gnd} <http://www.w3.org/2000/01/rdf-schema#comment> ?comment .
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
