from rest_framework.views import APIView
from bases.response import APIResponse


class UserPostFailCallbackAPIView(APIView):

    def get(self, request):
        response = APIResponse(success=False, code=400)

        print(request)

        return response.response()


class UserPostCancelCallbackAPIView(APIView):

    def get(self, request):
        response = APIResponse(success=False, code=400)
        print(request.data)
        return response.response()
