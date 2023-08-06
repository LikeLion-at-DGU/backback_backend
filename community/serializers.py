from rest_framework import serializers
from .models import *


class CompletedSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False)
    writer = serializers.SerializerMethodField()

    def get_writer(self, instance):
        return {"id": instance.writer.id, "nickname": instance.writer.username}

    class Meta:
        model = Completed
        fields = [
            "writer",
            "title",
            "content",
            "image",
        ]
        read_only_fields = ["writer"]


class CompletedEditSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, read_only=True)
    writer = serializers.SerializerMethodField()

    def get_writer(self, instance):
        return {"id": instance.writer.id, "nickname": instance.writer.username}

    class Meta:
        model = Completed
        fields = [
            "writer",
            "title",
            "content",
            "image",
        ]
        read_only_fields = ["writer"]
