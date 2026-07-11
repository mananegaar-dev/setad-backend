from drf_spectacular.utils import extend_schema
# from tasks.tag import PROFILE

from rest_framework.generics import ListAPIView

# serializer:
from excel_app.api.v1.serializer.area import AreaSerializer

# models;
from excel_app.models import Area

# permission:
from permission import AreaAccessMixin

@extend_schema(
         responses={200: AreaSerializer(many=True)},
        summary="لیست منطقه ها",
        tags=["Area"],
        )   
class AreaView(ListAPIView):
    serializer_class = AreaSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="super_admin").exists():
            return Area.objects.all()

        return user.areas.all()