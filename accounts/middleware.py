from rest_framework_simplejwt.tokens import RefreshToken


class AdminJWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path.startswith("/admin/"):
            refresh = RefreshToken.for_user(request.user)
            token = str(refresh.access_token)
            response = self.get_response(request)
            response.set_cookie(
                "access_token", token, max_age=60 * 60 * 24 * 14, httponly=True
            )
            response.set_cookie("uid", request.user.id, max_age=60 * 60 * 24 * 14)
            return response

        return self.get_response(request)
