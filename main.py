from api.v1 import api_bp
from flask import Flask
from subthread import *

# Start the crawlers threads
start_crawlers_threads()

# Start the notification thread
notification_thread = NotificationThread()
notification_thread.start_loop()

# Start the flask app
app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix='/api/v1')

app.route('/')(lambda: 'Hello World!')

app.run(debug=True)