from django.urls import path

from . import midwife_views, views

urlpatterns = [
    path("create/", views.CreatePregnancyView.as_view(), name="pregnancy-create"),
    path("active/", views.ActivePregnancyView.as_view(), name="pregnancy-active"),
    path("update/", views.UpdatePregnancyView.as_view(), name="pregnancy-update"),
    path(
        "download-card/",
        views.DownloadCardView.as_view(),
        name="pregnancy-download-card",
    ),
    path(
        "midwife/woman-record/",
        midwife_views.WomanRecordView.as_view(),
        name="midwife-woman-record",
    ),
    path(
        "midwife/create-or-update/",
        midwife_views.CreateOrUpdatePregnancyView.as_view(),
        name="midwife-create-or-update",
    ),
    path(
        "midwife/anc-visit/",
        midwife_views.ANCVisitUpsertView.as_view(),
        name="midwife-anc-visit",
    ),
]
