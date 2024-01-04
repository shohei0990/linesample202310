import datetime
from dateutil.relativedelta import relativedelta

import streamlit as st
from streamlit_option_menu import option_menu  # option_menuを使用するために追加

import pandas as pd
import matplotlib.pyplot as plt

import json
import os
import requests

#%%
# JSON ファイルの読み込み
file = r"C:\Users\redgr\workspace\20231022_LINEsample\shinohara\myproject_Renaissance\myproject_Renaissance\rune4output.json"
df = pd.read_json(file)

# 重複データの削除
df = df.drop_duplicates()
#index の降り直し
df = df.reset_index(drop=True)

#%%
# ポイントカードでグルーピングし、売上金額順にソート
# 直近 n ヶ月の購入金額を対象とする
def rule_amount(col, df, n, x):

    today = datetime.date.today() 
    target_day = today - relativedelta(months=n)

    df_latest = df.query("DATE_TIME > @target_day")

    grouped = df_latest[["POINT_CARD", "TTL_AMT_EX_TAX"]].groupby("POINT_CARD")
    # 直近 n ヶ月の購入金額合計でソート
    grouped_sum = grouped.sum().sort_values("TTL_AMT_EX_TAX", ascending=True)
    # 上位 x % を抽出
    sum_highest = grouped_sum.head(int(len(grouped_sum) * x/100))
    # 円グラフ描画
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    sum_highest.plot(kind="barh", ax=ax, subplots=True)
    col.pyplot(fig)

#%%
# ポイントカードの利用率順にソート
# 直近 n ヶ月の利用率を対象とする
def rule_ratio(col, df, n, x):

    today = datetime.date.today() 
    target_day = today - relativedelta(months=n)

    df_latest = df.query("DATE_TIME > @target_day")
    
    # クーポンを使っていたら 1 使っていなかったら 0 とする列を追加
    # この平均値がクーポン利用率となる
    df_latest.loc[df["PRM_CODE"] == "CPN00000000", "PRM_FLAG"] = 0
    df_latest.loc[df["PRM_CODE"] != "CPN00000000", "PRM_FLAG"] = 1

    grouped = df_latest[["POINT_CARD", "PRM_FLAG"]].groupby("POINT_CARD")
    ratio_mean = grouped.mean().sort_values("PRM_FLAG", ascending=False)
    # 上位 x % を抽出
    ratio_highest = ratio_mean.head(int(len(ratio_mean) * x/100))
    # 円グラフ描画
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    ratio_highest.plot(kind="barh", ax=ax, subplots=True)
    col.pyplot(fig)

#%%
# ここから先 streamlit の表示内容

# サイドバーでページオプションを選択
with st.sidebar:
    selected = option_menu(
        menu_title="メインメニュー",
        options=["BIツール", "プロモーション管理"],
        icons=["house", "people"],
        menu_icon="cast", default_index=0,
    )

# 選択されたページに応じて表示を切り替え
if selected == "BIツール":
    st.title("優良顧客発掘ツール")
    st.write("読み込んだJSONデータ:", df)

    # 入力フォーム
    n = st.text_input('直近何ヶ月のデータを表示しますか？', '24')
    x = st.number_input('上位何%のデータを表示しますか？',0 ,100, 100, step=20)

    # グラフの表示
    col1, col2 = st.columns([1, 1])
    rule_amount(col1, df, int(n), int(x))
    rule_ratio(col2, df, int(n), int(x))

    # 直近のデータをフィルタリング
    today = datetime.date.today() 
    target_day = today - relativedelta(months=int(n))
    df_latest = df.query("DATE_TIME > @target_day")

    # ボタンを押したときにサーバー側にデータをJSON形式で保存
    st.write('最新のデータ保存：')
    if st.button('保存'):
        # JSON形式でファイルに書き出し
        with open('latest_data.json', 'w', encoding='utf-8') as f:
            df_latest.to_json(f, force_ascii=False, orient='records', lines=True)
        
        st.success('優良顧客対象のデータが保存されました。')

elif selected == "プロモーション管理":

    # CSVファイルのパス（ここにあなたのCSVファイルのパスを指定してください）
    json_file_path2 = r"C:\Users\redgr\workspace\20231022_LINEsample\shinohara\myproject_Renaissance\myproject_Renaissance\latest_data.json"

    # CSVファイルからデータフレームを読み込む
    df2 = pd.read_json(json_file_path2, lines=True)

    # FastAPIエンドポイントのURL
    FASTAPI_ENDPOINT = "https://webapp-class1to4-4-con.azurewebsites.net/" 

    # プロモーションデータ入力用フォーム
    # プロモーション登録ボタン

    # 対象ユーザーを表示するための機能
    def show_target_users():
        target_users = df2
        st.write("### クーポン対象ユーザー")
        st.dataframe(target_users)  # ここで他の必要なカラムを表示することができます

    show_target_users_button = st.button('クーポン対象者を表示')

    if show_target_users_button:
        show_target_users()

    with st.form("promotion_form"):
        st.write("### プロモーション詳細を入力")
        prm_code = st.text_input("PRM_CODE", "202300000272")
        prm_name = st.text_input("PRM_NAME", "冬のビール特売キャンペーン")
        from_date = st.date_input("FROM_DATE")
        to_date = st.date_input("TO_DATE")
        percent = st.number_input("PERCENT", min_value=0.0, max_value=100.0, value=20.0) / 100
        discount = st.number_input("DISCOUNT", min_value=0, max_value=100, value=0)
        prd_id = st.number_input("PRD_ID", min_value=0, value=1)
        submit_button = st.form_submit_button(label='クーポン登録')

    if submit_button:
        promotion_data = {
            "PRM_CODE": prm_code,
            "PRM_NAME": prm_name,
            "FROM_DATE": str(from_date),
            "TO_DATE": str(to_date),
            "PERCENT": percent,
            "DISCOUNT": discount,
            "PRD_ID": prd_id
        }
        response = requests.post(f"{FASTAPI_ENDPOINT}/promotions/", json=promotion_data)
        if response.status_code == 200:
            st.success("プロモーションが正常に登録されました。")
            st.write("### 入力されたプロモーション詳細")
            st.json(promotion_data)  # 入力されたデータを表示
        else:
            st.error(f"プロモーションの登録に失敗しました: {response.text}")

    # USERID入力用
    # user_id = st.text_input("クーポンを送るUSERID")



    # LINE_IDを用いて、対象ユーザーにクーポンを送信する機能
    # 固定のクーポン番号（12桁）
    # クーポン番号の入力
    coupon_number = st.text_input('クーポン番号を入力してください（12桁）', max_chars=12)


    def send_coupon_to_user(userid, coupon_number):
        # JSONリクエストボディを作成
        payload = {
            "userid": userid,
            "barcode_number": coupon_number
        }
        
        # FastAPIエンドポイントにPOSTリクエストを送信
        response = requests.post(f"{FASTAPI_ENDPOINT}/promotionsend/", json=payload)
        return response

    # 対象ユーザーにクーポンを送信するボタン
    send_coupon_button = st.button('対象ユーザーにクーポンを送信')

    if send_coupon_button:
        # 入力されたクーポン番号の検証
        if len(coupon_number) == 12 and coupon_number.isdigit():
            target_users = df2
            for line_id in target_users['LINE_ID']:
                response = send_coupon_to_user(line_id, coupon_number)
                if response.ok:
                    st.success(f"ユーザー {line_id} へのクーポンが送信されました。")
                else:
                    st.error(f"ユーザー {line_id} へのクーポン送信に失敗しました: {response.text}")
        else:
            st.error("正しい12桁のクーポン番号を入力してください。")




