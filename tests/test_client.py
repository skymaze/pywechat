import pytest
from pywechat.client import WechatClient, AsyncWechatClient
from pywechat.models.message import (
    GenericMessage,
    TextMessage,
    EncryptedResponseMessage,
    EventType,
    MessageType,
)


def test_get_access_token(wechat_client: WechatClient):
    access_token = wechat_client.get_access_token()
    assert access_token is not None
    assert isinstance(access_token, str)


@pytest.mark.asyncio
async def test_async_get_access_token(async_wechat_client: AsyncWechatClient):
    access_token = await async_wechat_client.get_access_token()
    assert access_token is not None
    assert isinstance(access_token, str)


def test_generate_signature(wechat_client: WechatClient):
    signature = wechat_client.generate_signature("1727185580", "nonce")
    assert signature is not None
    assert isinstance(signature, str)


def test_check_signature(wechat_client: WechatClient):
    assert wechat_client.check_signature(
        "9bbb8b7d8ce841bfe8a59a6db5fc37647ebe4a53", "1727186898", "1313055186"
    )
    assert not wechat_client.check_signature(
        "9bbb8b7d8ce841bfe8a59a6db5fc37647ebe4a53", "1727185580", "invalid_nonce"
    )


def test_generate_encrypted_message_signature(wechat_client: WechatClient):
    signature = wechat_client.generate_signature("1727185580", "nonce", "encrypt")
    assert signature is not None
    assert isinstance(signature, str)


def test_check_encrypted_message_signature(wechat_client: WechatClient):
    signature = wechat_client.generate_signature("1727185580", "nonce", "encrypt")
    assert wechat_client.check_signature(signature, "1727185580", "nonce", "encrypt")
    assert not wechat_client.check_signature(
        signature, "1727185580", "invalid_nonce", "encrypt"
    )
    assert not wechat_client.check_signature(
        signature, "1727185580", "nonce", "invalid_encrypt"
    )


def test_encrypt_text_message(wechat_client: WechatClient):
    message = TextMessage(
        ToUserName="to_user_name",
        FromUserName="from_user_name",
        CreateTime=123456789,
        MsgType="text",
        Content="content",
    )
    encrypted_message = wechat_client.encrypt_message(message)
    assert encrypted_message is not None
    assert isinstance(encrypted_message, EncryptedResponseMessage)


def test_xml_to_message(wechat_client: WechatClient):
    xml_message = "<xml><ToUserName><![CDATA[gh_399908c3505e]]></ToUserName>\n<FromUserName><![CDATA[oIqny6t2aR0L7dhDHr6qkm27kvxA]]></FromUserName>\n<CreateTime>1727187078</CreateTime>\n<MsgType><![CDATA[event]]></MsgType>\n<Event><![CDATA[unsubscribe]]></Event>\n<EventKey><![CDATA[]]></EventKey>\n</xml>" # noqa
    message = wechat_client.xml_to_message(xml_message)
    assert message is not None
    assert isinstance(message, GenericMessage)
    assert message.ToUserName == "gh_399908c3505e"
    assert message.FromUserName == "oIqny6t2aR0L7dhDHr6qkm27kvxA"
    assert message.CreateTime == 1727187078
    assert message.MsgType == "event"
    assert message.Event == EventType.UNSUBSCRIBE
    assert message.EventKey is None


def test_message_to_xml(wechat_client: WechatClient):
    message = TextMessage(
        ToUserName="oIqny6t2aR0L7dhDHr6qkm27kvxA",
        FromUserName="gh_399908c3505e",
        CreateTime=1727188435,
        MsgType=MessageType.TEXT,
        Content="Received text message: hello",
    )
    xml_message = wechat_client.message_to_xml(message)
    assert xml_message is not None
    assert isinstance(xml_message, str)
    assert (
        xml_message
        == "<xml><ToUserName>oIqny6t2aR0L7dhDHr6qkm27kvxA</ToUserName><FromUserName>gh_399908c3505e</FromUserName><CreateTime>1727188435</CreateTime><MsgType>text</MsgType><Content>Received text message: hello</Content></xml>" # noqa
    )
