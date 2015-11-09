__author__ = 'benjamin ahlbrand'

from bottle import Bottle, run, request, response, static_file, json_dumps
import NLPManager

app = Bottle()
nlp = NLPManager.getInstance()


@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route('/expand_filter/<terms>', method='GET')
def query(terms):
    """
    Expected input for terms is term1&term2&term3&...&termN

    returns json dictionary of arrays of expanded terms related to input
    """
    terms = terms.split('&')
    rst = dict()

    for term in terms:
        rst[term] = []
        for s in nlp.gen_forms(term, float(app.config['app.threshold'])):
            ret = [t[0] for t in s['terms']]
            for r in ret:
                if r not in rst[term]:
                    rst[term].append(r)

    response.content_type = 'application/json'
    return json_dumps(rst, indent=2)


app.config.load_config('conf.ini')
run(app, host=app.config['app.host'], port=app.config['app.port'], debug=True, reloader=True)
