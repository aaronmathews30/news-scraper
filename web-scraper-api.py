from flask import Flask, request
from flask.json import jsonify
from werkzeug.exceptions import HTTPException
from Base.api_exception import APIException, CustomException, FailureException
from Base.api_response import APIResponse
import webscraper
app = Flask(__name__)


@app.route('/scrape', methods=['POST'])
def scrape_news():
    content = request.json

    url = content.get('url')
    
    m_dict = {'message': webscraper.web_scraper(url)}
    return jsonify(m_dict)

 
@app.errorhandler(Exception)
def flask_error(e):
    if isinstance(e, APIException):
        return e
    if isinstance(e, HTTPException):
        code = e.code
        msg = e.description
        return APIException({}, code, msg)
    else:
        if not app.config['DEBUG']:
            return "1"
        else:
            return e

if __name__ == '__main__':
    app.run(debug=True)
