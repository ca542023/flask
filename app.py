import os
from flask import Flask, request, redirect, jsonify
import requests

app = Flask(__name__)

# 환경 변수에서 값 불러오기; Railway Variables에 CALLBACK_URL, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET로 등록해둔 값 사용
CALLBACK_URL = os.getenv("CALLBACK_URL", "https://cpsslab.up.railway.app/callback")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
# state 값을 실제 운영에서는 CSRF 방지를 위해 난수로 생성해야 합니다.
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
    # 단순한 버튼 또는 링크로 네이버 로그인 페이지로 리다이렉트
    return f'<a href="{auth_url}">네이버 로그인하기</a>'

@app.route('/callback')
def callback():
    # 네이버에서 리다이렉트 시 전달하는 code와 state 파라미터 수신
    code = request.args.get("code")
    state = request.args.get("state")
    
    if not code:
        return jsonify({"error": "Authorization code not received"}), 400
    
    # state 검증 (실제 운영 시, 보안 강화를 위해 반드시 확인 필요)
    if state != STATE_VALUE:
        return jsonify({"error": "Invalid state parameter"}), 400

    # 네이버에서 토큰 발급 요청 URL 및 파라미터 구성
    token_url = "https://nid.naver.com/oauth2.0/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": NAVER_CLIENT_ID,
        "client_secret": NAVER_CLIENT_SECRET,
        "redirect_uri": CALLBACK_URL,
        "code": code,
        "state": state,
    }
    
    # 네이버에 토큰 요청 (GET 방식 사용)
    token_response = requests.get(token_url, params=payload)
    
    if token_response.status_code == 200:
        token_data = token_response.json()
        # access_token, refresh_token, expires_in 등의 정보가 담긴 토큰 데이터 반환
        return jsonify(token_data)
    else:
        return jsonify({
            "error": "Failed to get token", 
            "details": token_response.text
        }), token_response.status_code

if __name__ == '__main__':
    # Railway의 환경 변수 PORT가 자동 할당됩니다.
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
