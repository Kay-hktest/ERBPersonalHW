# python data/social_worker_importer.py --mode import --file data/social_workers.csv
# python data/social_worker_importer.py --mode export --file data/social_workers_export.csv
#python data/social_worker_importer.py --mode clean_data 
import os
import sys
import argparse
import csv
from django.db import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erb_project2.settings')
import django
django.setup()

from fsa.models import SocialWorker


def import_from_csv(file_path):
    """將CSV數據批量導入Django資料庫"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            workers = [
                SocialWorker(
                    name=row['社工姓名'],
                    staff_id=row['職員編號'],
                    contact=row['聯絡方式'],
                    department=row['所屬部門']
                ) for row in reader
            ]
            SocialWorker.objects.bulk_create(workers)
            print(f'成功導入 {len(workers)} 筆社工資料')
    except IntegrityError as e:
        print(f'職員編號重複錯誤: {str(e)}')
    except Exception as e:
        print(f'導入失敗: {str(e)}')

def export_to_csv(output_path):
    """從資料庫導出數據並保留中文表頭"""
    fields = ['name', 'staff_id', 'contact', 'department']
    headers = ['社工姓名', '職員編號', '聯絡方式', '所屬部門']

    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for worker in SocialWorker.objects.all():
                writer.writerow([getattr(worker, field) for field in fields])
        print(f'已導出 {SocialWorker.objects.count()} 筆資料至 {output_path}')
    except Exception as e:
        print(f'導出失敗: {str(e)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='社工資料導入/導出工具')
    parser.add_argument('--mode', choices=['import', 'export', 'clean_data'], required=True,
                       help='操作模式: import, export 或 clean_data')
    parser.add_argument('--file', required=True,
                       help='導入用的CSV文件路徑或導出的輸出路徑')
    
    args = parser.parse_args()
    
    if args.mode == 'import':
        if not os.path.exists(args.file):
            print(f'錯誤: 文件 {args.file} 不存在')
            sys.exit(1)
        import_from_csv(args.file)
    elif args.mode == 'export':
        export_to_csv(args.file)
    elif args.mode == 'clean_data':
        if not os.path.exists(args.file):
            print(f'錯誤: 文件 {args.file} 不存在')
            sys.exit(1)
        try:
            with open(args.file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                cleaned_data = [clean_data(row) for row in reader]
            with open(args.file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(cleaned_data)
            print(f'成功清理並保存 {len(cleaned_data)} 筆資料至 {args.file}')
        except Exception as e:
            print(f'清理失敗: {str(e)}')