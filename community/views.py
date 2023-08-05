from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from .models import Completed, Reaction, CompletedReport
from .serializers import CompletedListSerializer, CompletedSerializer
from .paginations import CompletedPagination
from .permissions import IsOwnerOrReadOnly

from django.shortcuts import get_object_or_404


class CompleletedViewSet(viewsets.ModelViewSet):
    queryset = Completed.objects.all()
    pagination_class = CompletedPagination
    parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return CompletedListSerializer
        return CompletedSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy", "completed_reports"]:
            return [IsOwnerOrReadOnly()]
        elif self.action in ["likes"]:
            return [IsAuthenticated()]
        return []

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(writer=request.user)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True, url_path="reports")
    def completed_reports(self, request, pk=None):
        completed = self.get_object()
        CompletedReport.objects.create(
            writer=request.user, completed=completed, reason=request.POST["reason"]
        )
        return Response()

    @action(methods=["POST"], detail=True)
    def likes(self, request, pk=None):
        completed = self.get_object()
        if reaction := Reaction.objects.filter(
            user=request.user, post__isnull=True
        ).first():
            reaction.delete()
        else:
            Reaction.objects.create(user=request.user, completed=completed)
        return Response()
