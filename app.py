# coding: utf-8

from flask import Flask
from flask.ext.cors import CORS
import requests
import json
import pyphen

def extend(d1, d2):
    '''
    Simple extension of d1 with d2. It's assumed that d1 and d2 have disjoint
    keys. Otherwise, a more elaborate function would be needed.
    '''
    for k, i in d2.iteritems():
        d1[k] = i
    return d1

def hyphenate(text, lang='de'):
    # cf.: https://github.com/Kozea/Pyphen/tree/master/dictionaries
    lcodes = {
        'de' : 'de_DE' ,
        'en' : 'en_GB'
    }
    dic = pyphen.Pyphen(lang=lcodes[lang])

    hwords = []
    for word in text.split(" "):
        syl = []
        # slight work-around concercing already hyphenated words
        for parts in word.split("-"):
            h = dic.inserted(parts)
            h = h.replace('-', '&shy;')
            syl.append(h)
        hwords.append('-'.join(syl))
    return ' '.join(hwords)

def get_aux_json(lang = 'de'):
    try:
        f = open('i18n-%s.json' % lang, 'r')
    except:
        f = open('i18n-de.json', 'r')
    data = json.load(f)
    f.close()
    return data

def map_rec_dict(d, f, dict_cond = lambda x: True, key_cond = lambda x: True, process_values = True):
    '''
    A simple function that maps a function f recursively over the values
    of a given dictionary d. If the values of a key happen to be a list, the
    function f will be mapped over the values of the list. It is assumed that
    the values of this list are again dictionaries.

    Optionally takes a function dict_cond and key_cond.
    - values of a sub dictionary are only processed when dict_cond is
      True (but 'nested' dictionaries will be processed), additionally to the
      dict itself, the key pointing to the dict is also passed
    - values will only be processed when key_cond holds

    Returns a new dictionary.
    '''
    dp = {}
    for key, val in d.iteritems():
        if isinstance(val, dict):
            if dict_cond(key, val):
                dp[key] = map_rec_dict(val, f, dict_cond, key_cond, process_values = True)
            else:
                dp[key] = map_rec_dict(val, f, dict_cond, key_cond, process_values = False)
        elif isinstance(val, list):
            dp[key] = map(
                          lambda x:
                              map_rec_dict(x, f, dict_cond, key_cond, process_values = True)
                              if isinstance(x, dict) and dict_cond(key, x)
                              else
                                  map_rec_dict(x, f, dict_cond, key_cond, process_values = False)
                          ,
                          val
                      )
        else:
            dp[key] = f(val) if (key_cond(key) and process_values) else val
    return dp

def image_cache_link(uri):
    if uri[-4:] in ['.jpg', '.png']:
        return "http://172.18.113.6:5001/u?url=%s" % uri
    else:
        return uri

app = Flask(__name__)
app.config['SPARQL_ENDPOINT'] = 'http://localhost:8890/sparql'
cors = CORS(app)

QUERY = """
DEFINE input:same-as "yes"
DEFINE input:inference <gndrules>

PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX gndo: <http://d-nb.info/standards/elementset/gnd#>
PREFIX gnd: <http://d-nb.info/gnd/>
PREFIX kgl: <http://kg.ub.uni-leipzig.de/>

CONSTRUCT {{ 
    gnd:{gnd} <http://www.w3.org/2000/01/rdf-schema#label> ?j .
    gnd:{gnd} <http://xmlns.com/foaf/0.1/depiction> ?c .

    gnd:{gnd} kgl:born ?h .
    gnd:{gnd} kgl:bornIn ?e .

    gnd:{gnd} kgl:died ?i .
    gnd:{gnd} kgl:diedIn ?g .

    gnd:{gnd} kgl:cityCluster ?k .
    ?k <http://www.w3.org/2000/01/rdf-schema#label> ?klabel .
    ?k <http://xmlns.com/foaf/0.1/depiction> ?kpic .

    gnd:{gnd} kgl:profession ?l .
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

        OPTIONAL {{ 
            gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#acquaintanceshipOrFriendship> ?k .
            ?k <http://d-nb.info/standards/elementset/gnd#preferredNameForThePerson> ?klabel .
            # ?k rdfs:label ?klabel .
            OPTIONAL {{
                ?k foaf:depiction ?kpic .
            }}
        }}
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

@app.route("/gnd/<lang>/<gnd>")
@app.route("/gnd/<gnd>")
def q(gnd, lang='de'):
    r = requests.get(app.config['SPARQL_ENDPOINT'],
                     headers={'accept': 'application/json'},
                     params={'query': QUERY.format(gnd=gnd)})
    j = json.loads(r.text)
    j = map_rec_dict(
            j,
            image_cache_link,
            lambda k, d : 'type' in d and d['type'] == 'uri',
            lambda x : x == 'value'
        )
    j = map_rec_dict(
            j,
            lambda x: hyphenate(x),
            lambda k, d : k == 'http://www.w3.org/2000/01/rdf-schema#abstract',
            lambda x : x == 'value'
        )

    ja = get_aux_json(lang)
    j = extend(j, ja)

    #print("%s" % j)
    #return "<pre>%s</pre>" % r.text
    return json.dumps(j, sort_keys=True, indent=4)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
