from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from bases.serializers import ModelSerializer
from posts.models import EcoCarping, Post
from camps.models import CampSite


class AutoCampPostForWeekendSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = ['id', 'tags', 'title', 'thumbnail', 'views']


class EcoCarpingSerializer(ModelSerializer):
    tags = TagListSerializerField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'latitude', 'longitude',
                  'image', 'title', 'text', 'tags', 'created_at']

    def get_created_at(self, data):
        return data.created_at.strftime("%Y-%m-%d %H:%M")


class AutoCampPostSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        re_ret = {}

        count = 0
        ret = super().to_representation(instance)
        re_ret["id"] = ret.pop("id")
        re_ret["created_at"] = ret.pop("created_at")
        re_ret["updated_at"] = ret.pop("updated_at")
        re_ret["title"] = ret.pop("title")
        re_ret["thumbnail"] = ret.pop("thumbnail")
        re_ret["views"] = ret.pop("views")
        re_ret["tags"] = ret.pop("tags")

        for i in range(3):
            camp = {}
            camp["text"] = ret[f"text{i+1}"]
            camp["image"] = ret[f"image{i+1}"]
            camp["source"] = ret[f"source{i+1}"]
            campsite_pk = ret[f"campsite{i+1}"]
            camp["sub_title"] = ret[f"sub_title{i+1}"]

            if campsite_pk is not None:
                campsite = CampSite.objects.get(id=campsite_pk)
                camp["name"] = campsite.name
                camp["address"] = campsite.address
                camp["phone"] = campsite.phone
                camp["type"] = campsite.type
                camp["oper_day"] = campsite.oper_day
                camp["website"] = campsite.website
                camp["sub_facility"] = campsite.sub_facility
                count += 1
            else:
                camp["address"] = ""
                camp["phone"] = ""
                camp["type"] = ""
                camp["oper_day"] = ""
                camp["website"] = ""
                camp["sub_facility"] = ""

            re_ret[f"campsite{i+1}"] = camp

        re_ret["count"] = count
        return re_ret
