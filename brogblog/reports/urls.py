from django.urls import path
from .views import ReportBlogListView, HandleReportBlogView

urlpatterns = [
    path('', ReportBlogListView.as_view(), name='report-list'),
    path('handle/<int:report_id>/', HandleReportBlogView.as_view(), name='handle-report-blog'),
]
