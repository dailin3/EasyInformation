import os
import dotenv

dotenv.load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
CWD = os.getcwd()
BUPT_USERNAME=os.getenv("BUPT_USERNAME")
BUPT_PASSWORD=os.getenv("BUPT_PASSWORD")
API_KEY_DOUBAO = os.getenv("API_KEY_DOUBAO")
MODEL_END_POINT_ID_DOUBAO = os.getenv("MODEL_END_POINT_ID_DOUBAO")
DESCRIPTION = "一位热爱技术的学生，软件工程专业大一，住在S2楼，不喜欢一些学校政务相关的事，最近希望知道沙河校医院啥时候可以报销"
EXAMPLE = "技术社团招新 学术讲座 S2楼通知 软件工程专业大一通知"
BARK_TOKEN = os.getenv("BARK_TOKEN")
CATEGORY = ["学术","活动","通知","政务","娱乐","其他"]
DEFAULT_BATCH_SIZE = 10
CHROME_DRIVER_PATH = os.path.join(CWD, "chromedriver")
NOTIFICATION_INTERVAL = 60