from django.http import JsonResponse


class APIResponse():
    success = False
    code = 0
    error_message = ""

    def __init__(self, success, code):
        self.succes = success
        self.code = code

    def format(self):
        return {
            'success': self.success,
            'code': self.code,
            'data': [],
            'error_message': ""
        }

    def response(self, data, error_message, status):
        form = self.format()
        if data:
            form['data'] = data
        if error_message:
            form['error_message'] = error_message

        return JsonResponse(form, status=status)
