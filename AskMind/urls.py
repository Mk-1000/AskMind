from django.urls import path
from question_answer import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.search_question, name='ask_question'),
    # Add this URL pattern for the favicon
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=staticfiles_storage.url("favicon.ico"),
            permanent=False,
        ),
        name="favicon",
    ),
]
