from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# ------------------ 配置 ------------------
SERVICE_ACCOUNT_FILE = "enerogo-firebase-adminsdk-kgd62-1f39ab9ab5.json"
PACKAGE_NAME = "com.zhichengcloud.power"

# 初始化 FastAPI
app = FastAPI(title="Play Integrity Token Decoder")

# 请求 body 模型
class TokenRequest(BaseModel):
    integrityToken: str

# ------------------ API 接口 ------------------
@app.post("/decode-token")
def decode_token(request: TokenRequest):
    try:
        # 创建 service account 凭证
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/playintegrity"]
        )

        # 刷新 token
        credentials.refresh(Request())
        access_token = credentials.token

        # 调用 Google Play Integrity API
        url = f"https://playintegrity.googleapis.com/v1/{PACKAGE_NAME}:decodeIntegrityToken"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        body = {"integrityToken": request.integrityToken}

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            payload = response.json()
            return {"success": True, "data": payload}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
