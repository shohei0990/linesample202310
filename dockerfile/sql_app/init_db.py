from sqlalchemy.orm import Session

from datetime import datetime

import models
from database import db_session, engine, Base

def add_products_to_database(db: Session, product_data: list):
    try:
        for product in product_data:
            product_master = models.ProductMaster( PRD_CODE= product["JANコード"], NAME=product["商品名"], PRICE=product["価格"])

            db.add(product_master)

        db.commit()
        print()
        return True
    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()

def add_promotions_to_database(db: Session, promotion_data: list):
    try:
        for product in promotion_data:
            product_master = models.Promotion(
                PRM_CODE= product["PRM_CODE"],
                FROM_DATE=product["FROM_DATE"],
                TO_DATE=product["TO_DATE"],
                NAME = product["NAME"],
                PERCENT = product["PERCENT"],
                DISCOUNT = product["DISCOUNT"],
                PRD_ID = product["PRD_ID"]
                )

            db.add(product_master)

        db.commit()
        print()
        return True
    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()

models.Base.metadata.create_all(bind=engine)

# 既存のテーブルを削除
Base.metadata.drop_all(engine)

# 新しいテーブルを作成
Base.metadata.create_all(engine)

product_data = [
    {"JANコード": "4901777323131", "商品名": "コカ・コーラ", "価格": 150},
    {"JANコード": "4902102111513", "商品名": "ペプシコーラ", "価格": 140},
    {"JANコード": "4901114235744", "商品名": "日本茶", "価格": 120},
    {"JANコード": "4909411073285", "商品名": "オレンジジュース", "価格": 180},
    {"JANコード": "4904323643446", "商品名": "アップルジュース", "価格": 160},
    {"JANコード": "4901360349287", "商品名": "レモネード", "価格": 200},
    {"JANコード": "4902750863108", "商品名": "緑茶", "価格": 130},
    {"JANコード": "4901080267519", "商品名": "コーヒー", "価格": 170},
    {"JANコード": "4909131014820", "商品名": "ウーロン茶", "価格": 110},
    {"JANコード": "4902102072121", "商品名": "グレープジュース", "価格": 190},
]

promotions = [
    {
        "PRM_CODE": "PROMO123",
        "FROM_DATE": datetime(2023, 9, 1),
        "TO_DATE": datetime(2023,9,20),
        "NAME": "夏のセール",
        "PERCENT": 10.0,
        "DISCOUNT": 0,
        "PRD_ID": 1  # この値は商品に関連付けられる特定の商品IDに置き換える必要があります
    },
    {
        "PRM_CODE": "PROMO456",
        "FROM_DATE": datetime(2023, 10, 15),
        "TO_DATE": datetime(2023, 10, 31),
        "NAME": "秋のキャンペーン",
        "PERCENT": 0.0,
        "DISCOUNT": 20,
        "PRD_ID":2
    }]

tax = models.TaxMaster( CODE=10, NAME="10%", PERCENT=0.1)


db = db_session()
db.add(tax)


add_products_to_database(db, product_data)
add_promotions_to_database(db, promotions)

db.close()