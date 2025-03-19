from api.v1 import api_bp
from flask import Flask
import click

app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix='/api/v1')

app.route('/')(lambda: 'Hello World!')

if __name__ == '__main__':
   app.run(debug=True)