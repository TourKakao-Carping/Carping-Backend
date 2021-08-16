from rest_framework import viewsets
from rest_framework.response import Response

from camps.models import AutoCamp
from camps.serializers import AutoCampSerializer, AutoCampMainSerializer


class AutoCampViewSet(viewsets.ModelViewSet):
    serializer_class = AutoCampSerializer
    queryset = AutoCamp.objects.all()

    # 메인에서 보여줄 최근 10개 신규 차박지
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())[:10]
        serializer = AutoCampMainSerializer(queryset, many=True)
        return Response(serializer.data)
