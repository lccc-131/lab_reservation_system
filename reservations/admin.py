from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Laboratory, TimeSlot, Reservation, UserProfile


@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'location', 'capacity', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'location', 'description']
    list_editable = ['is_active', 'category']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'category', 'location', 'capacity')
        }),
        ('详细信息', {
            'fields': ('description', 'equipment')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['laboratory', 'get_weekday_display', 'start_time', 'end_time', 'is_available']
    list_filter = ['laboratory', 'weekday', 'is_available']
    list_editable = ['is_available']
    ordering = ['laboratory', 'weekday', 'start_time']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'laboratory', 'date', 'start_time', 'end_time', 'status', 'created_at']
    list_filter = ['status', 'laboratory', 'date', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'laboratory__name']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'laboratory', 'date', 'start_time', 'end_time', 'purpose')
        }),
        ('状态管理', {
            'fields': ('status', 'admin_comment')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'laboratory')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户信息'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# 设置admin界面标题
admin.site.site_header = '实验室预约管理系统'
admin.site.site_title = '实验室预约管理'
admin.site.index_title = '欢迎使用实验室预约管理系统'
