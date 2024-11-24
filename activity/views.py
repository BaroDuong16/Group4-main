from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserActivityLog
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import datetime
from django.utils import timezone
from module_group.models import ModuleGroup

@login_required
def activity_view(request):
    # Get search and date filter parameters
    search_query = request.GET.get('search', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    # Get all activity logs for the user, ordered by newest first
    activity_logs = UserActivityLog.objects.filter(user=request.user).order_by('-activity_timestamp')

    # Log the activity if it's the first access or a search/filter is performed
    if not request.session.get('activity_page_accessed', False):
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='page_visit',
            activity_details="Accessed activity_view",
            activity_timestamp=timezone.now()
        )
        request.session['activity_page_accessed'] = True  # Set the flag to prevent further logging

    if search_query or from_date or to_date:
        # Log the search/filter activity
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='search',
            activity_details=f"Searched activities with query: '{search_query}' and dates: '{from_date}' to '{to_date}'",
            activity_timestamp=timezone.now()
        )

    # Filter activity logs based on search query and date range
    if search_query:
        activity_logs = activity_logs.filter(activity_details__icontains=search_query)

    if from_date:
        from_date_parsed = parse_date(from_date)
        if from_date_parsed:
            activity_logs = activity_logs.filter(activity_timestamp__gte=from_date_parsed)

    if to_date:
        to_date_parsed = parse_date(to_date)
        if to_date_parsed:
            to_date_with_time = datetime.combine(to_date_parsed, datetime.max.time())
            activity_logs = activity_logs.filter(activity_timestamp__lte=to_date_with_time)

    # Pagination setup
    page_number = request.GET.get('page', 1)
    page_size = 20
    paginator = Paginator(activity_logs, page_size)
    activity_logs_page = paginator.get_page(page_number)

    # Calculate the page range for pagination display
    page_range_start = max(activity_logs_page.number - 2, 1)
    page_range_end = min(activity_logs_page.number + 2, paginator.num_pages)
    page_range = range(page_range_start, page_range_end + 1)  # Include end page

    # Calculate the start index for the current page
    activity_logs_page.start_index = (activity_logs_page.number - 1) * page_size + 1

    module_groups = ModuleGroup.objects.all()
    # Render the template with context data
    return render(request, 'activity.html', {
        'module_groups': module_groups,
        'activity_logs': activity_logs_page,
        'search_query': search_query,
        'from_date': from_date,
        'to_date': to_date,
        'page_range': page_range,
    })
