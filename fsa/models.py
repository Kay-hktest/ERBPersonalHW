from django.db import models

class SocialWorker(models.Model):
    name = models.CharField('社工姓名', max_length=100)
    staff_id = models.CharField('職員編號', max_length=20, unique=True)
    contact = models.CharField('聯絡方式', max_length=50)
    department = models.CharField('所屬部門', max_length=50)

    def __str__(self):
        return self.name

class ActivityCategory(models.Model):
    category_name = models.CharField('政府規範類別', max_length=50)

    def __str__(self):
        return self.category_name

class Activity(models.Model):
    title = models.CharField('活動名稱', max_length=200)
    social_worker = models.ForeignKey(SocialWorker, on_delete=models.CASCADE, verbose_name='負責社工')
    activity_date = models.DateField('活動日期')
    categories = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE, verbose_name='活動類別')
    participant_num = models.IntegerField('參與長者人數')
    total_sessions = models.IntegerField('總節數')

    def __str__(self):
        return self.title
