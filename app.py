import os
import cv2
import numpy as np
from flask import Flask, request, redirect, jsonify
import requests

app = Flask(__name__)

# 환경 변수에서 값 불러오기
CALLBACK_URL = os.getenv("CALLBACK_URL", "https://cpss.up.railway.app/callback")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
STATE_VALUE = "RANDOM_STATE_STRING"  # 실제 운영 시 난수 생성 및 검증 필요

@app.route('/')
def index():
    auth_url = (
        "https://nid.naver.com/oauth2.0/authorize"
        f"?response_type=code&client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={CALLBACK_URL}"
        f"&state={STATE_VALUE}"
    )
    return f'<a href="{auth_url}">네이버 로그인하기</a>'

@app.route('/callback')
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    
    if not code:
        return jsonify({"error": "Authorization code not received"}), 400
    
    if state != STATE_VALUE:
        return jsonify({"error": "Invalid state parameter"}), 400

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
    이미지 파일에서 OpenCV를 사용하여 QR 코드를 디코딩하는 엔드포인트.
    클라이언트는 'file' 필드에 이미지 파일을 전송해야 합니다.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # 파일을 바이트 배열로 읽고 numpy 배열로 변환
        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
        # 이미지 디코딩 (컬러 이미지로 읽음)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # OpenCV 내장 QR 코드 디텍터 사용
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(image)
        
        if data:
            return jsonify({'qr_data': data})
        else:
            return jsonify({'error': 'No QR code found in the image'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
