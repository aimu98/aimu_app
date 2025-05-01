from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
import datetime


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('reserved', '予約済み'),
        ('cancelled', 'キャンセル'),
        ('completed', '完了'),
    ]
    PLAN_CHOICES = [
        ('basic', 'ベーシックプラン'),
        ('753', '七五三プラン'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("名前", max_length=100)
    children_name = models.CharField("お子様のお名前", max_length=100)
    date = models.DateField("予約日")
    start_time = models.TimeField()
    end_time = models.TimeField(default=datetime.time(12, 0)) 
    created_at = models.DateTimeField(auto_now_add=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    
    def __str__(self):
        return f"{self.user} - {self.get_plan_display()}"
    
    @property
    def can_cancel(self):
        return (self.date - date.today()).days >= 3
    
    @property
    def can_edit(self):
        return (self.date - date.today()).days >= 1 
    
    @staticmethod
    def get_reserved_times(date):
        reservations = Reservation.objects.filter(date=date)
        reserved_times = [(r.start_time, r.end_time) for r in reservations]
        return reserved_times
    
    class Meta:
        unique_together = ('date', 'start_time')  # 二重予約防止

    def is_cancellable(self):
        return (self.date - date.today()) >= timedelta(days=3)

class AvailableSlot(models.Model):
    date = models.DateField("日付")  
    start_time = models.TimeField("開始時間")
    end_time = models.TimeField("終了時間")    
    class Meta:
        unique_together = ('date', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.date} {self.start_time}"
