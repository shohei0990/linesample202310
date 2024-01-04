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

# WebhookからのPOSTデータの構造を定義
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
                generate_image_from_text(text)
                # Now, upload this image to Imgur (or any other service) and get its URL
                with open('output.jpg', 'rb') as image_file:
                    image_data = image_file.read()
                    response = requests.post('https://api.imgur.com/3/image', headers=headers, data=image_data)
                data = response.json()
                image_url = data['data']['link']

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