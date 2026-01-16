from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta


class Laboratory(models.Model):
    """实验室模型"""
    CATEGORY_CHOICES = [
        ('physics', '物理'),
        ('chemistry', '化学'),
        ('biology', '生物'),
        ('computer', '计算机'),
        ('engineering', '工程'),
        ('mathematics', '数学'),
        ('electronics', '电子'),
        ('materials', '材料'),
        ('environmental', '环境'),
        ('medical', '医学'),
        ('other', '其他'),
    ]

    name = models.CharField(max_length=100, verbose_name="实验室名称")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="科目分类")
    location = models.CharField(max_length=200, verbose_name="位置")
    capacity = models.PositiveIntegerField(verbose_name="容量")
    equipment = models.TextField(verbose_name="设备描述", blank=True)
    description = models.TextField(verbose_name="实验室描述", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="是否可用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "实验室"
        verbose_name_plural = "实验室"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def get_category_icon(self):
        """根据分类返回对应的图标"""
        icon_map = {
            'physics': 'fas fa-atom',
            'chemistry': 'fas fa-flask',
            'biology': 'fas fa-dna',
            'computer': 'fas fa-desktop',
            'engineering': 'fas fa-cogs',
            'mathematics': 'fas fa-calculator',
            'electronics': 'fas fa-microchip',
            'materials': 'fas fa-cube',
            'environmental': 'fas fa-leaf',
            'medical': 'fas fa-heartbeat',
            'other': 'fas fa-microscope',
        }
        return icon_map.get(self.category, 'fas fa-microscope')

    def get_category_color(self):
        """根据分类返回对应的颜色"""
        color_map = {
            'physics': '#6f42c1',      # 紫色
            'chemistry': '#fd7e14',    # 橙色
            'biology': '#198754',      # 绿色
            'computer': '#0d6efd',     # 蓝色
            'engineering': '#dc3545',  # 红色
            'mathematics': '#20c997',  # 青色
            'electronics': '#ffc107',  # 黄色
            'materials': '#6c757d',    # 灰色
            'environmental': '#28a745', # 深绿色
            'medical': '#e83e8c',      # 粉色
            'other': '#495057',        # 深灰色
        }
        return color_map.get(self.category, '#495057')


class TimeSlot(models.Model):
    """时间段模型"""
    WEEKDAY_CHOICES = [
        (0, '周一'),
        (1, '周二'),
        (2, '周三'),
        (3, '周四'),
        (4, '周五'),
        (5, '周六'),
        (6, '周日'),
    ]

    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, verbose_name="实验室")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, verbose_name="星期")
    start_time = models.TimeField(verbose_name="开始时间")
    end_time = models.TimeField(verbose_name="结束时间")
    is_available = models.BooleanField(default=True, verbose_name="是否可预约")

    class Meta:
        verbose_name = "时间段"
        verbose_name_plural = "时间段"
        unique_together = ['laboratory', 'weekday', 'start_time']
        ordering = ['laboratory', 'weekday', 'start_time']

    def __str__(self):
        return f"{self.laboratory.name} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Reservation(models.Model):
    """预约记录模型"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="预约用户")
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, verbose_name="实验室")
    date = models.DateField(verbose_name="预约日期")
    start_time = models.TimeField(verbose_name="开始时间")
    end_time = models.TimeField(verbose_name="结束时间")
    purpose = models.TextField(verbose_name="使用目的")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    admin_comment = models.TextField(blank=True, verbose_name="管理员备注")

    class Meta:
        verbose_name = "预约记录"
        verbose_name_plural = "预约记录"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.laboratory.name} - {self.date}"

    def clean(self):
        """验证预约时间"""
        if self.start_time >= self.end_time:
            raise ValidationError("开始时间必须早于结束时间")

        if self.date < timezone.now().date():
            raise ValidationError("不能预约过去的日期")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_past(self):
        """判断预约是否已过期"""
        return self.date < timezone.now().date()

    @property
    def can_cancel(self):
        """判断是否可以取消"""
        return self.status in ['pending', 'approved'] and not self.is_past


class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    student_id = models.CharField(max_length=20, unique=True, verbose_name="学号")
    phone = models.CharField(max_length=20, verbose_name="电话")
    department = models.CharField(max_length=100, verbose_name="院系")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"

    def __str__(self):
        return f"{self.user.username} - {self.student_id}"
