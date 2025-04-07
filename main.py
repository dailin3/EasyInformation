from api.v1 import api_bp
from flask import Flask
from subthread import *

# judge if the script is first runing
if __name__ == "__main__":

    first_run = False

    if not os.path.exists(os.path.join(os.path.join(config.CWD, "db"),"main.db")):
        # create the database
        database.connect()
        database.create_tables([Info, Assignments,Notifications])
        database.close()
        print("Database created successfully.")
        first_run = True

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