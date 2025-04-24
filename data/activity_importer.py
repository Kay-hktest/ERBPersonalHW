
#python data/activity_importer.py --mode import --file data/2025activity_test_data.csv
# python data/activity_importer.py --mode export --file data/activity_data_export.csv

import os
import sys
import argparse
import csv
from django.db import IntegrityError
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erb_project2.settings')
import django
django.setup()

from fsa.models import Activity, SocialWorker, ActivityCategory

def import_from_csv(file_path):
    """將CSV數據批量導入Django資料庫，處理外鍵關聯，並加強錯誤提示"""
    required_fields = ['活動名稱', '職員編號', '活動日期', '政府規範類別', '參與長者人數', '總節數']
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            activities = []
            row_num = 1
            for row in reader:
                row_num += 1
                # 檢查必填欄位
                missing = [field for field in required_fields if not row.get(field)]
                if missing:
                    print(f"第{row_num}行缺少欄位: {','.join(missing)}，跳過該行")
                    continue
                # 職員外鍵
                try:
                    sw = SocialWorker.objects.get(staff_id=row['職員編號'])
                except SocialWorker.DoesNotExist:
                    print(f"第{row_num}行找不到職員編號 {row['職員編號']} 的社工，跳過該行")
                    continue
                # 活動類別外鍵
                try:
                    cat = ActivityCategory.objects.get(category_name=row['政府規範類別'])
                except ActivityCategory.DoesNotExist:
                    valid_categories = list(ActivityCategory.objects.values_list('category_name', flat=True))
                    print(f"第{row_num}行找不到活動類別 {row['政府規範類別']}，有效類別為: {', '.join(valid_categories)}，跳過該行")
                    continue
                # 日期格式
                try:
                    activity_date = datetime.strptime(row['活動日期'], '%Y-%m-%d').date()
                except Exception:
                    print(f"第{row_num}行活動日期格式錯誤: {row['活動日期']}，應為YYYY-MM-DD，跳過該行")
                    continue
                # 數值型欄位
                try:
                    participant_num = int(row['參與長者人數'])
                except Exception:
                    print(f"第{row_num}行參與長者人數格式錯誤: {row['參與長者人數']}，應為整數，跳過該行")
                    continue
                try:
                    total_sessions = int(row['總節數'])
                except Exception:
                    print(f"第{row_num}行總節數格式錯誤: {row['總節數']}，應為整數，跳過該行")
                    continue
                activities.append(Activity(
                    title=row['活動名稱'],
                    social_worker=sw,
                    activity_date=activity_date,
                    categories=cat,
                    participant_num=participant_num,
                    total_sessions=total_sessions
                ))
            if activities:
                Activity.objects.bulk_create(activities)
            print(f'成功導入 {len(activities)} 筆活動資料')
    except IntegrityError as e:
        print(f'資料庫錯誤: {str(e)}')
    except Exception as e:
        print(f'導入失敗: {str(e)}')

def export_to_csv(output_path):
    """從資料庫導出活動數據，保留中文表頭"""
    fields = ['title', 'social_worker', 'activity_date', 'categories', 'participant_num', 'total_sessions']
    headers = ['活動名稱', '職員編號', '活動日期', '政府規範類別', '參與長者人數', '總節數']
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for act in Activity.objects.all():
                writer.writerow([
                    act.title,
                    act.social_worker.staff_id if act.social_worker else '',
                    act.activity_date.strftime('%Y-%m-%d'),
                    act.categories.category_name if act.categories else '',
                    act.participant_num,
                    act.total_sessions
                ])
        print(f'已導出 {Activity.objects.count()} 筆活動資料至 {output_path}')
    except Exception as e:
        print(f'導出失敗: {str(e)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='活動資料導入/導出工具')
    parser.add_argument('--mode', choices=['import', 'export'], required=True, help='操作模式: import 或 export')
    parser.add_argument('--file', required=True, help='導入用的CSV文件路徑或導出的輸出路徑')
    args = parser.parse_args()
    if args.mode == 'import':
        if not os.path.exists(args.file):
            print(f'錯誤: 文件 {args.file} 不存在')
            sys.exit(1)
        import_from_csv(args.file)
    elif args.mode == 'export':
        export_to_csv(args.file)