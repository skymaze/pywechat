# Tests

## Prerequisites
- [进入微信公众账号测试号申请系统](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
- set environment variables
  - `WECHAT_APPID`
  - `WECHAT_APPSECRET`
  - `WECHAT_TOKEN`
  - `WECHAT_AES_KEY`
- or create a `.env.tests` file
  ```
  WECHAT_APPID=your_appid
  WECHAT_APPSECRET=your_appsecret
  WECHAT_TOKEN=your_token
  WECHAT_AES_KEY=your_aes_key
  ```

## Run
```bash
pytest
```