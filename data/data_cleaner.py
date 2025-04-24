# python data/data_cleaner.py --mode all
import os
import sys
import argparse
from django.db import transaction

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erb_project2.settings')
import django
django.setup()

from fsa.models import SocialWorker, Activity, ActivityCategory

def clean_database(mode, tables=None):
    """安全清理数据库数据，支持全部或指定表清理"""
    models_mapping = {
        'SocialWorker': SocialWorker,
        'Activity': Activity,
        'ActivityCategory': ActivityCategory
    }

    try:
        with transaction.atomic():
            if mode == 'all':
                deleted_counts = {
                    'Activity': Activity.objects.all().delete()[0],
                    'SocialWorker': SocialWorker.objects.all().delete()[0],
                    'ActivityCategory': ActivityCategory.objects.all().delete()[0]
                }
            else:
                deleted_counts = {}
                for table in tables:
                    if table in models_mapping:
                        deleted_counts[table] = models_mapping[table].objects.all().delete()[0]
            
            return deleted_counts
    except Exception as e:
        print(f'清理过程中发生错误: {str(e)}')
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='数据库清理工具')
    parser.add_argument('--mode', 
                        choices=['all', 'specific'], 
                        required=True,
                        help='清理模式: all-清理所有表, specific-清理指定表')
    parser.add_argument('--tables',
                        nargs='+',
                        help='需要清理的表名列表（当mode=specific时必需）')
    
    args = parser.parse_args()

    if args.mode == 'specific' and not args.tables:
        parser.error("specific模式需要指定--tables参数")

    # 操作确认
    confirm = input(f'即将清理模式[{args.mode}]下的数据，是否继续？(yes/no): ')
    if confirm.lower() not in ['yes', 'y']:
        print('操作已取消')
        sys.exit(0)

    try:
        result = clean_database(args.mode, args.tables)
        print('清理完成，删除记录数：')
        for table, count in result.items():
            print(f'{table}: {count}条')
    except Exception as e:
        print(f'清理失败: {str(e)}')
        sys.exit(1)