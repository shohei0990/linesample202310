import requests

CLIENT_ID = '5e439cffec5166f'  # 上記で取得したClient IDを使用

headers = {
    'Authorization': f'Client-ID {CLIENT_ID}',
}

# 画像ファイルをバイナリモードで読み込む
with open('test.jpg', 'rb') as image_file:
    # 画像データをエンコード
    image_data = image_file.read()
    response = requests.post('https://api.imgur.com/3/image', headers=headers, data=image_data)

# レスポンスからURLを取得
data = response.json()
image_url = data['data']['link']

print(image_url)  # これが公開URLです

