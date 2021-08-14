from rest_framework.response import Response
from django.http import JsonResponse


class ApiResopnse():
    success = False
    message = ''
    error_code = ''

    def __init__(self, success, message, error_code):
        self.success = success
        self.message = message
        self.error_code = error_code

    def format(self):
        return {
            'success': self.success,
            'meta': {
                'message': self.message,
                'error_code': self.error_code
            },
        }

    def response(self, status=200):
        return Response(self.format(), status=status)

    def json_response(self, data):
        if data:
            self.format()['data'] = data
        return JsonResponse(self.format())


# class APIResponse(object):
#     success = False
#     status_co
