from bs4 import BeautifulSoup
import requests, dotenv, os

dotenv.load_dotenv()

class CAS:
    _history_session = []

    def __init__(self, username = None, password = None):
        if len(self._history_session) == 0:
            if username is None:
                username = os.getenv("BUPT_USERNAME")
            if password is None:
                password = os.getenv("BUPT_PASSWORD")
            self.username = username
            self.password = password
            self.url = "https://auth.bupt.edu.cn/authserver/login"
            try:
                self._login()
            except requests.HTTPError as e:
                if e.response.status_code not in [401, 423]:
                    raise e
                self.status = False
            else:
                self.status = True
            print("New session created")
        else:
            self.session = self._history_session[-1]
            print("Reusing session")

    def _get_session(self):
        session = requests.Session()
        session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        return session

    def _login(self):
        self.session = self._get_session()
        resp = self.session.get(url=self.url)
        varid = BeautifulSoup(
            resp.text, "lxml"
        ).find(attrs={"name": "execution"})["value"]
        post_data = {
            "username": self.username,
            "password": self.password,
            "type": "username_password",
            "submit": "LOGIN",
            "_eventId": "submit",
            "execution": varid
        }
        resp = self.session.post(url=self.url, data=post_data)
        resp.raise_for_status()
        self._history_session.append(self.session)

    # redirect all undefined methods to self.session
    def __getattr__(self, name):
        attr = getattr(self.session, name)
        if callable(attr):
            return attr.__get__(self.session, type(self.session))
        else:
            return attr