
from django.urls import path
from auth_app.api.v1 import CurrentUserView, UserLoginView,CookieTokenRefreshView,LogoutView, IsLogin


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="auth-login"),
    path("login/verify/", OtpVerifyView.as_view(), name="auth-login-verify"),
    path("is/login/", IsLogin.as_view(), name="is-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("refresh/cookie/", CookieTokenRefreshView.as_view(), name="auth-refresh-cookie"),
    path("user/me/", CurrentUserView.as_view(), name="auth-current-user"),



]
