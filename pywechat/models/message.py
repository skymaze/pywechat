from enum import Enum
from typing import List, Union
from pydantic import BaseModel


class EncryptedRequestMessage(BaseModel):
    ToUserName: str
    Encrypt: str


class EncryptedResponseMessage(BaseModel):
    Encrypt: str
    MsgSignature: str
    TimeStamp: str
    Nonce: str


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    MUSIC = "music"
    ARTICLE = "news"
    EVENT = "event"


class BaseMessage(BaseModel):
    ToUserName: str
    FromUserName: str
    CreateTime: int
    MsgType: MessageType


class TextMessage(BaseMessage):
    Content: str


class ImageDetail(BaseModel):
    MediaId: str


class ImageMessage(BaseMessage):
    Image: ImageDetail


class VoiceDetail(BaseModel):
    MediaId: str


class VoiceMessage(BaseMessage):
    Voice: VoiceDetail


class VideoDetail(BaseModel):
    MediaId: str
    Title: str
    Description: str


class VideoMessage(BaseMessage):
    Video: VideoDetail


class MusicDetail(BaseModel):
    Title: str
    Description: str
    MusicUrl: str
    HQMusicUrl: str
    ThumbMediaId: str


class MusicMessage(BaseMessage):
    Music: MusicDetail


class ArticleDetail(BaseModel):
    Title: str
    Description: str
    PicUrl: str
    Url: str


class ArticleList(BaseModel):
    item: List[ArticleDetail]


class ArticleMessage(BaseMessage):
    ArticleCount: int
    Articles: ArticleList


class EventType(str, Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    SCAN = "SCAN"
    LOCATION = "LOCATION"
    CLICK = "CLICK"
    VIEW = "VIEW"


class BaseEvent(BaseMessage):
    # https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_event_pushes.html
    Event: EventType


class SubscribeEvent(BaseEvent):
    # 关注事件 subscribe
    EventKey: str | None = None
    Ticket: str | None = None


class UnsubscribeEvent(BaseEvent):
    # 取消关注事件 unsubscribe
    pass


class ScanEvent(BaseEvent):
    # 扫描带参数二维码事件 SCAN
    EventKey: str
    Ticket: str


class LocationEvent(BaseEvent):
    # 上报地理位置事件 LOCATION
    Latitude: float
    Longitude: float
    Precision: float


class ClickEvent(BaseEvent):
    # 点击菜单拉取消息时的事件推送 CLICK
    EventKey: str


class ViewEvent(BaseEvent):
    # 点击菜单跳转链接时的事件推送 VIEW
    EventKey: str


class GenericEvent(BaseEvent):
    Event: EventType
    EventKey: str | None = None
    ticket: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    precision: float | None = None


class GenericMessage(GenericEvent):
    FromUserName: str | None = None
    CreateTime: int | None = None
    MsgType: MessageType | None = None
    Content: str | None = None
    Image: ImageDetail | None = None
    Voice: VoiceDetail | None = None
    Video: VideoDetail | None = None
    Music: MusicDetail | None = None
    ArticleCount: int | None = None
    Articles: ArticleList | None = None
    Encrypt: str | None = None
    MsgSignature: str | None = None
    TimeStamp: str | None = None
    Nonce: str | None = None


Event = Union[
    SubscribeEvent,
    UnsubscribeEvent,
    ScanEvent,
    LocationEvent,
    ClickEvent,
    ViewEvent,
    GenericEvent,
]

Message = Union[
    TextMessage,
    ImageMessage,
    VoiceMessage,
    VideoMessage,
    MusicMessage,
    ArticleMessage,
    GenericMessage,
]
