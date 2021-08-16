from bases.serializers import ModelSerializer
from comments.models import Comment, Like, Review, BookMark


class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = ['user']


class ReviewSerializer(ModelSerializer):
    like = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'image', 'star1', 'star2', 'star3', 'star4', 'total_star', 'like']


class CommentSerializer(ModelSerializer):
    like = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'root', 'like']


class BookMarkSerializer(ModelSerializer):
    class Meta:
        model = BookMark
        fields = ['user']
