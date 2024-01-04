from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, VARCHAR, CHAR,DECIMAL,TIMESTAMP,DATE
from .database import Base
from pydantic import BaseModel

class ProductsMaster(Base):
    __tablename__ ="M_PRODUCT"
    PRD_ID = Column(Integer, primary_key = True, index=True,autoincrement=True)
    PRD_CODE = Column(CHAR(6), unique=True, index=True)
    PRD_NAME = Column(VARCHAR(32))
    PRD_PRICE = Column(Integer)
    TAX_ID = Column(Integer,ForeignKey("M_TAX.TAX_ID",ondelete="SET NULL"))

class TaxsMaster(Base):
    __tablename__ = "M_TAX"
    TAX_ID = Column(Integer, primary_key = True, index=True,autoincrement=True)
    TAX_CODE = Column(CHAR(6), unique=True, index=True)
    TAX_NAME = Column(VARCHAR(32))
    TAX_PER = Column(DECIMAL(2,2))

class Transactions(Base):
    __tablename__ = "M_TRANSACTION"
    TRD_ID = Column(Integer, primary_key = True, index=True, autoincrement=True)
    MEM_ID = Column(Integer,ForeignKey("M_USER.MEM_ID", ondelete="SET NULL"))
    POINT_CARD = Column(CHAR(7))
    DATE_TIME = Column(TIMESTAMP)
    STORE_CODE = Column(CHAR(8))
    EMP_CODE = Column(CHAR(6))
    POS_ID = Column(Integer)
    TOTAL_AMT = Column(Integer)
    TTL_AMT_EX_TAX = Column(Integer)

class TransactionDetail(Base):
    __tablename__ = "M_TRANSACTION_DETAILS"
    DTL_ID = Column(Integer, primary_key = True, index=True, autoincrement=True)
    TRD_ID = Column(Integer, ForeignKey('M_TRANSACTION.TRD_ID', ondelete="SET NULL"), nullable=True)
    PRD_ID = Column(Integer, ForeignKey('M_PRODUCT.PRD_ID', ondelete="SET NULL"), nullable=True)
    PRD_CODE = Column(CHAR(6))
    PRD_NAME = Column(VARCHAR(32))
    PRD_PRICE = Column(Integer)
    PRM_ID = Column(Integer,ForeignKey("M_CAMPAIGN.PRM_ID",ondelete="SET NULL"))
    PERCENT = Column(DECIMAL(2,2), nullable=True)
    DISCOUNT = Column(Integer, nullable=True)
    TAX_ID = Column(Integer, ForeignKey("M_TAX.TAX_ID"), nullable=False)

class Promotions(Base):
    __tablename__ = "M_CAMPAIGN"
    PRM_ID = Column(Integer, primary_key = True, index=True, autoincrement=True)
    PRM_CODE = Column(CHAR(13),unique=True,index=True)
    PRM_NAME = Column(VARCHAR(32))
    FROM_DATE = Column(DATE)
    TO_DATE = Column(DATE)
    PERCENT = Column(DECIMAL(2,2), nullable=True)
    DISCOUNT = Column(Integer, nullable=True)
    PRD_ID = Column(Integer, ForeignKey('M_PRODUCT.PRD_ID', ondelete="SET NULL"), nullable=True)

class Users(Base):
    __tablename__ = "M_USER"
    MEM_ID = Column(Integer, primary_key = True, index=True,autoincrement=True)
    LINE_ID = Column(CHAR(33),unique=True,index=True)
    POINT_CARD = Column(CHAR(7),unique=True,index=True)
    RGS_DATE = Column(DATE)
    NAME = Column(VARCHAR(32))
    BIRTHDAY = Column(DATE)
    SEX = Column(Integer)
    ADDRESS = Column(VARCHAR(64))
    MAIL = Column(VARCHAR(64),unique=True)

