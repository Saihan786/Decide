"""
URL configuration for decide project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from decide import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("join/", views.join_session, name="join_session_page"),
    path("join/submit-review/", views.submit_review, name="submit_review"),
    path("document/", views.write_document, name="write_doc_page"),
    path("document/save/", views.save_document, name="save_document"),
    path("document/submit/", views.submit_document, name="submit_document"),
    path("document/result/", views.result_phase, name="result_phase"),
]
