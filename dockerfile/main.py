from fastapi import FastAPI, Depends, Request, HTTPException, Header,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from sql_app import schemas, models,crud
from sql_app.database import db_session, engine
from sql_app.models import Promotions

from datetime import date
from pydantic import BaseModel
from typing import Optional

import uvicorn
import json

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FollowEvent,TextSendMessage,ImageSendMessage
from starlette.exceptions import HTTPException

import os
from os.path import join, dirname
from dotenv import load_dotenv 

# 追記：Azure連携
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
# 追記：
from barcode import EAN13
from barcode.writer import ImageWriter
from linebot.exceptions import LineBotApiError


# 追記：Azureの設定
connection_string = ""
container_name = "barcode"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# 追加
# リクエストボディのためのモデルを定義
class PromotionCreate(BaseModel):
    PRM_CODE: str
    PRM_NAME: str
    FROM_DATE: date
    TO_DATE: date
    PERCENT: float
    DISCOUNT: float
    PRD_ID: int


class PromotionRequest(BaseModel):
    userid: str
    barcode_number: str


# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)

# LINE Botのシークレットとアクセストークン
# LINE Bot APIとWebhookHandlerをインスタンス化します。
# LINE Bot APIは、LINEのメッセージを送受信するためのAPIを提供します。
# WebhookHandlerは、Webhookからのイベントを処理するためのクラスです。
# 環境変数から設定を読み込む
#CHANNEL_SECRET = os.environ.get("CHA_SECRET", "default_secret")
#CHANNEL_ACCESS_TOKEN = os.environ.get("CHA_ACCESS", "default_access")
#CLIENT_ID = os.environ.get("CLIENT", "default_clientid") 

CHANNEL_SECRET = 
CHANNEL_ACCESS_TOKEN = 
CLIENT_ID   = 

# LINE Bot APIを使うためのクライアントのインスタンス化
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# FastAPIをインスタンス化
app = FastAPI()

headers = {
    'Authorization': f'Client-ID {CLIENT_ID}',
}

#通信設定
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    db = db_session()
    try:
        return db
    finally:
        db.close()

# 追記：バーコード生成の最後の桁を追加
def calculate_check_digit(ean):
    assert len(ean) == 12, "EAN code should be 12 digits"
    sum_odd = sum(int(digit) for digit in ean[::2])
    sum_even = sum(int(digit) for digit in ean[1::2])
    checksum = (10 - (sum_odd + 3 * sum_even) % 10) % 10
    return checksum

# 追記：バーコード生成
def generate_barcode_image_from_text(data: str, filename: str = "barcode"):
    # バーコードオブジェクトを生成（JANコードのクラスを取得）EAN13オブジェクトの生成
    ean13 = EAN13(data, writer=ImageWriter())
    ean13.save(filename)

# 追記：Azure保存
def upload_image_to_azure(file_path):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_path)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    return blob_client.url

@app.get("/")
def index():
    return "Hello world"

###商品マスタ検索
@app.get("/search_product/{code}")
async def search(code:str, db: Session = Depends(get_db)):
    
    product_data = crud.get_product(db, code)
    print(product_data)

    if product_data:
        return product_data
    else:    
        return "null"

###商品マスタ検索
@app.get("/search_promotion/{code}")
async def search(code:str, db: Session = Depends(get_db)):
    
    promotion_data = crud.get_promotion(db, code)
    print(promotion_data)

    if promotion_data:
        return promotion_data
    else:    
        return "null"

###購入明細の登録
@app.post("/buy_product/")
async def search(data:schemas.Transaction, db: Session = Depends(get_db)):
        TRD_ID = crud.create_transaction(db, data)
        for product in data.BUYPRODUCTS:
            print(product)
            for i in range(product.COUNT):
                promotion = db.query(models.Promotions).filter(models.Promotions.PRD_ID == product.PRD_ID).first()
                if promotion:
                    discount = promotion.DISCOUNT + product.PRICE * promotion.PERCENT
                    Transaction_detail = {
                        "TRD_ID" : TRD_ID,
                        "PRD_ID" : product.PRD_ID,
                        "PRD_CODE" : product.PRD_CODE,
                        "PRD_NAME" : product.NAME,
                        "PRD_PRICE" : product.PRICE,
                        "TAX_ID" : 1,
                        "PRM_ID" : promotion.PRM_ID,
                        "DISCOUNT" : discount
                    }
                else:
                    Transaction_detail = {
                        "TRD_ID" : TRD_ID,
                        "PRD_ID" : product.PRD_ID,
                        "PRD_CODE" : product.PRD_CODE,
                        "PRD_NAME" : product.NAME,
                        "PRD_PRICE" : product.PRICE,
                        "TAX_ID" : 1,
                        "PRM_ID" : None,  # プロモーションが存在しない場合はPRM_IDをNoneに設定
                        "DISCOUNT" : 0  # プロモーションが存在しない場合はDISCOUNTを0に設定
                    }
                crud.create_transaction_detail(db, Transaction_detail)

        TOTAL_AMT, TTL_AMT_EX_TAX = crud.update_transaction(db, TRD_ID)
        print(TOTAL_AMT)
        return True, TOTAL_AMT, TTL_AMT_EX_TAX

## 追記：プロモーション情報の登録
@app.post("/promotions/")
async def create_promotion(promotion: PromotionCreate, db: Session = Depends(get_db)):

    # 13桁目の確認生成
    check_digit = calculate_check_digit(promotion.PRM_CODE)
    full_barcode = promotion.PRM_CODE + str(check_digit)

    # 受信したテキストでバーコードを生成
    generate_barcode_image_from_text(full_barcode, 'barcode')

    db_promotion = models.Promotions(
        PRM_CODE=full_barcode,
        PRM_NAME=promotion.PRM_NAME,
        FROM_DATE=promotion.FROM_DATE,
        TO_DATE=promotion.TO_DATE,
        PERCENT=promotion.PERCENT,
        DISCOUNT=promotion.DISCOUNT,
        PRD_ID=promotion.PRD_ID
    )
    db.add(db_promotion)
    db.commit()
    db.refresh(db_promotion)
    return db_promotion


#　追記：Lineユーザーへの送信
@app.post("/promotionsend/")
def push_promotion(request: PromotionRequest):
    try:
        #特定の１ユーザーに送る時はこちら。その他にも、マルチキャスト、ナローキャストがある。
        # line_bot_api.push_message(userid, TextSendMessage(text='test message from python to one user'))
        # 13桁目の確認生成
        # バーコード番号からチェックディジットを計算してバーコードを生成
        full_barcode = request.barcode_number + str(calculate_check_digit(request.barcode_number))
        generate_barcode_image_from_text(full_barcode, "barcode")
        
        # バーコード画像をAzureにアップロード
        image_url = upload_image_to_azure('barcode.png')


        image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
        line_bot_api.push_message(request.userid, image_message)

        # 成功のレスポンスを返す
        return {"status": "OK", "userid": request.userid, "message": "Coupon sent successfully."}

    except LineBotApiError as e:
        # LINE APIエラーが発生した場合の処理
        return {"status": "NG", "userid": request.userid, "message": f"Failed to send coupon: {e.error.message}"}

    except Exception as e:
        # その他のエラーが発生した場合の処理
        return {"status": "NG", "userid": request.userid, "message": str(e)}

        # with get_db_session() as db:
        #     users = db.query(models.User).all()
        #     for user in users:
        #         line_bot_api.push_message(user.LINE_ID, TextSendMessage(text='おいらは仁坊！'))


#Lineのイベント処理
@app.post("/callback")
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature=Header(None),
    ):
    body = await request.body()

    try:
        background_tasks.add_task(
            handler.handle, body.decode("utf-8"), x_line_signature
        )
        
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return JSONResponse(content={})

#登録・ブロック時の対応
@handler.add(FollowEvent)
def handle_follow(event):  # db 引数の型注釈を追加
    # Followイベントをハンドリングするコードをここに記述
    with get_db_session() as db:
        user_id = event.source.user_id
        user = models.User(
                    LINE_ID = user_id
                    )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(event)

#メッセージ処理
@handler.add(MessageEvent)
def handle_message(event):
    if event.type != "message" or event.message.type != "text":
        return    
    
    # ユーザーIDを取得して出力
    user_id = event.source.user_id
    print(f"Received message from user ID: {user_id}")

    message = TextMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)
    print(event)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)