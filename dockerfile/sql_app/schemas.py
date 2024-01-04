from pydantic import BaseModel, Field
from typing import List

class ProductMaster(BaseModel):
    productcode: str =  Field(...
                        ,min_length=6, max_length=6
                        )
    name: str
    price: int

    class Config:
        orm_mode = True

class Product(BaseModel):
    PRD_ID: int
    PRD_CODE : str = Field(...,min_length=6, max_length=6)
    NAME: str
    PRICE: int
    COUNT: int

    class Config:
        orm_mode = True

class Transaction(BaseModel):
    MEM_ID: int
    EMP_CODE : int
    STORE_CODE : int
    POS_ID : int
    POINT_CARD : str
    BUYPRODUCTS: List[Product]

    class Config:
        orm_mode = True

class Transaction_detail(BaseModel):
    TRD_ID :int
#    DTL_ID :int
    PRD_ID :int
    PRD_CODE :str
    PRD_NAME :str
    PRD_PRICE :int
    TAX_CD :str
    PRM_ID : int
    DISCOUNT : int

    class Config:
        orm_mode = True

class Line(BaseModel):
    image_url :str

    class Config:
        orm_mode = True