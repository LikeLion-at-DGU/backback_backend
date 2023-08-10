from rest_framework import serializers
from core.serializers import WriterSerializer
from .models import *


class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = PostImage
        fields = "__all__"


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = "__all__"


class PurposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purpose
        fields = "__all__"


class PostListSerializer(serializers.ModelSerializer):
    writer = WriterSerializer(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField()
    content = serializers.CharField(write_only=True)
    content_short = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "created_at",
            "updated_at",
            "writer",
            "title",
            "content",
            "content_short",
            "likes_cnt",
            "comments_cnt",
            "view_cnt",
        ]
        read_only_fields = [
            "view_cnt",
        ]

    def get_content_short(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    def get_comments_cnt(self, instance):
        return instance.comments.count()


class PostDetailSerializer(serializers.ModelSerializer):
    writer = WriterSerializer(read_only=True)
    purposes = PurposeSerializer(many=True)
    exercises = ExerciseSerializer(many=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    is_clipped = serializers.SerializerMethodField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "created_at",
            "updated_at",
            "writer",
            "purposes",
            "exercises",
            "title",
            "images",
            "content",
            "likes_cnt",
            "comments_cnt",
            "is_liked",
            "is_clipped",
            "view_cnt",
        ]
        read_only_fields = [
            "view_cnt",
        ]

    def get_is_liked(self, instance):
        return instance.reactions.filter(
            completed__isnull=True, user=self.context["request"].user
        ).exists()

    def get_images(self, obj):
        image = obj.images.all()
        return PostImageSerializer(instance=image, many=True, context=self.context).data

    def create(self, validated_data):
        instance = Post.objects.create(**validated_data)
        image_set = self.context["request"].FILES
        for image_data in image_set.getlist("image"):
            PostImage.objects.create(post=instance, image=image_data)
        return instance

    def get_is_clipped(self, obj):
        user = self.context["request"].user
        return Scrap.objects.filter(user=user, post=obj).exists()

    def get_comments_cnt(self, instance):
        return instance.comments.count()


class ScrapSerializer(serializers.ModelSerializer):
    post = PostListSerializer()

    class Meta:
        model = Scrap
        fields = "__all__"


class CompletedListCreateSerializer(serializers.ModelSerializer):
    writer = WriterSerializer(read_only=True)
    image = serializers.ImageField(use_url=True)
    title = serializers.CharField(write_only=True)
    content = serializers.CharField(write_only=True)

    class Meta:
        model = Completed
        fields = [
            "writer",
            "id",
            "image",
            "title",
            "content",
        ]
        read_only_fields = [
            "writer",
        ]


class CompletedSerializer(serializers.ModelSerializer):
    writer = WriterSerializer(read_only=True)
    image = serializers.ImageField(use_url=True, read_only=True)
    likes_cnt = serializers.SerializerMethodField()

    class Meta:
        model = Completed
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "writer",
            "likes_cnt",
            "is_private",
        ]

    def get_likes_cnt(self, instance):
        return instance.reactions.count()


class CommentSerializer(serializers.ModelSerializer):
    writer = WriterSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "writer",
            "id",
            "content",
            "created_at",
        ]
        read_only_fields = ["post"]
