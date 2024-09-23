# Wechat Examples Server

This is a simple server that demonstrates how to use the Wechat API.

# Tools
- [消息推送测试](https://developers.weixin.qq.com/apiExplorer?type=messagePush)

# Run

Create .env file or set environment variables.

```bash
uvicorn server.main:app --reload --log-config server/log_config_dev.yaml --host 0.0.0.0 --port 8000
```