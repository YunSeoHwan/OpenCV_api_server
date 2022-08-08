from types import NoneType
# OpenCV
import cv2
from flask import Flask, request
import requests
import numpy as np
from flask_restx import Api, Resource
from todo import Todo

# Flask 객체 인스턴스
app = Flask(__name__)

# swagger 경로설정
api = Api(
    app,
    version='0.1',
    title="OpenCV API Server",
    description="JustKode's Todo API Server!",
    terms_url="/",
    license="MIT"
)


api.add_namespace(Todo, '/todos')

# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=80)
@api.route('/hello')  # 데코레이터 이용, '/hello' 경로에 클래스 등록
class HelloWorld(Resource):
    def get(self):  # GET 요청시 리턴 값에 해당 하는 dict를 JSON 형태로 반환
        return {"hello": "world!"}
# Image변환 Class
class OpenCV():

    # URL -> image 변환 메소드
    def getUrlImage(self,url):

        # URL을 numpy배열로 처리
        image_nparray = np.asarray(bytearray(requests.get(url).content), dtype=np.uint8)
        
        # OpenCV로 numpy -> image 변환
        image = cv2.imdecode(image_nparray, 0)
        return image

    # Image center값 반환 메소드
    def detectImage(self, screenshotPath,detectImagePath):
        
        # http 경우 URL 변환 메소드로 image처리
        if "http" in screenshotPath and detectImagePath:
            sourceimage = self.getUrlImage(screenshotPath)
            template = self.getUrlImage(detectImagePath)
        
        # 일반적인 경우
        else:
            sourceimage = cv2.imread(screenshotPath,0)
            template = cv2.imread(detectImagePath,0)

            # Image값이 존재하지 않을 때 (-1, -1) 반환
            if type(sourceimage) == NoneType or type(template) == NoneType:
                return (-1,-1)

        # 찾을 이미지의 가로, 세로 너비 할당
        w, h=template.shape[::-1]

        # 흑백처리 메소드
        method = eval('cv2.TM_CCOEFF_NORMED')
        # 찾는이미지의 좌표값, 가중치 반환 메소드
        res = cv2.matchTemplate(sourceimage, template, method)

        # 가장 비슷하지 않은 가중치, 비슷한 가중치, 가중치 낮은 왼쪽 위 모서리, 가중치 높은 왼쪽 위 모서리
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # 최댓값을 좌측 상단 좌표로 설정(x, y)
        top_left = max_loc
        
        # 찾은 이미지의 center값
        center = ((top_left[0] + int(w/2))/2, (top_left[1] + int(h/2))/2)

        return center

# POST Server
@app.route('/image-position', methods=['POST'])
def image_position():

    # json으로 request
    json = request.json

    # class 변수 할당
    oc = OpenCV()

    # center 반환 메소드
    center = oc.detectImage(json['baseImgPath'], json['detectImgPath'])

    # 반환 형식
    output={
        "status": 200,
        "data" : {
            'x':center[0],
            'y':center[1]
        }
    }

    return(output)

if __name__ == '__main__':
    # 코드 수정 시 반영
    app.run(debug=True, host='0.0.0.0', port=80)