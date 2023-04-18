from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('details/<int:number>', views.detail, name='details'),
    path('cases/<int:number>', views.cases, name='cases'),
    path('weekly/<str:project>', views.weekly, name='weekly'),
    path('failed/<int:number>', views.failed, name='failed'),
    path('jenkins_full/', views.jenkins_full, name='jenkins_full'),
    path('jenkins_simulation/', views.jenkins_simulation, name='jenkins_simulation'),
    path('get_report/<str:project>', views.get_report, name='get_report'),
    path('get_weekly/<str:project>', views.get_weekly, name='get_weekly'),
    path('get_receivers/<str:project>', views.get_receivers, name='get_receivers'),
    path('update_weekly/<str:project>', views.update_weekly, name='update_weekly'),
    path('get_slurm_queue_failed/<str:project>', views.get_slurm_queue_failed, name='get_slurm_queue_failed'),
    path('index_selectbox/<int:num>', views.index_selectbox, name='index_selectbox'),
    path('get_previous/<int:num>/<str:build_date>', views.get_previous, name='get_previous'),
    path('previous_cases/<int:number>/<str:build_date>', views.previous_cases, name='previous_cases'),
    path('autocomplete_list/<int:num>', views.autocomplete_list, name='autocomplete_list'),
    path('autocomplete_case/<int:num>', views.autocomplete_case, name='autocomplete_case'),
    path('search_list/<int:num>/<str:test_name>', views.search_list, name='search_list'),
    path('search_case/<int:num>/<str:test_name>', views.search_case, name='search_case'),
    path('delete/', views.delete, name='delete'),
]