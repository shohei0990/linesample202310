from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from . import settings

import os

host='mysql-class1to4-japaneast-4.mysql.database.azure.com'
user='Tech0class1to44'
password='Step4-class1to4-4'
database='modern-pos-rev'

# # 環境変数を参照
# host =  os.environ.get("host")
# user  =  os.environ.get("user")
# password =  os.environ.get("password")
# database =  os.environ.get("database")

# app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'

SQLALCHEMY_DATABASE_URL = f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

db_session = sessionmaker(autocommit=False, autoflush=False, bind = engine)

Base = declarative_base()

