#!/usr/bin/env python
"""
创建示例数据的脚本
"""
import os
import sys
import django
from datetime import datetime, time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_reservation_system.settings')
django.setup()

from django.contrib.auth.models import User
from reservations.models import Laboratory, TimeSlot, Reservation, UserProfile

def create_sample_data():
    print("开始创建示例数据...")
    
    # 创建实验室
    labs_data = [
        {
            'name': '物理实验室A',
            'location': '理科楼301',
            'capacity': 30,
            'equipment': '示波器、信号发生器、万用表、电源等基础物理实验设备',
            'description': '适用于基础物理实验，包括力学、电学、光学等实验项目。'
        },
        {
            'name': '化学实验室B',
            'location': '理科楼205',
            'capacity': 25,
            'equipment': '通风橱、分析天平、离心机、pH计、加热设备等',
            'description': '专业化学实验室，配备完善的安全设施和精密仪器。'
        },
        {
            'name': '计算机实验室C',
            'location': '信息楼102',
            'capacity': 40,
            'equipment': '高性能计算机40台、投影设备、网络设备',
            'description': '现代化计算机实验室，支持编程、数据分析、软件开发等课程。'
        },
        {
            'name': '生物实验室D',
            'location': '生科楼401',
            'capacity': 20,
            'equipment': '显微镜、培养箱、离心机、PCR仪、电泳设备等',
            'description': '生物学专业实验室，适用于分子生物学、细胞生物学实验。'
        },
        {
            'name': '工程实验室E',
            'location': '工程楼501',
            'capacity': 15,
            'equipment': '3D打印机、激光切割机、数控机床、测量工具等',
            'description': '工程技术实验室，支持机械设计、制造工艺等实践课程。'
        }
    ]
    
    laboratories = []
    for lab_data in labs_data:
        lab, created = Laboratory.objects.get_or_create(
            name=lab_data['name'],
            defaults=lab_data
        )
        laboratories.append(lab)
        if created:
            print(f"创建实验室: {lab.name}")
    
    # 为每个实验室创建时间段
    time_slots_data = [
        (time(8, 0), time(10, 0)),   # 8:00-10:00
        (time(10, 0), time(12, 0)),  # 10:00-12:00
        (time(14, 0), time(16, 0)),  # 14:00-16:00
        (time(16, 0), time(18, 0)),  # 16:00-18:00
        (time(19, 0), time(21, 0)),  # 19:00-21:00
    ]
    
    for lab in laboratories:
        for weekday in range(7):  # 周一到周日
            for start_time, end_time in time_slots_data:
                time_slot, created = TimeSlot.objects.get_or_create(
                    laboratory=lab,
                    weekday=weekday,
                    start_time=start_time,
                    end_time=end_time
                )
                if created:
                    print(f"创建时间段: {lab.name} - {time_slot.get_weekday_display()} {start_time}-{end_time}")
    
    # 创建测试用户
    users_data = [
        {
            'username': 'student1',
            'password': 'student123',
            'first_name': '张三',
            'email': 'student1@example.com',
            'profile': {
                'student_id': '2021001',
                'phone': '13800138001',
                'department': '计算机科学与技术学院'
            }
        },
        {
            'username': 'student2',
            'password': 'student123',
            'first_name': '李四',
            'email': 'student2@example.com',
            'profile': {
                'student_id': '2021002',
                'phone': '13800138002',
                'department': '物理学院'
            }
        },
        {
            'username': 'teacher1',
            'password': 'teacher123',
            'first_name': '王老师',
            'email': 'teacher1@example.com',
            'is_staff': True,
            'profile': {
                'student_id': 'T001',
                'phone': '13800138003',
                'department': '化学学院'
            }
        }
    ]
    
    for user_data in users_data:
        profile_data = user_data.pop('profile')
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"创建用户: {user.username}")
            
            # 创建用户资料
            UserProfile.objects.get_or_create(
                user=user,
                defaults=profile_data
            )
            print(f"创建用户资料: {user.username}")
    
    print("示例数据创建完成！")
    print("\n登录信息:")
    print("管理员账户: admin / admin123")
    print("学生账户1: student1 / student123")
    print("学生账户2: student2 / student123")
    print("教师账户: teacher1 / teacher123")

if __name__ == '__main__':
    create_sample_data()
