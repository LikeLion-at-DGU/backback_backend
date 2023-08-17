from ssl import Purpose

from django.conf import settings
from rest_framework import serializers
from core.serializers import WriterSerializer
from .models import Banner, Completed, Exercise, Post, PostImage, Scrap, Comment


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
    likes_cnt = serializers.SerializerMethodField(read_only=True)
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

    def get_likes_cnt(self, instance):
        return instance.reactions.count()


class PostDetailSerializer(serializers.ModelSerializer):
    writer = WriterSerializer(read_only=True)
    likes_cnt = serializers.SerializerMethodField(read_only=True)
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
            "purpose",
            "exercise",
            "title",
            "images",
            "content",
            "likes_cnt",
            "comments_cnt",
            "is_liked",
            "is_clipped",
            "view_cnt",
            "type",
        ]
        read_only_fields = [
            "view_cnt",
        ]

    def get_likes_cnt(self, instance):
        return instance.reactions.count()

    def get_is_liked(self, instance):
        if (user := self.context["request"].user).is_authenticated:
            return instance.reactions.filter(completed__isnull=True, user=user).exists()
        return False

    def get_images(self, obj):
        images = obj.images.all()
        image_urls = [
            settings.BASE_URL + settings.MEDIA_URL + str(image.image)
            for image in images
        ]
        return image_urls

    def create(self, validated_data):
        user = self.context["request"].user
        profile = user.profile

        if profile.type == "COMMON" and validated_data.get("type") != "ORDINARY":
            raise serializers.ValidationError("해당 게시판에 작성 권한이 없습니다.")

        instance = Post.objects.create(**validated_data)
        image_set = self.context["request"].FILES
        for image_data in image_set.getlist("images"):
            PostImage.objects.create(post=instance, image=image_data)
        return instance

    def get_is_clipped(self, obj):
        if (user := self.context["request"].user).is_authenticated:
            return Scrap.objects.filter(user=user, post=obj).exists()
        return False

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
    is_liked = serializers.SerializerMethodField(read_only=True)

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

    def get_is_liked(self, instance):
        if (user := self.context["request"].user).is_authenticated:
            return instance.reactions.filter(completed__isnull=True, user=user).exists()
        return False


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


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            "id",
            "image",
            "priority",
        ]
