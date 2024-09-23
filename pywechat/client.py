import logging
import time
import hashlib
import socket
import struct
import secrets
import xmltodict
from httpx import AsyncClient, Client
import base64
from typing import Optional, Union, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from .models.message import (
    EncryptedResponseMessage,
    EncryptedRequestMessage,
    GenericMessage,
    Message,
)


logger = logging.getLogger(__name__)


class BaseCache:
    def get(self, key: str) -> Tuple[Optional[str], Optional[int]]:
        raise NotImplementedError

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        raise NotImplementedError

    async def aget(self, key: str) -> Tuple[Optional[str], Optional[int]]:
        raise NotImplementedError

    async def aset(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        raise NotImplementedError


class MemoryCache(BaseCache):
    def __init__(self):
        self._cache: dict[str, str] = {}
        self._expiry: dict[str, int] = {}

    def get(self, key: str) -> Tuple[Optional[str], Optional[int]]:
        if key in self._expiry and self._expiry[key] < time.time():
            del self._cache[key]
            del self._expiry[key]
            return None, None
        return self._cache.get(key), self._expiry.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._cache[key] = value
        if ex is not None:
            self._expiry[key] = time.time() + ex
        return True

    async def aget(self, key: str) -> Tuple[Optional[str], Optional[int]]:
        return self.get(key)

    async def aset(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        return self.set(key, value, ex)


class BaseWechatClient:
    def __init__(
        self,
        appid: str,
        app_secret: str,
        app_token: str,
        encoding_aes_key: str,
        cache: BaseCache,
    ):
        self._appid = appid
        self._app_secret = app_secret
        self._app_token = app_token
        self._encoding_aes_key = encoding_aes_key
        self._encoded_key = base64.b64decode(encoding_aes_key + "=")
        self._chipper = Cipher(
            algorithms.AES(self._encoded_key), modes.CBC(self._encoded_key[:16])
        )
        self._cache = cache
        self._request_client: Union[Client, AsyncClient]

    def request(self, method: str, url: str, **kwargs):
        raise NotImplementedError

    def generate_signature(self, timestamp: str, nonce: str, encrypt: str):
        data = [self._app_token, timestamp, nonce, encrypt]
        data.sort()
        sha1 = hashlib.sha1()
        sha1.update("".join(data).encode())
        return sha1.hexdigest()

    def check_signature(
        self, signature: str, timestamp: str, nonce: str, encrypt: Optional[str] = None
    ):
        data = [self._app_token, timestamp, nonce]
        if encrypt is not None:
            data.append(encrypt)
        data.sort()
        sha1 = hashlib.sha1()
        sha1.update("".join(data).encode())
        if sha1.hexdigest() == signature:
            return True
        return False

    def decrypt_message(
        self, encrypt_message: EncryptedRequestMessage
    ) -> GenericMessage:
        decryptor = self._chipper.decryptor()
        plain_text = (
            decryptor.update(encrypt_message.Encrypt.encode("utf-8"))
            + decryptor.finalize()
        )
        padding = plain_text[-1]
        content = plain_text[16:-padding]
        xml_length = socket.ntohl(struct.unpack(b"I", content[:4])[0])
        xml_content = (content[4 : xml_length + 4]).decode("utf-8")
        from_appid = (content[xml_length + 4 :]).decode("utf-8")
        if from_appid != self._appid:
            raise Exception("Invalid AppID")
        return GenericMessage.model_validate(self.xml_to_message(xml_content))

    def pkcs7_padding(self, data: bytes) -> bytes:
        if not isinstance(data, bytes):
            data = data.encode()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    def encrypt_message(self, message: Message) -> EncryptedResponseMessage:
        text = self.message_to_xml(message).encode("utf-8")
        tmp_list = []
        tmp_list.append(secrets.token_bytes(16))
        length = struct.pack(b"I", socket.htonl(len(text)))
        tmp_list.append(length)
        tmp_list.append(text)
        tmp_list.append(self._appid.encode("utf-8"))

        encryptor = self._chipper.encryptor()

        ciphertext = (
            encryptor.update(self.pkcs7_padding(b"".join(tmp_list)))
            + encryptor.finalize()
        )
        encrypt = base64.b64encode(ciphertext).decode("utf-8")
        timestamp = str(time.time())
        nonce = secrets.token_urlsafe(16)
        signature = self.generate_signature(timestamp, nonce, encrypt)
        return EncryptedResponseMessage(
            Encrypt=encrypt,
            MsgSignature=signature,
            TimeStamp=timestamp,
            Nonce=nonce,
        )

    def message_to_xml(self, message: Message) -> str:
        logger.debug(f"Converting message to XML: {message}")
        return xmltodict.unparse({"xml": message.model_dump(exclude_none=True)})

    def xml_to_message(self, xml: str) -> GenericMessage:
        logger.debug(f"Converting XML to message: {xml}")
        return GenericMessage.model_validate(xmltodict.parse(xml).get("xml"))


class WechatClient(BaseWechatClient):
    def __init__(
        self,
        appid: str,
        app_secret: str,
        app_token: str,
        encoding_aes_key: str,
        cache: BaseCache = MemoryCache(),
    ):
        super().__init__(appid, app_secret, app_token, encoding_aes_key, cache)
        self._request_client: Client = Client()

    def request(self, method: str, url: str, **kwargs):
        if "params" not in kwargs:
            kwargs["params"] = {}
        kwargs["params"]["access_token"] = self.get_access_token()
        return self._request_client.request(method, url, **kwargs)

    def get_access_token(self) -> str:
        cached_token, expire_time = self._cache.get(self._appid)
        if expire_time is not None and expire_time < int(time.time() + 60 * 5):
            return self.refresh_access_token()
        if cached_token is not None:
            return cached_token
        else:
            return self.refresh_access_token()

    def refresh_access_token(self):
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self._appid,
            "secret": self._app_secret,
        }
        response = self._request_client.request("GET", url, params=params)
        if response.status_code != 200:
            logger.error(f"Failed to get access token: {response.text}")
            raise Exception("Failed to get access token")
        data = response.json()
        if "errcode" in data:
            logger.error(f"Failed to get access token: {data}")
            raise Exception("Failed to get access token")
        self._cache.set(self._appid, data["access_token"], ex=int(data["expires_in"]))
        return data["access_token"]


class AsyncWechatClient(BaseWechatClient):
    def __init__(
        self,
        appid: str,
        app_secret: str,
        app_token: str,
        encoding_aes_key: str,
        cache: BaseCache = MemoryCache(),
    ):
        super().__init__(appid, app_secret, app_token, encoding_aes_key, cache)
        self._request_client: AsyncClient = AsyncClient()

    async def request(self, method: str, url: str, **kwargs):
        if "params" not in kwargs:
            kwargs["params"] = {}
        kwargs["params"]["access_token"] = await self.get_access_token()
        return await self._request_client.request(method, url, **kwargs)

    async def get_access_token(self) -> str:
        cached_token, expire_time = await self._cache.aget(self._appid)
        if expire_time is not None and expire_time < int(time.time() + 60 * 5):
            return await self.refresh_access_token()
        if cached_token is not None:
            return cached_token
        else:
            return await self.refresh_access_token()

    async def refresh_access_token(self):
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self._appid,
            "secret": self._app_secret,
        }
        logger.debug(f"Getting access token: {url} {params}")
        response = await self._request_client.request("GET", url, params=params)
        if response.status_code != 200:
            logger.error(f"Failed to get access token: {response.text}")
            raise Exception("Failed to get access token")
        data = response.json()
        if "errcode" in data:
            logger.error(f"Failed to get access token: {data}")
            raise Exception(f"Failed to get access token: {data}")
        await self._cache.aset(
            self._appid, data["access_token"], ex=int(data["expires_in"])
        )
        return data["access_token"]
