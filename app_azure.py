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
connection_string = 
container_name = "qrcode"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# LINE Botのシークレットとアクセストークン
# LINE Bot APIとWebhookHandlerをインスタンス化します。
# LINE Bot APIは、LINEのメッセージを送受信するためのAPIを提供します。
# WebhookHandlerは、Webhookからのイベントを処理するためのクラスです。
CHANNEL_SECRET = ""
CHANNEL_ACCESS_TOKEN = ""
CLIENT_ID   = '5e439cffec5166f' 
image_url   = "https://i.imgur.com/7PeNPFY.jpg"  # このURLは実際の画像のURLに置き換える必要があります。
preview_url = "https://i.imgur.com/7PeNPFY.jpg"  # プレビュー画像のURL。通常は元の画像と同じURLを使用することができます。


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

# 画像生成
def generate_image_from_text(text: str, filename: str = "output.jpg"):
    # Create a blank image
    width, height = 400, 200
    background_color = (255, 255, 255)
    text_color = (0, 0, 0)
    
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # You might need to adjust this font path or use a different font
    font = ImageFont.truetype("arial.ttf", size=30)
    text_width, text_height = draw.textsize(text, font=font)
    text_position = ((width - text_width) / 2, (height - text_height) / 2)

    draw.text(text_position, text, font=font, fill=text_color)

    image.save(filename)

# QR生成
def generate_qrcode_image_from_text(data: str, filename: str = "output.jpg"):
    # QRコードオブジェクトを作成
    qr = qrcode.QRCode(
        version=1,  # QRコードのバージョン (1から40まで)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 誤り訂正レベル (L, M, Q, H)
        box_size=10,  # ボックスサイズ
        border=4,     # 境界の幅
    )

    # データをQRコードに追加
    qr.add_data(data)
    # QRコードのマトリックスを生成
    qr.make(fit=True)
    # QRコードのイメージを取得
    img = qr.make_image(fill_color="black", back_color="white")
    # 画像を保存
    img.save(filename)

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

                # Generate an image with the received text
                generate_qrcode_image_from_text(text)
                
                # Azure Blob Storageにアップロード
                image_url = upload_image_to_azure('output.jpg')

                # Create an ImageSendMessage with the uploaded image URL
                image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)

                # Send the image back to the user
                line_bot_api.reply_message(event["replyToken"], image_message)
              
    return {"status": "OK"}

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)