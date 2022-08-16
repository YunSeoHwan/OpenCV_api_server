from types import NoneType
# OpenCV
import cv2
from flask import Flask, request
import requests
import numpy as np

# Flask 객체 인스턴스
app = Flask(__name__)

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
        
        # http 경우 URL 변환 메소드로 image처리
        if "http" in screenshotPath or detectImagePath:
            if "http" in screenshotPath and detectImagePath:
                sourceimage = self.getUrlImage(screenshotPath)
                template = self.getUrlImage(detectImagePath)
            elif "http" in screenshotPath:
                sourceimage = self.getUrlImage(screenshotPath)
                template = cv2.imread(detectImagePath,0)
            else:
                sourceimage = cv2.imread(screenshotPath,0)
                template = self.getUrlImage(detectImagePath)
        
        # 일반적인 경우
        else:
            # imread : img 경로를 읽어와 3차원 행렬로 return 
            sourceimage = cv2.imread(screenshotPath,0)
            template = cv2.imread(detectImagePath,0)

            # Image값이 존재하지 않을 때 (-1, -1) 반환
            if type(sourceimage) == NoneType or type(template) == NoneType:
                return (-1,-1)

        # 찾을 이미지의 가로, 세로 너비 할당
        w, h=template.shape[::-1]       # 설

        # 흑백처리 메소드
        # 문자열로 받은 매개변수를 실행하는 함수
        method = eval('cv2.TM_CCOEFF_NORMED')
        
        # 찾는이미지의 좌표값, 가중치 반환 메소드
        # 행렬로 res에 값 저장
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
    # json으로 받은 url or png파일을 넘겨줌.
    center = oc.detectImage(json['baseImgPath'], json['detectImgPath'])

    # status
    if center[0] == -1 and center[1] == -1:
        # 입력값 없을 시 201 표시
        stats = 201
    else:
        stats = 200
    # 반환 형식
    output={
        "status": stats,
        "data" : {
            'x':center[0],
            'y':center[1]
        }
    }

    return(output)

if __name__ == '__main__':
    # 코드 수정 시 반영
    app.run(debug=True)