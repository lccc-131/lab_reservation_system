from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Reservation, UserProfile


class ReservationForm(forms.ModelForm):
    """预约表单"""
    
    class Meta:
        model = Reservation
        fields = ['date', 'start_time', 'end_time', 'purpose']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': '',  # 将在模板中设置为今天的日期
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请简要说明使用目的...',
            }),
        }
        labels = {
            'date': '预约日期',
            'start_time': '开始时间',
            'end_time': '结束时间',
            'purpose': '使用目的',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError('开始时间必须早于结束时间')
        
        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='姓名')
    student_id = forms.CharField(max_length=20, required=True, label='学号')
    phone = forms.CharField(max_length=20, required=True, label='电话')
    department = forms.CharField(max_length=100, required=True, label='院系')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')
        labels = {
            'username': '用户名',
            'email': '邮箱',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加CSS类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        
        if commit:
            user.save()
            # 创建用户资料
            UserProfile.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                phone=self.cleaned_data['phone'],
                department=self.cleaned_data['department']
            )
        return user


class UserProfileForm(forms.ModelForm):
    """用户资料表单"""
    
    class Meta:
        model = UserProfile
        fields = ['student_id', 'phone', 'department']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'student_id': '学号',
            'phone': '电话',
            'department': '院系',
        }
