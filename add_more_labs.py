#!/usr/bin/env python
"""
添加更多不同分类的实验室示例数据
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_reservation_system.settings')
django.setup()

from reservations.models import Laboratory

def add_more_laboratories():
    print("开始添加更多实验室...")
    
    # 新增实验室数据
    new_labs = [
        {
            'name': '数学建模实验室',
            'category': 'mathematics',
            'location': '数学楼201',
            'capacity': 35,
            'equipment': '高性能计算机、数学软件（MATLAB、Mathematica、R）、投影设备',
            'description': '专门用于数学建模、统计分析和数值计算的实验室。'
        },
        {
            'name': '电子技术实验室',
            'category': 'electronics',
            'location': '电子楼301',
            'capacity': 25,
            'equipment': '示波器、信号发生器、电路板、焊接设备、电子元器件',
            'description': '电子电路设计、制作和测试的专业实验室。'
        },
        {
            'name': '材料科学实验室',
            'category': 'materials',
            'location': '材料楼401',
            'capacity': 20,
            'equipment': 'X射线衍射仪、扫描电镜、拉伸试验机、硬度计',
            'description': '材料性能测试、结构分析和新材料研发实验室。'
        },
        {
            'name': '环境监测实验室',
            'category': 'environmental',
            'location': '环境楼501',
            'capacity': 18,
            'equipment': '气相色谱仪、水质分析仪、大气采样器、噪声计',
            'description': '环境污染监测、环境影响评价和环保技术研究实验室。'
        },
        {
            'name': '医学检验实验室',
            'category': 'medical',
            'location': '医学楼601',
            'capacity': 22,
            'equipment': '血液分析仪、生化分析仪、显微镜、离心机、培养箱',
            'description': '临床医学检验、病理分析和医学研究实验室。'
        },
        {
            'name': '高级物理实验室',
            'category': 'physics',
            'location': '理科楼401',
            'capacity': 16,
            'equipment': '激光器、光谱仪、真空系统、低温设备、精密测量仪器',
            'description': '现代物理实验、光学实验和精密测量实验室。'
        },
        {
            'name': '有机化学实验室',
            'category': 'chemistry',
            'location': '理科楼305',
            'capacity': 24,
            'equipment': '反应釜、蒸馏装置、色谱仪、红外光谱仪、核磁共振仪',
            'description': '有机合成、化合物分析和化学反应研究实验室。'
        },
        {
            'name': '软件工程实验室',
            'category': 'computer',
            'location': '信息楼201',
            'capacity': 45,
            'equipment': '高配置开发机、服务器、网络设备、大屏显示器',
            'description': '软件开发、系统设计和项目管理实验室。'
        }
    ]
    
    created_count = 0
    
    for lab_data in new_labs:
        lab, created = Laboratory.objects.get_or_create(
            name=lab_data['name'],
            defaults=lab_data
        )
        if created:
            print(f"创建实验室: {lab.name} ({lab.get_category_display()})")
            created_count += 1
        else:
            print(f"实验室已存在: {lab.name}")
    
    print(f"\n新增实验室完成！共创建了 {created_count} 个实验室。")
    
    # 显示最新的分类统计
    print("\n当前分类统计:")
    total_labs = 0
    for category_code, category_name in Laboratory.CATEGORY_CHOICES:
        count = Laboratory.objects.filter(category=category_code, is_active=True).count()
        if count > 0:
            print(f"  {category_name}: {count} 个")
            total_labs += count
    
    print(f"\n总计: {total_labs} 个活跃实验室")

if __name__ == '__main__':
    add_more_laboratories()
