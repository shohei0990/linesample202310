import os 
from dotenv import load_dotenv 
import json
import tempfile
import uvicorn
from fastapi import FastAPI, Depends, Request, HTTPException
from pydantic import BaseModel
from typing import List
from linebot import (LineBotApi, WebhookHandler, WebhookParser)
from linebot.models import (MessageEvent, ImageMessage, TextMessage, TextSendMessage,)
from linebot.exceptions import (InvalidSignatureError)
import urllib.request
from urllib.error import HTTPError
import requests
from linebot.models import ImageSendMessage
from PIL import Image, ImageDraw, ImageFont
import qrcode

# Azure連携
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Azureの設定
connection_string = ""
container_name = "barcode"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# 追加
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image

# LINE Botのシークレットとアクセストークン
# LINE Bot APIとWebhookHandlerをインスタンス化します。
# LINE Bot APIは、LINEのメッセージを送受信するためのAPIを提供します。
# WebhookHandlerは、Webhookからのイベントを処理するためのクラスです。
CHANNEL_SECRET = "b908ab9e7e3a40fdd1247dfc5e51d32c"
CHANNEL_ACCESS_TOKEN = ""
CLIENT_ID   = '5e439cffec5166f' 


# FastAPIをインスタンス化
app = FastAPI()

# LINE Bot APIを使うためのクライアントのインスタンス化
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

headers = {
    'Authorization': f'Client-ID {CLIENT_ID}',
}

# WebhookからのPOSTデータの構造を定義します。LINEからのWebhookは一連のイベントを含んでいます。
# これらのイベントは、ユーザーからのメッセージ、ユーザーが友達になった通知、など様々なものがあります。
class LineWebhook(BaseModel):
    destination: str
    events: List[dict]

# バーコード生成
def generate_barcode_image_from_text(data: str, filename: str = "barcode"):
    # バーコードオブジェクトを生成（JANコードのクラスを取得）EAN13オブジェクトの生成
    ean13 = EAN13(data, writer=ImageWriter())
    ean13.save(filename)

# Azure保存
def upload_image_to_azure(file_path):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_path)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    return blob_client.url

# /callbackへのPOSTリクエストを処理するルートを定義
@app.post("/callback/")
async def callback(webhook_data: LineWebhook):
    for event in webhook_data.events:
        if event["type"] == "message":
            # LINEサーバーから画像データをダウンロード
            if event["message"]["type"] == "image":
                # LINEサーバーから画像データをダウンロード：download image data from line server
                message_content = line_bot_api.get_message_content(event["message"]["id"])
                # 画像データを一時ファイルに保存：save the image data to a temp file
                image_temp = tempfile.NamedTemporaryFile(delete=False)
                for chunk in message_content.iter_content():
                    image_temp.write(chunk)
                image_temp.close()
                # # 画像からバーコードを読み取る：read the barcode from the image

                # ユーザーIDの取得
                user_id = event["source"]["userId"]
                
            elif event["message"]["type"] == "text":
                text = event["message"]["text"]
                
                # 受信したテキストでバーコードを生成
                generate_barcode_image_from_text(text, 'barcode')

                # Azure Blob Storageにアップロード
                image_url = upload_image_to_azure('barcode.png')

                # アップロードされた画像URLを含むImageSendMessageを生成
                image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)

                # ユーザーに画像を送り返す
                line_bot_api.reply_message(event["replyToken"], image_message)
              
    return {"status": "OK"}

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)