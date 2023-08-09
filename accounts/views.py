from json import JSONDecodeError
import json
from django.http import JsonResponse
import requests
from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Profile
from .serializers import *
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.models import SocialAccount


state = "awefwefew"
BASE_URL = "http://127.0.0.1:8000/"
GOOGLE_CALLBACK_URI = BASE_URL + "api/accounts/google/login/callback/"
KAKAO_CALLBACK_URI = BASE_URL + "api/accounts/kakao/login/callback/"


def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = (
        "709196576668-sv64ue7f2rqaq3j3j298cvo2is328l92.apps.googleusercontent.com"
    )
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}"
    )


def google_callback(request):
    client_id = (
        "709196576668-sv64ue7f2rqaq3j3j298cvo2is328l92.apps.googleusercontent.com"
    )
    client_secret = "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"
    code = request.GET.get("code")

    # 1. 받은 코드로 구글에 access token 요청
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
    )

    ### 1-1. json으로 변환 & 에러 부분 파싱
    try:
        token_req_json = token_req.json()
    except json.JSONDecodeError as e:
        # JSON 디코딩 에러가 발생했을 때 처리할 내용
        print("JSON decoding error:", e)

    ### 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get("access_token")

    #################################################################

    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    )
    email_req_status = email_req.status_code

    ### 2-1. 에러 발생 시 400 에러 반환
    if email_req_status != 200:
        return JsonResponse(
            {"err_msg": "failed to get email"}, status=status.HTTP_400_BAD_REQUEST
        )

    ### 2-2. 성공 시 이메일 가져오기
    email_req_json = email_req.json()
    email = email_req_json.get("email")

    # return JsonResponse({'access': access_token, 'email':email})

    #################################################################

    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        user = User.objects.get(email=email)

        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != "google":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}api/accounts/google/login/finish/", data=data
        )
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}api/accounts/google/login/finish/", data=data
        )
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)
    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "email exists but not social user"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


def kakao_login(request):
    rest_api_key = "6556fdbf5f3e592092dbd5678bb76f64"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


def kakao_callback(request):
    rest_api_key = "6556fdbf5f3e592092dbd5678bb76f64"
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}"
    )
    try:
        token_req_json = token_req.json()
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    kakao_account = profile_json.get("kakao_account")
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    username = kakao_account.get("nickname")
    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(username=username)
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse(
                {"err_msg": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "kakao":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}api/accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}api/accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


class ProfileViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(["POST"], detail=True, url_path="follow")
    @permission_classes([IsAuthenticated])
    def follow(self, request, pk=None):
        user = request.user
        followed_user = self.get_object()

        if user.profile == followed_user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.profile in followed_user.followers.all():
            user.profile.following.remove(followed_user)
        else:
            user.profile.following.add(followed_user)
        return Response({}, status=status.HTTP_200_OK)

    @action(["POST"], detail=True, url_path="report")
    @permission_classes([IsAuthenticated])
    def report(self, request, pk=None):
        profile = self.get_object()
        reason = request.data.get("reason")

        if profile == request.user.profile:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ProfileReport.objects.create(
            writer=request.user, reason=reason, profile=profile
        )
        return Response()


class MeViewSet(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch", "options"]

    def get_object(self):
        if not self.request.user.is_active:
            raise PermissionDenied
        return get_object_or_404(
            User.objects.select_related("profile"), id=self.request.user.id
        )

    def get(self, request, *args, **kwargs):
        instance: User = self.get_object()
        serializer = self.get_serializer(instance.profile)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance: User = self.get_object()
        nickname = request.data.get("nickname")
        intro = request.data.get("intro")

        profile = instance.profile
        profile.nickname = nickname
        profile.intro = intro
        profile.save()

        serializer = self.get_serializer(instance.profile)
        return Response(serializer.data)
