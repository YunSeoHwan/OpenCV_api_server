from types import NoneType
import cv2
from flask import Flask, request
import requests
import numpy as np
import re
from flask_restx import Api
from todo import Todo

# Flask 객체 인스턴스

app = Flask(__name__)

api = Api(
    app,
    title="OpenCV API Server",
    description="screenshotPath와 detectImagePath를 입력받아 detectImagePath image의 Center 좌표를 반환해줍니다.",
    terms_url="http://127.0.0.1:5000/image-position",
    license="License : MIT"
)

# Image변환 Class
class OpenCV():

    # URL -> image 변환 메소드
    def getUrlImage(self, url):

        # URL을 numpy배열로 처리
        # array는 변수 할당 시, 원본데이터 변경 x, asarray는 원본데이터까지 바뀜 -> imdecode
        # numpy 배열형태로 바이너리 데이터(시퀀스)를 받는다. content : 바이너리 원문 받음,
        # dtype은 부호없는 2^8 범위(RGB)까지 받음. 
        image_nparray = np.asarray(bytearray(requests.get(url).content), dtype=np.uint8)
        
        # OpenCV로 numpy -> image 변환
        # imdecode : 바이너리 type을 이미지화, 속성값 0은 Grayscale -> 이미지 처리 중간단계로 사용
        image = cv2.imdecode(image_nparray, 0)
        return image

    # Image center값 반환 메소드
    def detectImage(self, screenshotPath,detectImagePath):
        # URL 정규식 표현
        url = re.compile('^(https?://)[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/[a-zA-Z0-9-_/.?=]*')

        # URL 주소 에러가 발생시 예외처리
        if (url.match(screenshotPath)!= None) == False or (url.match(detectImagePath)!= None) == False:
            # 각각의 경우 대한 처리
            if url.match(screenshotPath) == None and url.match(detectImagePath) == None:
                return "3"
            elif url.match(screenshotPath) == None:
                return "1"
            elif url.match(detectImagePath) == None:
                return "2"
        elif url.match(screenshotPath)!= None and url.match(detectImagePath)!= None:
            sourceimage = self.getUrlImage(screenshotPath)
            template = self.getUrlImage(detectImagePath)
            
        # python url 정규식 사용
        # url error test해보기
        # 일반적인 경우(.png, .jpg ...)
        else:
            # imread : img 경로를 읽어와 3차원 행렬로 return 
            sourceimage = cv2.imread(screenshotPath, 0)
            template = cv2.imread(detectImagePath, 0)
            # Image값이 존재하지 않을 때 (-1, -1) 반환
            if type(sourceimage) == NoneType or type(template) == NoneType:
                return (-1,-1)
        
        # 찾을 이미지의 가로, 세로 너비 할당
        # 흑백 이미지의 경우 height, width를 받아옴. color는 channel(BGR)값까지
        # imread를 사용하면 거꾸로 값을 받아옴, 따라서 뒤에서부터 값 할당
        w, h=template.shape[::-1]

        # 흑백처리 메소드
        # 문자열로 받은 매개변수를 실행하는 함수, 가장 성능이 뛰어남(연산이 복잡).
        method = eval('cv2.TM_CCOEFF_NORMED')
        
        # 찾는이미지의 좌표값, 가중치 반환 메소드
        # 원본 이미지와 찾는 이미지의 매칭 위치탐색
        # 행렬로 res에 값 저장
        res = cv2.matchTemplate(sourceimage, template, method) 

        # 가장 비슷하지 않은 가중치, 비슷한 가중치, 가중치 낮은 왼쪽 위 모서리, 가중치 높은 왼쪽 위 모서리
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # 최댓값을 좌측 상단 좌표로 설정(x, y)
        top_left = max_loc
        
        # 찾은 이미지의 center값
        center = ((top_left[0] + int(w/2))/2, (top_left[1] + int(h/2))/2)

        return center

# @app.errorhandler(404)
# def handle(_error):
#     return make_response(jsonify({'error' : 'Not found'}), 500)
# POST Server
@app.route('/image-position', methods=['POST'])
def image_position():
    
    # json으로 request
    json = request.json

    # class 변수 할당
    oc = OpenCV()

    # center 반환 메소드
    # json으로 받은 url or png파일을 넘겨줌.
    center = oc.detectImage(json['baseImgPath'], json['detectImgPath'])

    # status
    if center[0] == -1 and center[1] == -1:
        # 입력값 없을 시 204 표시
        stats = 404
        error = "Image is None."

    elif center == "1":
        stats = 404
        error = "baseImgPath is Error"

    elif center == "2":
        stats = 404
        error = "detectImagePath is Error"

    elif center == "3":
        stats = 404
        error = "All path Error"
                
        
    else:
        stats = 201
        error = "Success"
    # 반환 형식

    # 정상처리 경우
    if type(center) is tuple:
        output={
            "status": stats,
            "data" : {
                'x':center[0],
                'y':center[1]
            }
        }

    # 예외경우
    else:
        output={
            "status": stats,
            "error": error,
            
        }        

    return(output)
api.add_namespace(Todo, '/image-position')
if __name__ == '__main__':
    # 코드 수정 시 반영
    app.run(debug=True)