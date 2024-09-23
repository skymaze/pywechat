import logging
from pywechat.client import AsyncWechatClient, MemoryCache
from .config import APPID, APPSECRET, APPTOKEN, ENCODING_AES_KEY


logger = logging.getLogger(__name__)


logger.debug(f"Initializing Wechat Client with APPID={APPID}, {APPSECRET}, {APPTOKEN}")
wechat_client = AsyncWechatClient(
    APPID, APPSECRET, APPTOKEN, ENCODING_AES_KEY, MemoryCache()
)
