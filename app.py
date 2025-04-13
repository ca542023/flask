import os
import io
from flask import Flask, request, redirect, jsonify
import requests

# QR 코드 디코딩을 위한 라이브러리들
from pyzbar.pyzbar import decode
from PIL import Image

app = Flask(__name__)

# 환경 변수에서 값 불러오기
CALLBACK_URL = os.getenv("CALLBACK_URL", "https://cpss.up.railway.app/callback")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
# 실제 운영 시 CSRF 방지를 위해 난수 생성 로직을 적용할 것
STATE_VALUE = "RANDOM_STATE_STRING"

@app.route('/')
def index():
    # 네이버 로그인 인증 요청 URL 구성
    auth_url = (
        "https://nid.naver.com/oauth2.0/authorize"
        f"?response_type=code&client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={CALLBACK_URL}"
        f"&state={STATE_VALUE}"
    )
    # 간단한 네이버 로그인 버튼을 제공
    return f'<a href="{auth_url}">네이버 로그인하기</a>'

@app.route('/callback')
def callback():
    # 네이버에서 리다이렉트 시 전달하는 code와 state 파라미터 수신
    code = request.args.get("code")
    state = request.args.get("state")
    
    if not code:
        return jsonify({"error": "Authorization code not received"}), 400
    
    # state 검증 (실제 운영 시, 보안을 위해 개선 필요)
    if state != STATE_VALUE:
        return jsonify({"error": "Invalid state parameter"}), 400

    # 토큰 발급을 위한 네이버 API 호출
    token_url = "https://nid.naver.com/oauth2.0/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": NAVER_CLIENT_ID,
        "client_secret": NAVER_CLIENT_SECRET,
        "redirect_uri": CALLBACK_URL,
        "code": code,
        "state": state,
    }
    
    token_response = requests.get(token_url, params=payload)
    if token_response.status_code == 200:
        token_data = token_response.json()
        return jsonify(token_data)
    else:
        return jsonify({
            "error": "Failed to get token",
            "details": token_response.text
        }), token_response.status_code

@app.route('/scan', methods=['POST'])
def scan_qr():
    """
    업로드된 이미지 파일에서 QR 코드를 디코딩하여 그 데이터를 반환하는 엔드포인트.
    클라이언트는 'file'이라는 필드로 QR 코드 이미지 파일을 전송해야 합니다.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # 이미지 파일을 Pillow의 Image 객체로 열기
        image = Image.open(file.stream)
        # pyzbar를 사용하여 QR 코드 디코딩
        decoded_objects = decode(image)
        if not decoded_objects:
            return jsonify({'error': 'No QR code found in the image'}), 400
        # 첫 번째 QR 코드 데이터 추출 (여러 개라면 원하는대로 처리)
        qr_data = decoded_objects[0].data.decode('utf-8')
        return jsonify({'qr_data': qr_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Railway에서는 PORT 환경 변수를 통해 할당된 포트를 사용합니다.
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
