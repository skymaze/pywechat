import logging
import time
from fastapi import APIRouter, Request, Response
from pywechat.models.message import MessageType
from pywechat.models.message import GenericEvent, TextMessage

from ..wechat import wechat_client


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def push_test(signature: str, timestamp: str, nonce: str, echostr: str):
    if wechat_client.check_signature(signature, timestamp, nonce):
        if echostr:
            return Response(content=echostr)
        else:
            return Response(content="success")
    return Response(content="Invalid Signature", status_code=400)


@router.post("")
async def push(
    request: Request,
    signature: str,
    timestamp: str,
    nonce: str,
    msg_signature: str | None = None,
):
    if wechat_client.check_signature(signature, timestamp, nonce):
        xml_message = await request.body()
        logger.debug(f"Received message: {xml_message}")
        message = wechat_client.xml_to_message(xml_message)
        logger.debug(f"Received message: {message}")
        if message.Encrypt is not None:
            if wechat_client.check_signature(
                msg_signature, timestamp, nonce, message.Encrypt
            ):
                decrypted_message = wechat_client.decrypt_message(message.Encrypt)
                if decrypted_message.MsgType == MessageType.EVENT:
                    event_message = GenericEvent.model_validate(decrypted_message)
                    logger.debug(f"Received event message: {event_message}")
                    text_message = TextMessage(
                        ToUserName=event_message.FromUserName,
                        FromUserName=event_message.ToUserName,
                        CreateTime=int(time.time()),
                        MsgType=MessageType.TEXT,
                        content=f"Received encrypted event message: {event_message.Event}",
                    )
                    return Response(
                        content=wechat_client.message_to_xml(
                            wechat_client.encrypt_message(text_message)
                        ),
                        media_type="application/xml",
                    )
                return Response(content="success")
        if message.MsgType == MessageType.EVENT:
            event_message = GenericEvent.model_validate(
                message.model_dump(exclude_none=True, by_alias=True)
            )
            logger.debug(f"Received event message: {event_message}")
            text_message = TextMessage(
                ToUserName=event_message.FromUserName,
                FromUserName=event_message.ToUserName,
                CreateTime=int(time.time()),
                MsgType=MessageType.TEXT,
                Content=f"Received event message: {event_message.Event}",
            )
            return wechat_client.message_to_xml(text_message)
        return Response(content="success")
    return Response(content="Invalid Signature", status_code=400)
