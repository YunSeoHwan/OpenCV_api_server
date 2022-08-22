from doctest import Example
from flask import request
from flask_restx import Resource, Namespace, fields


todos = {}
count = 1

# namespace 생성
Todo = Namespace(
     name="OpenCV",
    description="OpenCV image 좌표처리 API",
)

# 입력값 model
todo_fields = Todo.model('ImgPath', {  
    'baseImgPath': fields.String(description='URL or ImagePath', required=True, example="https://screenshot.com/11.png"),
    'detectImgPath': fields.String(description='URL or ImagePath', required=True, example="https://detectImage/11.png")
})

# 성공 model
todo_fields_success = Todo.model('success_output', {  
    "status": fields.Integer(required=True, example="201"),
    "x": fields.Integer(required=True, example="157.0"),
    "y": fields.Integer(required=True, example="12.0")
        
})

# value_none model
todo_fields_value_none = Todo.model('value_none_output',{
    "status": fields.Integer(required=True, example="204"),
    "x": fields.Integer(required=True, example="-1"),
    "y": fields.Integer(required=True, example="-1")
})

# url error model
todo_fields_url_error = Todo.model('url_error_output',{
    "status": fields.Integer(description="404",required=True, example="404"),
    "contents": fields.String(description="Error name", required=True, example="detectImagePath is Error")
})

# swagger domain
@Todo.route('')
class TodoPost(Resource):
    @Todo.expect(todo_fields)
    @Todo.response(201, 'Success', todo_fields_success)
    @Todo.response(204, 'Value None', todo_fields_value_none)
    @Todo.response(404, 'URL Error', todo_fields_url_error)

    def post(self):
        """baseImgPath detectImgPath Center 좌표를 반환합니다."""