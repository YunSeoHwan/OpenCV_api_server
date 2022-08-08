from flask import Flask
from flask_restx import Api
from todo import Todo

# Flask 객체 인스턴스
app = Flask(__name__)

# swagger 객체생성
api = Api(
    app,
    title="OpenCV API Server",
    description="screenshotPath와 detectImagePath를 입력받아 detectImagePath image의 Center 좌표를 반환해줍니다.",
    terms_url="http://127.0.0.1:5000/image-position",
    license="License : MIT"
)

# Swagger namespace 생성
api.add_namespace(Todo, '/image-position')

if __name__ == '__main__':
    # 코드 수정 시 반영
    app.run(debug=True, port=80)