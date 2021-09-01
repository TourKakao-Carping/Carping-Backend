from django.http import JsonResponse


class APIResponse():
    success = False
    code = 400
    error_message = ""

    def __init__(self, success, code):
        self.success = success
        self.code = code

    def format(self):
        return {
            'success': self.success,
            'code': self.code,
            'data': [],
            'error_message': ""
        }

    def response(self, *args, **kwargs):
        form = self.format()

        data = kwargs.get("data")
        error_message = kwargs.get("error_message")

        if data:
            form['data'] = data
        if error_message:
            form['error_message'] = error_message

        return JsonResponse(form)
