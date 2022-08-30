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
    "message": fields.Integer(description="400",required=True),
    "Error": fields.String(description="Error name", required=True,example="Error name")
})

todo_fields_cv2_error = Todo.model('cv2_error_output',{
    "cv2.Error": fields.String(description="Check your URL", required=True, example="Check your URL")
})

todo_fields_connect_error = Todo.model('Connect_error_output',{
    "ConnectionError": fields.String(description="Check your URL", example="Check your URL", required=True)
})

todo_fields_internal_error = Todo.model('Internal_error_output',{
    "Error name": fields.String(description="Error message", example="Error message", required=True)
})

# swagger domain
@Todo.route('')
class TodoPost(Resource):
    @Todo.expect(todo_fields)
    @Todo.response(201, 'Success', todo_fields_success)
    @Todo.response(204, 'Value None', todo_fields_value_none)
    @Todo.response(400, 'URL Error', todo_fields_url_error)
    @Todo.response(404, 'Connect Error', todo_fields_connect_error)
    @Todo.response(500, 'Internal Error', todo_fields_internal_error) 
    # @Todo.response(501, 'Attribute Error', todo_fields_attribute_error)
    # @Todo.response(502, )
    def post(self):
        """baseImgPath detectImgPath Center 좌표를 반환합니다."""