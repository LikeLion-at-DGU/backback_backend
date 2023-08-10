import string
from json import JSONDecodeError
import json
import os

from django.contrib.auth.models import User
from django.http import JsonResponse
import requests
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

BASE_URL = os.getenv("BASE_URL")
GOOGLE_CALLBACK_URI = BASE_URL + "api/accounts/google/login/callback/"
KAKAO_CALLBACK_URI = BASE_URL + "api/accounts/kakao/login/callback/"


def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}"
    )


def google_callback(request):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    code = request.GET.get("code")
    state = get_random_string(32, allowed_chars=string.ascii_letters + string.digits)

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

    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}api/accounts/google/login/finish/", data=data
        )
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)
    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "email exists but not social user"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = User.objects.get(email=email)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    response_data = {
        "message": "Login Success",
        "access_token": access_token,
        "refresh_token": str(refresh),
    }
    response = JsonResponse(response_data)
    response.set_cookie("access_token", access_token, max_age=60 * 60 * 2)
    return response


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


def kakao_login(request):
    rest_api_key = os.getenv("KAKAO_REST_API_KEY")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


def kakao_callback(request):
    rest_api_key = os.getenv("KAKAO_REST_API_KEY")
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
    uid = profile_json.get("id")
    username = "kakao_" + str(uid)  # username 겹치는 문제 해결 위해 수정 (1)
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
    except User.DoesNotExist:  # username 겹치는 문제 해결 위해 수정 (2)
        user = User.objects.create(username=username)
        SocialAccount.objects.create(
            user=user,
            uid=uid,
            extra_data=profile_json,
            date_joined=profile_json.get("connected_at"),
            last_login=timezone.now(),
            provider="kakao",
        )
    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "user exists but not social user"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = User.objects.get(username=username)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    response_data = {
        "message": "Login Susccess",
        "access_token": access_token,
        "refresh_token": str(refresh),
    }
    response = JsonResponse(response_data)
    response.set_cookie("access_token", access_token, max_age=60 * 60 * 2)
    return response


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI
