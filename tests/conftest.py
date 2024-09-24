import os
import pytest
from dotenv import find_dotenv, load_dotenv
from pywechat.client import WechatClient, AsyncWechatClient, MemoryCache


@pytest.fixture(scope="session")
def wechat_client():
    env_file = find_dotenv(".env.tests")
    load_dotenv(env_file)
    return WechatClient(
        os.getenv("APPID"),
        os.getenv("APPSECRET"),
        os.getenv("APPTOKEN"),
        os.getenv("ENCODING_AES_KEY"),
        MemoryCache(),
    )


@pytest.fixture(scope="session")
def async_wechat_client():
    env_file = find_dotenv(".env.tests")
    load_dotenv(env_file)
    return AsyncWechatClient(
        os.getenv("APPID"),
        os.getenv("APPSECRET"),
        os.getenv("APPTOKEN"),
        os.getenv("ENCODING_AES_KEY"),
        MemoryCache(),
    )
