import streamlit as st
import pandas as pd
import json

st.title("JSONファイルを読み込むStreamlitアプリ")

# 空のデータフレームを作成
json_data = pd.DataFrame()

# JSONファイルを読み込む
with open("test3.json", "r", encoding='utf-8') as file:
    for line in file:
        # 各行をJSONオブジェクトとして読み込む
        record = json.loads(line)
        # Pandasデータフレームに変換
        record_df = pd.json_normalize(record)
        # 各レコードをデータフレームに追加
        json_data = json_data.append(record_df, ignore_index=True)

# Jsonデータの表示
st.write("読み込んだJSONデータ:", json_data)
