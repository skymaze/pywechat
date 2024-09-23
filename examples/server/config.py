import os
from dotenv import load_dotenv


load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "PyWechat Server")
DOCS_URL = "/docs"
APPID = os.getenv("APPID")
APPSECRET = os.getenv("APPSECRET")
APPTOKEN = os.getenv("APPTOKEN")
ENCODING_AES_KEY = os.getenv("ENCODING_AES_KEY")
