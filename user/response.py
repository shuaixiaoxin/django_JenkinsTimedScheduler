from rest_framework.response import Response


class CustomResponse(Response):
    def __init__(self, code, message, data=None, status=None, DataCount=None,
                 template_name=None, headers=None, exception=False, content_type=None):

        returnCode = code if isinstance(code, int) or isinstance(code, float) else str(code)
        # returnData = json.loads(data) if isinstance(data, dict) else data
        data = {
            "code": returnCode,
            "message": str(message),
            "data": data,
            "DataCount": DataCount,
        }
        super().__init__(data, status=status, template_name=template_name,
                         headers=headers, exception=exception, content_type=content_type)
