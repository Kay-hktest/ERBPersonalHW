# python data/activity_category_importer.py --mode import --file data/activity_categories.csv
# python data/activity_category_importer.py --mode export --file data/activity_categories_export.csv
import os
import sys
import argparse
import csv
from django.db import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erb_project2.settings')
import django
django.setup()

from fsa.models import ActivityCategory

def import_from_csv(file_path):
    """將CSV數據批量導入ActivityCategory資料表"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            categories = [
                ActivityCategory(
                    category_name=row['政府規範類別']
                ) for row in reader
            ]
            ActivityCategory.objects.bulk_create(categories)
            print(f'成功導入 {len(categories)} 筆活動類別資料')
    except IntegrityError as e:
        print(f'類別重複錯誤: {str(e)}')
    except Exception as e:
        print(f'導入失敗: {str(e)}')

def export_to_csv(output_path):
    """從資料庫導出活動類別數據並保留中文表頭"""
    fields = ['category_name']
    headers = ['政府規範類別']
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for cat in ActivityCategory.objects.all():
                writer.writerow([getattr(cat, field) for field in fields])
        print(f'已導出 {ActivityCategory.objects.count()} 筆活動類別資料至 {output_path}')
    except Exception as e:
        print(f'導出失敗: {str(e)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='活動類別資料導入/導出工具')
    parser.add_argument('--mode', choices=['import', 'export'], required=True,
                       help='操作模式: import 或 export')
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