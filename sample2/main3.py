import pandas as pd
import streamlit as st
import requests

# CSVファイルのパス（ここにあなたのCSVファイルのパスを指定してください）
csv_file_path = 'rune4_sort.csv'

# CSVファイルからデータフレームを読み込む
df = pd.read_csv(csv_file_path)

# FastAPIエンドポイントのURL
FASTAPI_ENDPOINT = ""

# プロモーションデータ入力用フォーム
# プロモーション登録ボタン

with st.form("promotion_form"):
    st.write("### プロモーション詳細を入力")
    prm_code = st.text_input("PRM_CODE", "2023000000725")
    prm_name = st.text_input("PRM_NAME", "test")
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

# 対象ユーザーを表示するための機能
def show_target_users():
    target_users = df[df['linecamp'] == 1]
    st.write("### クーポン対象ユーザー")
    st.dataframe(target_users)  # ここで他の必要なカラムを表示することができます

show_target_users_button = st.button('クーポン対象者を表示')

if show_target_users_button:
    show_target_users()

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
        target_users = df[df['linecamp'] == 1]
        for line_id in target_users['LINE_ID']:
            response = send_coupon_to_user(line_id, coupon_number)
            if response.ok:
                st.success(f"ユーザー {line_id} へのクーポンが送信されました。")
            else:
                st.error(f"ユーザー {line_id} へのクーポン送信に失敗しました: {response.text}")
    else:
        st.error("正しい12桁のクーポン番号を入力してください。")