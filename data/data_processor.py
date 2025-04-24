import csv
from datetime import datetime
import os
from django.core.management.base import BaseCommand
from fsa.models import SocialWorker, ActivityCategory, Activity

class DataProcessor:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    def clean_social_worker_data(self, row):
        """清理社工数据"""
        return {
            'name': row['社工姓名'].strip(),
            'staff_id': row['職員編號'].strip(),
            'contact': row['聯絡方式'].strip(),
            'department': row['所屬部門'].strip()
        }
    
    def clean_activity_data(self, row):
        """清理活动数据"""
        return {
            'title': row['活動名稱'].strip(),
            'social_worker': row['負責社工'].strip(),
            'activity_date': datetime.strptime(row['活動日期'], '%Y-%m-%d').date(),
            'category': row['活動類別'].strip(),
            'participant_num': int(row['參與長者人數']),
            'total_sessions': int(row['總節數'])
        }
    
    def import_data(self):
        """导入所有CSV数据到数据库"""
        # 导入社工数据
        with open(os.path.join(self.data_dir, 'social_workers.csv'), encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = self.clean_social_worker_data(row)
                SocialWorker.objects.get_or_create(
                    staff_id=data['staff_id'],
                    defaults=data
                )
        
        # 导入活动类别
        with open(os.path.join(self.data_dir, 'activity_categories.csv'), encoding='utf-8') as f:
            for line in f:
                category_name = line.strip()
                if category_name:
                    ActivityCategory.objects.get_or_create(category_name=category_name)
        
        # 导入活动数据
        with open(os.path.join(self.data_dir, 'activities.csv'), encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = self.clean_activity_data(row)
                social_worker = SocialWorker.objects.get(name=data['social_worker'])
                category = ActivityCategory.objects.get(category_name=data['category'])
                
                Activity.objects.get_or_create(
                    title=data['title'],
                    activity_date=data['activity_date'],
                    defaults={
                        'social_worker': social_worker,
                        'categories': category,
                        'participant_num': data['participant_num'],
                        'total_sessions': data['total_sessions']
                    }
                )
    
    def export_data(self, output_dir):
        """导出数据到CSV文件"""
        # 导出社工数据
        with open(os.path.join(output_dir, 'social_workers_export.csv'), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['社工姓名', '職員編號', '聯絡方式', '所屬部門'])
            for worker in SocialWorker.objects.all():
                writer.writerow([worker.name, worker.staff_id, worker.contact, worker.department])
        
        # 导出活动类别
        with open(os.path.join(output_dir, 'activity_categories_export.csv'), 'w', encoding='utf-8') as f:
            for category in ActivityCategory.objects.all():
                f.write(f"{category.category_name}\n")
        
        # 导出活动数据
        with open(os.path.join(output_dir, 'activities_export.csv'), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['活動名稱', '負責社工', '活動日期', '活動類別', '參與長者人數', '總節數'])
            for activity in Activity.objects.all():
                writer.writerow([
                    activity.title,
                    activity.social_worker.name,
                    activity.activity_date,
                    activity.categories.category_name,
                    activity.participant_num,
                    activity.total_sessions
                ])

class Command(BaseCommand):
    help = '导入和导出CSV数据'
    
    def add_arguments(self, parser):
        parser.add_argument('--import', action='store_true', help='导入CSV数据到数据库')
        parser.add_argument('--export', action='store_true', help='从数据库导出数据到CSV')
        parser.add_argument('--output', type=str, help='导出目录路径')
    
    def handle(self, *args, **options):
        processor = DataProcessor()
        
        if options['import']:
            processor.import_data()
            self.stdout.write(self.style.SUCCESS('成功导入数据'))
        
        if options['export']:
            if not options['output']:
                self.stdout.write(self.style.ERROR('请指定输出目录'))
                return
            processor.export_data(options['output'])
            self.stdout.write(self.style.SUCCESS('成功导出数据'))