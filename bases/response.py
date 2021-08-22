from django.http import JsonResponse


class APIResponse():
    success = False
    code = ""

    def __init__(self, success, code):
        self.succes = success
        self.code = code

    def format(self):
        return {
            'success': self.success,
            'code': self.code,
            'data': []
        }

    def response(self, data, status):
        form = self.format()
        if data:
            form['data'] = data
        return JsonResponse(form, status=status)
