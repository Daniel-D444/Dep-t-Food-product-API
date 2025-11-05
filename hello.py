import requests
import json
from flask      import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
from markupsafe import escape

app = Flask(__name__)
CORS(app)

app.logger.setLevel("INFO")

API_TOKEN = "2597522b3emsh0cabcabdff55152p12fa39jsn13dfaadadc0e"
GOOGLE_NEWS_API_URL = "https://google-news22.p.rapidapi.com/v1"

@app.route("/")
def hello_world():

    tokenHeader = request.headers['Token']
    app.logger.info("the token is "+tokenHeader)

    text = "<html><head></head><body>"
    text += "<h1>Welcom to gateway</h1>"
    text += "<p>You are using the token: "+tokenHeader
    text += "<h2>GET /</h2>"
    text += "<p>This documentation</p>"
    text += "</body></html>"
    return text

@app.route("/news")
def get_google_news():
    response = {}
    args = "search?q=euro&country=us&language=en"
    g_response = requests.get(GOOGLE_NEWS_API_URL + "/" + args,
                              headers = {"x-rapidapi-key": API_TOKEN})
    
    if (g_response.status_code == 200):
        app.logger.info("Youpi")
        app.logger.info(g_response.text)
        response["body"] = json.loads(g_response.text)
    else :
        app.logger.error("Aie zut")
        response["status"] = "error. Api Google said :"+str(g_response.status_code)

    #response ["google_news"] = json.dumps(g_response, default=vars)

    return response
