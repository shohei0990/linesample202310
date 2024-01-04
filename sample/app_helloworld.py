import os # ここを追加
from dotenv import load_dotenv # ここを追加
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

# FastAPIをインスタンス化
app = FastAPI()

# LINE Botのシークレットとアクセストークン
# LINE Bot APIとWebhookHandlerをインスタンス化します。
# LINE Bot APIは、LINEのメッセージを送受信するためのAPIを提供します。
# WebhookHandlerは、Webhookからのイベントを処理するためのクラスです。
CHANNEL_SECRET = ""
CHANNEL_ACCESS_TOKEN = ""

# LINE Bot APIを使うためのクライアントのインスタンス化
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# WebhookからのPOSTデータの構造を定義
# WebhookからのPOSTデータの構造を定義します。LINEからのWebhookは一連のイベントを含んでいます。
# これらのイベントは、ユーザーからのメッセージ、ユーザーが友達になった通知、など様々なものがあります。
class LineWebhook(BaseModel):
    destination: str
    events: List[dict]

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
                
                # ユーザーが「ざいことうろく」を入力した場合
                if text == "ざいことうろく":
                    line_bot_api.reply_message(
                        event["replyToken"],
                        TextSendMessage(text="最初に、商品のバーコード写真を投稿するか カメラを撮影してください"))

                # ユーザーが「ざいこかくにん」を入力した場合
                elif text == "ざいこかくにん":
                    line_bot_api.reply_message(
                        event["replyToken"],
                        TextSendMessage(text="こちらがのざいこリストはこちらです"))
                
                # ユーザーが「かいものリスト」を入力した場合
                elif text == "かいものリスト":
                    line_bot_api.reply_message(
                        event["replyToken"],
                        TextSendMessage(text="あなたのかいものリストはこちらです"))

                # その他のテキストメッセージにはそのまま応答します
                else:
                    # ユーザーIDの取得
                    user_id = event["source"]["userId"]
                    line_bot_api.reply_message(
                        event["replyToken"],
                        TextSendMessage(text="User ID: " + user_id + "\nMessage: " + event["message"]["text"]))
   
    return {"status": "OK"}

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)