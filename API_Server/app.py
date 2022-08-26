from types import NoneType
import ftplib
import cv2
from flask import Flask, request, make_response, jsonify
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
    def check_input(self, input):
        # URL 정규식 표현
        url = re.compile('^(https?://)[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/[a-zA-Z0-9-_/.?=]*')
    
        # FTP 정규식
        ftp = re.compile('^(ftp://)')

        # 사진, url 체크
        if url.match(input) != None:
            return "http"
        
        elif ftp.match(input) != None:
            return "ftp"
        else:
            return "img"

    # FTP Server 다운 메소드
    def ftp_server_down(self, ftp_url):

        # 정규식
        f = "\w+"

        # ftp url 분리
        ftp_list = re.findall(f, ftp_url)
        user = ftp_list[1]
        pwd = ftp_list[2]
        host = ftp_list[3] +"."+ ftp_list[4] +"."+ ftp_list[5] +"."+ ftp_list[6]
        port = int(ftp_list[7])
        path = ftp_list[8:]
        real_path = ""

        for i in range(len(path)):
            real_path = real_path + "/" + path[i]
        
        ftp = ftplib.FTP(timeout=30)

        # 서버 접속 예외처리
        try:
            ftp.connect(host, port)
            ftp.login(user, pwd)

        # BaseImage 다운
            if "BaseImage" in real_path:
                ftp.cwd(real_path)
                list = ftp.nlst()

                for file in list:
                    with open(r'C:\CLOUDXPM-imageDetectAPI\API_Server\image\BaseImage\{}'.format(file), 'wb') as f:
                        r = ftp.retrbinary(f"RETR {file}", f.write)
                
                # 파일 닫기
                ftp.close()
                
            # DetectImage 다운
            elif "DetectImage" in real_path:
                ftp.cwd(real_path)

                list = ftp.nlst()
                for file in list:
                    with open(r'C:\CLOUDXPM-imageDetectAPI\API_Server\image\DetectImage\{}'.format(file), 'wb') as f:
                        r = ftp.retrbinary(f"RETR {file}", f.write)

                # 파일 닫기
                ftp.close()

        except ConnectionRefusedError:
            return "4"     

        except ftplib.error_perm:
            return "6"   
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
    def detectImage(self, screenshotPath, detectImagePath):
        sourceimage = self.check_input(screenshotPath)
        template = self.check_input(detectImagePath)

        # 각 경우에 대한 예외처리
        try:
            if sourceimage == "http":
                sourceimage = self.getUrlImage(screenshotPath)

            elif sourceimage == "img":
                sourceimage = cv2.imread(screenshotPath, 0)

                if type(sourceimage) == NoneType:
                    return "1"

            elif sourceimage == "ftp":
                f = self.ftp_server_down(screenshotPath)
                if f == "4":
                    return "4"

                elif f == "6":
                    return "6"    

                else:
                    sourceimage = cv2.imread("C:/CLOUDXPM-imageDetectAPI/API_Server/image/BaseImage/a.PNG", 0)
            
            if template == "http":
                template = self.getUrlImage(detectImagePath)

            elif template == "img":
                template = cv2.imread(detectImagePath, 0)

                if type(template) == NoneType:
                    return "2"

            elif template == "ftp":
                f = self.ftp_server_down(detectImagePath)
                if f == "4":
                    return "4"

                elif f == "6":
                    return "6"

                else:
                    template = cv2.imread("C:/CLOUDXPM-imageDetectAPI/API_Server/image/DetectImage/bb.PNG", 0)       

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

        # 예외처리
        except AttributeError:
            return "3"

        except requests.exceptions.ConnectionError:
            return "4"

        except cv2.error:
            return "5"
        
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
    if center == "1":
        msg = "Check your baseImgPath"
        error = "baseImgPath is Error"

    elif center == "2":
        msg = "Check your detectImagePath"
        error = "detectImagePath is Error"

    elif center == "3":
        return make_response(jsonify({'AttributeError' : 'Check your url'}), 500)            

    elif center == "4":
        return make_response(jsonify({'ConnectionError' : 'Check your url'}), 404)

    elif center == "5":
        return make_response(jsonify({'cv2.error' : 'Check your url'}), 500)

    elif center == "6":
        return make_response(jsonify({'FTP_Path_Error' : 'Check your FTP_path'}), 500)

    else:
        stats = "Success"
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
        return output

    # 예외경우
    else:
        output={
            "message": msg,
            "error": error
        }
        return make_response(jsonify(output), 400)       

api.add_namespace(Todo, '/image-position')

if __name__ == '__main__':
    # 코드 수정 시 반영
    app.run(debug=True)