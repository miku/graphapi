import requests
import json
import yaml

config_file = open('config.yaml', 'r')
config = yaml.load(config_file)

SPARQL_ENDPOINT = config["endpoint"]

# These should be moved to a separate yaml file to configure what
# kind of information the API will send back

props = [
    'http://d-nb.info/standards/elementset/gnd#placeOfBirth',
    'http://d-nb.info/standards/elementset/gnd#placeOfDeath',
    'http://d-nb.info/standards/elementset/gnd#dateOfBirth',
    'http://d-nb.info/standards/elementset/gnd#dateOfDeath',
    'http://www.w3.org/2000/01/rdf-schema#label',
    'http://xmlns.com/foaf/0.1/depiction'
]

# used for debugging and testing

GND = 'http://d-nb.info/gnd/%s'

gnds = {
    'goethe' : GND % '118540238',
    'twain' : GND % '118624822',
    'schiller': GND % '118607626'
}



def get_gnd_uri(gnd):
    return GND % gnd

# TODO:
# Generalize to pass an array of triple patterns from which a single query
# is generated

def fill_triple(s = None, p = None, o = None):
    subject = '?s' if s == None else '<%s>' % s
    pred = '?p' if p == None else '<%s>' % p
    obj = '?o' if o == None else '<%s>' % o

    query_template = '''
    DEFINE input:same-as "yes"
    DEFINE input:inference <gndrules>
    CONSTRUCT {{
        {s} {p} {o} .
    }}
    WHERE {{
        {s} {p} {o} .
    }}
    '''
    query = query_template.format(s=subject, p=pred, o=obj)
    return json.dumps(query_endpoint(query))

def query_endpoint(query):
    '''
    Retrieves a result set from a SPARQL query a dictionary
    '''
    r = requests.get(SPARQL_ENDPOINT,
                     headers={'accept': 'application/json'},
                     params={'query': query}
                     )
    j = json.loads(r.text)
    return j

#
# not yet used but implemented as possible blueprint
#

def paginate_query(query):
    limit = 1
    i = 0
    while(1):
        r = requests.get(SPARQL_ENDPOINT,
                         headers={
                            'accept': 'text/csv'
                            },
                         params={
                            'query': query + 'LIMIT %d OFFSET %d' % (limit, i*limit)
                         })
        yield(r.text)
        output = r.text[:-1]
        if i > 0:
           output = "\n".join(output.split("\n")[1:])

        if output != '':
           # print(output)
           pass
        else:
           break

        i += 1

def get_cluster(gnd):
    query = """
    DEFINE input:same-as "yes"
    DEFINE input:inference <gndrules>

    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX gndo: <http://d-nb.info/standards/elementset/gnd#>
    PREFIX gnd: <http://d-nb.info/gnd/>
    PREFIX kgl: <http://kg.ub.uni-leipzig.de/>

    SELECT DISTINCT ?k ?klabel ?kpic
    WHERE {{ 
        GRAPH <http://d-nb.info/gnd/> {{
           gnd:{gnd} gndo:placeOfBirth ?b .
           gnd:{gnd} gndo:professionOrOccupation ?p .
           ?k gndo:placeOfBirth ?b .
           ?k gndo:professionOrOccupation ?p .
           # gnd:{gnd} <http://d-nb.info/standards/elementset/gnd#acquaintanceshipOrFriendship> ?k .
           ?k rdfs:label ?klabel .
           OPTIONAL {{
               ?k foaf:depiction ?kpic .
           }}
        }}
    }}
    ORDER BY ?k ?klabel ?kpic
    """
    paginate_query(query.format(gnd = gnd))

