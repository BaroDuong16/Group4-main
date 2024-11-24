from django.shortcuts import render, get_object_or_404, redirect
from .models import AnalyticsReport
from .forms import AnalyticsReportForm

# User views
def analytics_report_list(request):
    analytics_reports = AnalyticsReport.objects.all()
    return render(request, 'analytics_report_list.html', {'analytics_reports': analytics_reports})

def analytics_report_detail(request, pk):
    analytics_report = get_object_or_404(AnalyticsReport, pk=pk)
    return render(request, 'analytics_report_detail.html', {'analytics_report': analytics_report})

def analytics_report_add(request):
    if request.method == 'POST':
        form = AnalyticsReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('analytics_report:analytics_report_list')
    else:
        form = AnalyticsReportForm()
    return render(request, 'analytics_report_form.html', {'form': form})

def analytics_report_edit(request, pk):
    analytics_report = get_object_or_404(AnalyticsReport, pk=pk)
    if request.method == 'POST':
        form = AnalyticsReportForm(request.POST, instance=analytics_report)
        if form.is_valid():
            form.save()
            return redirect('analytics_report:analytics_report_list')
    else:
        form = AnalyticsReportForm(instance=analytics_report)
    return render(request, 'analytics_report_form.html', {'form': form})

def analytics_report_delete(request, pk):
    analytics_report = get_object_or_404(AnalyticsReport, pk=pk)
    if request.method == 'POST':
        analytics_report.delete()
        return redirect('analytics_report:analytics_report_list')
    return render(request, 'analytics_report_confirm_delete.html', {'analytics_report': analytics_report})


