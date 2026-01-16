from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # 首页 - 实验室列表
    path('', views.laboratory_list, name='laboratory_list'),
    
    # 实验室详情
    path('laboratory/<int:lab_id>/', views.laboratory_detail, name='laboratory_detail'),
    
    # 预约相关
    path('reserve/<int:lab_id>/', views.make_reservation, name='make_reservation'),
    path('reservation/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    
    # 用户相关
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('profile/', views.user_profile, name='user_profile'),
    
    # 管理员相关
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/reservations/', views.admin_reservations, name='admin_reservations'),
    path('admin-panel/reservation/<int:reservation_id>/approve/', views.approve_reservation, name='approve_reservation'),
    path('admin-panel/reservation/<int:reservation_id>/reject/', views.reject_reservation, name='reject_reservation'),
    
    # 认证相关
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    
    # AJAX接口
    path('api/check-availability/', views.check_availability, name='check_availability'),
    path('api/laboratories/', views.laboratory_list_ajax, name='laboratory_list_ajax'),
]
