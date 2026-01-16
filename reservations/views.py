from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Laboratory, Reservation, TimeSlot, UserProfile
from .forms import ReservationForm, UserRegistrationForm, UserProfileForm


def laboratory_list(request):
    """实验室列表页面"""
    laboratories = Laboratory.objects.filter(is_active=True)
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    # 搜索筛选
    if search_query:
        laboratories = laboratories.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(equipment__icontains=search_query)
        )

    # 分类筛选
    if category_filter:
        laboratories = laboratories.filter(category=category_filter)

    # 获取所有分类及其数量
    all_laboratories = Laboratory.objects.filter(is_active=True)
    if search_query:
        all_laboratories = all_laboratories.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(equipment__icontains=search_query)
        )

    category_counts = {}
    for category_code, category_name in Laboratory.CATEGORY_CHOICES:
        count = all_laboratories.filter(category=category_code).count()
        if count > 0:
            # 创建一个临时实验室对象来获取颜色
            temp_lab = Laboratory(category=category_code)
            category_counts[category_code] = {
                'name': category_name,
                'count': count,
                'color': temp_lab.get_category_color()
            }

    context = {
        'laboratories': laboratories,
        'search_query': search_query,
        'category_filter': category_filter,
        'category_counts': category_counts,
        'total_count': all_laboratories.count(),
    }
    return render(request, 'reservations/laboratory_list.html', context)


def laboratory_detail(request, lab_id):
    """实验室详情页面"""
    laboratory = get_object_or_404(Laboratory, id=lab_id, is_active=True)

    # 获取未来7天的预约情况
    today = timezone.now().date()
    future_dates = [today + timedelta(days=i) for i in range(7)]

    # 获取该实验室的时间段
    time_slots = TimeSlot.objects.filter(laboratory=laboratory, is_available=True)

    # 获取已有预约
    existing_reservations = Reservation.objects.filter(
        laboratory=laboratory,
        date__in=future_dates,
        status__in=['pending', 'approved']
    ).values('date', 'start_time', 'end_time')

    context = {
        'laboratory': laboratory,
        'time_slots': time_slots,
        'future_dates': future_dates,
        'existing_reservations': list(existing_reservations),
    }
    return render(request, 'reservations/laboratory_detail.html', context)


@login_required
def make_reservation(request, lab_id):
    """创建预约"""
    laboratory = get_object_or_404(Laboratory, id=lab_id, is_active=True)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.laboratory = laboratory

            # 检查预约冲突
            conflicts = Reservation.objects.filter(
                laboratory=laboratory,
                date=reservation.date,
                status__in=['pending', 'approved'],
                start_time__lt=reservation.end_time,
                end_time__gt=reservation.start_time
            )

            if conflicts.exists():
                messages.error(request, '该时间段已被预约，请选择其他时间。')
            else:
                reservation.save()
                messages.success(request, '预约申请已提交，等待管理员审核。')
                return redirect('reservations:my_reservations')
    else:
        form = ReservationForm()

    context = {
        'form': form,
        'laboratory': laboratory,
    }
    return render(request, 'reservations/make_reservation.html', context)


@login_required
def my_reservations(request):
    """用户预约记录"""
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'reservations': reservations,
    }
    return render(request, 'reservations/my_reservations.html', context)


@login_required
def cancel_reservation(request, reservation_id):
    """取消预约"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if reservation.can_cancel:
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, '预约已取消。')
    else:
        messages.error(request, '无法取消该预约。')

    return redirect('reservations:my_reservations')


@login_required
def user_profile(request):
    """用户资料"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '资料已更新。')
            return redirect('reservations:user_profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'reservations/user_profile.html', context)


def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def admin_panel(request):
    """管理员面板"""
    pending_count = Reservation.objects.filter(status='pending').count()
    total_labs = Laboratory.objects.count()
    total_users = User.objects.count()

    context = {
        'pending_count': pending_count,
        'total_labs': total_labs,
        'total_users': total_users,
    }
    return render(request, 'reservations/admin_panel.html', context)


@user_passes_test(is_admin)
def admin_reservations(request):
    """管理员预约管理"""
    status_filter = request.GET.get('status', 'pending')
    reservations = Reservation.objects.filter(status=status_filter).order_by('-created_at')

    context = {
        'reservations': reservations,
        'status_filter': status_filter,
    }
    return render(request, 'reservations/admin_reservations.html', context)


@user_passes_test(is_admin)
def approve_reservation(request, reservation_id):
    """批准预约"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.status = 'approved'
    reservation.save()
    messages.success(request, f'已批准 {reservation.user.username} 的预约申请。')
    return redirect('reservations:admin_reservations')


@user_passes_test(is_admin)
def reject_reservation(request, reservation_id):
    """拒绝预约"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.status = 'rejected'
    reservation.save()
    messages.success(request, f'已拒绝 {reservation.user.username} 的预约申请。')
    return redirect('reservations:admin_reservations')


def user_login(request):
    """用户登录"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'reservations:laboratory_list')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误。')

    return render(request, 'reservations/login.html')


def user_logout(request):
    """用户登出"""
    logout(request)
    messages.success(request, '已成功登出。')
    return redirect('reservations:laboratory_list')


def user_register(request):
    """用户注册"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '注册成功，请登录。')
            return redirect('reservations:login')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'reservations/register.html', context)


def check_availability(request):
    """检查预约可用性（AJAX接口）"""
    lab_id = request.GET.get('lab_id')
    date = request.GET.get('date')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    if not all([lab_id, date, start_time, end_time]):
        return JsonResponse({'available': False, 'message': '参数不完整'})

    try:
        laboratory = Laboratory.objects.get(id=lab_id)
        conflicts = Reservation.objects.filter(
            laboratory=laboratory,
            date=date,
            status__in=['pending', 'approved'],
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if conflicts.exists():
            return JsonResponse({'available': False, 'message': '该时间段已被预约'})
        else:
            return JsonResponse({'available': True, 'message': '时间段可用'})

    except Laboratory.DoesNotExist:
        return JsonResponse({'available': False, 'message': '实验室不存在'})


def laboratory_list_ajax(request):
    """AJAX实验室列表接口"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    laboratories = Laboratory.objects.filter(is_active=True)

    # 搜索筛选
    if search_query:
        laboratories = laboratories.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(equipment__icontains=search_query)
        )

    # 分类筛选
    if category_filter:
        laboratories = laboratories.filter(category=category_filter)

    # 构建响应数据
    labs_data = []
    for lab in laboratories:
        labs_data.append({
            'id': lab.id,
            'name': lab.name,
            'category': lab.get_category_display(),
            'category_code': lab.category,
            'location': lab.location,
            'capacity': lab.capacity,
            'description': lab.description[:100] + '...' if len(lab.description) > 100 else lab.description,
            'equipment': lab.equipment[:80] + '...' if len(lab.equipment) > 80 else lab.equipment,
            'icon': lab.get_category_icon(),
            'color': lab.get_category_color(),
        })

    return JsonResponse({
        'laboratories': labs_data,
        'count': len(labs_data)
    })
