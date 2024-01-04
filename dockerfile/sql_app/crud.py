from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

#製品名の取得
def get_product(db:Session,  code:int):
    response = {}
    product = db.query(models.ProductsMaster).filter(models.ProductsMaster.PRD_CODE == code).first()
    response = {
            "PRD_ID": product.PRD_ID,
            "PRD_CODE": product.PRD_CODE,
            "NAME": product.PRD_NAME,
            "PRICE": product.PRD_PRICE,
            "COUNT": 1
        }
    
    response["PRNAME"] = ""
    response["DISCOUNT"] = 0
    return response

def get_promotion(db:Session, code:int):
    response = {}
    promotion = db.query(models.Promotions).filter(models.Promotions.PRM_CODE == code).first()
    product = db.query(models.ProductsMaster).filter(models.ProductsMaster.PRD_ID == promotion.PRD_ID).first()
    response = {
        "PRD_ID": promotion.PRD_ID,
    }
    response["PRNAME"] = promotion.PRM_NAME
    response["DISCOUNT"] = promotion.DISCOUNT + int(product.PRD_PRICE*promotion.PERCENT)
    return response

#transactionの登録
def create_transaction(db:Session, transaction: schemas.Transaction):
    # 現在の日時を取得
    current_datetime = datetime.now()

    # MySQLのTIMESTAMPフォーマットに整形
    mysql_timestamp = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

    db_transaction = models.Transactions(
                            DATE_TIME = mysql_timestamp,
                            EMP_CODE = transaction.EMP_CODE,
                            STORE_CODE = transaction.STORE_CODE,
                            POS_ID = transaction.POS_ID,
                            TOTAL_AMT = 0,
                            TTL_AMT_EX_TAX = 0,
                            MEM_ID = transaction.MEM_ID,
                            POINT_CARD = transaction.POINT_CARD
                            )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    last_inserted_id = db_transaction.TRD_ID
    return last_inserted_id

#transaction_detailの登録
def create_transaction_detail(db:Session, transaction_detail: schemas.Transaction_detail):
    
    db_transaction = models.TransactionDetail(
                            TRD_ID = transaction_detail["TRD_ID"],
                            PRD_ID = transaction_detail["PRD_ID"],
                            PRD_CODE = transaction_detail["PRD_CODE"],
                            PRD_NAME = transaction_detail["PRD_NAME"],
                            PRD_PRICE = transaction_detail["PRD_PRICE"],
                            TAX_ID = transaction_detail["TAX_ID"],
                            PRM_ID = transaction_detail["PRM_ID"],
                            DISCOUNT = transaction_detail["DISCOUNT"]
                            )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

#transactionの更新
def update_transaction(db:Session, TRD_ID):
    products = db.query(models.TransactionDetail).filter(models.TransactionDetail.TRD_ID == TRD_ID).all()
    TOTAL_AMT = 0
    TTL_AMT_EX_TAX = 0
    for product in products:
        Tax = db.query(models.TaxsMaster).filter(models.TaxsMaster.TAX_ID == product.TAX_ID).first()
        print("TAX_ID",Tax.TAX_ID)

        TOTAL_AMT += product.PRD_PRICE
        TOTAL_AMT -= product.DISCOUNT
        TTL_AMT_EX_TAX += (product.PRD_PRICE - product.DISCOUNT) + (product.PRD_PRICE - product.DISCOUNT)*(Tax.TAX_PER)
    
    db_transaction = db.query(models.Transactions).filter(models.Transactions.TRD_ID == TRD_ID).first()
    
    try:
        if db_transaction:
            db_transaction.TOTAL_AMT = TOTAL_AMT
            db_transaction.TTL_AMT_EX_TAX = TTL_AMT_EX_TAX  
            db.commit()
            db.refresh(db_transaction)
    except Exception as e:
        db.rollback()  # エラーが発生した場合はロールバック
        raise e
    
    finally:
        db.close()  # セッションを閉じる

    return TOTAL_AMT, TTL_AMT_EX_TAX  
