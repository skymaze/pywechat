import logging
from fastapi import APIRouter
from ..wechat import wechat_client


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/access_token")
async def get_access_token():
    return await wechat_client.get_access_token()
