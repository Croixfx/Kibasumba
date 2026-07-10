from django.urls import path

from . import views

urlpatterns = [
    path("request-otp/", views.RequestOTPView.as_view(), name="request-otp"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify-otp"),
    path("set-password/", views.SetPasswordView.as_view(), name="set-password"),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "admin/create-staff/",
        views.CreateStaffView.as_view(),
        name="create-staff",
    ),
    path("me/", views.MeView.as_view(), name="me"),
    path(
        "midwife/create-woman/",
        views.CreateWomanView.as_view(),
        name="create-woman",
    ),
]
