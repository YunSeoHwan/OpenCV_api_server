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
todo_fields = Todo.model('detectImage', {  
    'screenshotPath': fields.String(description='URL or ImagePath', required=True, example="https://screenshot.com/11.png"),
    'detectImagePath': fields.String(description='URL or ImagePath', required=True, example="https://detectImage/11.png")
})

# 성공 model
todo_fields_success = Todo.model('success_output', {  
    "status": fields.Integer(required=True, example="200"),
    "x": fields.Integer(required=True, example="157.0"),
    "y": fields.Integer(required=True, example="12.0")
        
})

# value_none model
todo_fields_value_none = Todo.model('value_none_output',{
    "status": fields.Integer(required=True, example="201"),
    "x": fields.Integer(required=True, example="-1"),
    "y": fields.Integer(required=True, example="-1")
})

# swagger domain
@Todo.route('')
class TodoPost(Resource):
    @Todo.expect(todo_fields)
    @Todo.response(200, 'Success', todo_fields_success)
    @Todo.response(201, 'Value None', todo_fields_value_none)
    def post(self):
        """screenshotPath와 detectImagePath입력받아 Center 좌표를 반환합니다."""