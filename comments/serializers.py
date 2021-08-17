from bases.serializers import ModelSerializer
from comments.models import Comment, Review


class ReviewSerializer(ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'image', 'star1', 'star2', 'star3', 'star4', 'total_star', 'like']


class CommentSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'root', 'like']
