import os
import dotenv

dotenv.load_dotenv()

CWD = os.getcwd()
BUPT_USERNAME=os.getenv("BUPT_USERNAME")
BUPT_PASSWORD=os.getenv("BUPT_PASSWORD")
API_KEY_DOUBAO = os.getenv("API_KEY_DOUBAO")
MODEL_END_POINT_ID_DOUBAO = os.getenv("MODEL_END_POINT_ID_DOUBAO")
DESCRIPTION = ""
EXAMPLE = ""
BARK_TOKEN = ""
CATEGORY = ["学术","活动","通知","政务","娱乐","其他"]
DEFAULT_BATCH_SIZE = 20