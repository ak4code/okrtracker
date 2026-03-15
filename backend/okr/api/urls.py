from django.urls import path

from okr.api.views import (
    CheckInDetailAPIView,
    KeyResultCheckInListAPIView,
    KeyResultDetailAPIView,
    OkrCommentListAPIView,
    OkrDetailAPIView,
    OkrKeyResultListAPIView,
    OkrListAPIView,
    QuarterDetailAPIView,
    QuarterListAPIView,
)

app_name = 'okr_api'

urlpatterns = [
    path('quarters/', QuarterListAPIView.as_view(), name='quarter-list'),
    path('quarters/<int:quarter_id>/', QuarterDetailAPIView.as_view(), name='quarter-detail'),
    path('okrs/', OkrListAPIView.as_view(), name='okr-list'),
    path('okrs/<int:okr_id>/', OkrDetailAPIView.as_view(), name='okr-detail'),
    path('okrs/<int:okr_id>/comments/', OkrCommentListAPIView.as_view(), name='okr-comment-list'),
    path('okrs/<int:okr_id>/key-results/', OkrKeyResultListAPIView.as_view(), name='okr-key-result-list'),
    path('check-ins/<int:check_in_id>/', CheckInDetailAPIView.as_view(), name='check-in-detail'),
    path('key-results/<int:key_result_id>/', KeyResultDetailAPIView.as_view(), name='key-result-detail'),
    path(
        'key-results/<int:key_result_id>/check-ins/',
        KeyResultCheckInListAPIView.as_view(),
        name='key-result-check-in-list',
    ),
]
