# views.py (add this new view)
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from .models import Activity, ActivityCategory, SocialWorker

def activity_summary(request):
    # Get filter parameters
    selected_month = request.GET.get('month')
    selected_social_worker = request.GET.get('social_worker')
    category_id = request.GET.get('category')

    # Base queryset
    activities = Activity.objects.all().order_by('-activity_date')
    
    # Apply filters
    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            activities = activities.filter(activity_date__year=year, activity_date__month=month)
        except (ValueError, AttributeError):
            pass
    
    if selected_social_worker:
        activities = activities.filter(social_worker__id=selected_social_worker)
    
    if category_id:
        activities = activities.filter(categories__id=category_id)

    # Annotate with month and aggregate data
    summary_data = activities.annotate(
        month=TruncMonth('activity_date')
    ).values('month', 'social_worker__name').annotate(
        total_activities=Count('id'),
        total_participants=Sum('participant_num')
    ).order_by('-month', 'social_worker__name')

    # Get totals
    totals = activities.aggregate(
        total_activities=Count('id'),
        total_participants=Sum('participant_num'),
        total_sessions=Sum('total_sessions')
    )

    # Get categories for filter dropdown
    categories = ActivityCategory.objects.all()
    # Get social workers for filter dropdown
    social_workers = SocialWorker.objects.all()
    


    context = {
        'summary_data': summary_data,
        'categories': categories,
        'totals': totals,
        'total_activities': totals['total_activities'] or 0,
        'total_participants': totals['total_participants'] or 0,
        'total_sessions': totals['total_sessions'] or 0,
        'selected_month': selected_month,
        'social_workers': social_workers,
        'selected_social_worker': selected_social_worker,
        'selected_category': category_id,
        'activities': activities
    }
    return render(request, 'fsa/activity_summary.html', context)