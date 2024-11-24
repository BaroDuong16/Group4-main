from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict
from .models import AIInsights
from course.models import Course
from .forms import AI_InsightsForm, ExcelImportForm, AI_InsightsCourseForm
import pandas as pd
from django.contrib import messages
from module_group.models import ModuleGroup
from django.http import HttpResponse
import openpyxl
import json

# User views
def ai_insights_list(request):
    ai_insights = AIInsights.objects.all()
    form = ExcelImportForm()
    return render(request, 'ai_insights_list.html', {'ai_insights': ai_insights, 'form': form})

def ai_insights_detail(request, id):
    ai_insights = AIInsights.objects.get(id=id)
    return render(request, 'ai_insights_detail.html', {'ai_insights': ai_insights})

def ai_insights_add(request):
    if request.method == 'POST':
        form = AI_InsightsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ai_insights:ai_insights_list')
    else:
        form = AI_InsightsForm()
    return render(request, 'ai_insights_form.html', {'form': form})

def ai_insights_edit(request, id):
    ai_insights = get_object_or_404(AIInsights, id=id)
    print(ai_insights)
    if request.method == 'POST':
        form = AI_InsightsForm(request.POST, instance=ai_insights)
        if form.is_valid():
            form.save()
            return redirect('ai_insights:ai_insights_list')
    else:
        form = AI_InsightsForm(instance=ai_insights)
    return render(request, 'ai_insights_form.html', {'form': form})

def ai_insights_delete(request, id):
    notification = AIInsights.objects.get(id=id)
    if request.method == 'POST':
        notification.delete()
        return redirect('ai_insights:ai_insights_list')
    return render(request, 'ai_insights_confirm_delete.html', {'notification': notification})

def export_ai_insights(request):
    # Create a workbook and add a worksheet
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_insights.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'AI Insights'

    
    # Define the columns
    columns = ['username','course','insight_text','insight_type']
    worksheet.append(columns)
    
    # Fetch all users and write to the Excel file
    for ai_insight in AIInsights.objects.all():
        try:    
            worksheet.append([str(ai_insight.username), ai_insight.course, ai_insight.insight_text, ai_insight.insight_type])
        except Exception as e:
            print(e)
    
    workbook.save(response)
    return response

def import_ai_insights(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                # Read the Excel file
                df = pd.read_excel(uploaded_file)
                insights_imported = 0  # Counter for users successfully imported

                # Loop over the rows in the DataFrame
                for index, row in df.iterrows():
                    username = row.get("username")
                    course = str(row.get("course"))
                    insight_text = row.get("insight_text")
                    insight_type = row.get("insight_type")

                    print(f"Processing row: {username}, {course}, {insight_type}")  # Debugging

                    # Check if the user already exists
                    from user.models import User
                    username_id = User.objects.get(username=username).id

                    print(username_id)

                    if not AIInsights.objects.filter(username_id=username_id, course=course, insight_type=insight_type, insight_text=insight_text).exists():
                        # Create and save the new user
                        AIInsights.objects.create(
                            username_id=username_id,
                            course=course,
                            insight_type=insight_type,
                            insight_text=insight_text
                        )
                        insights_imported += 1
                        print(f"Insight {username} created")  # Debugging
                    else:
                        messages.warning(request, f"Insight '{username}' already exists. Skipping.")
                        print(f"Insight {username} already exists")  # Debugging

                # Feedback message
                if insights_imported > 0:
                    messages.success(request, f"{insights_imported} insights imported successfully!")
                else:
                    messages.warning(request, "No insights were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")  # Debugging

            return redirect('ai_insights:ai_insights_list')
    else:
        form = ExcelImportForm()

    return render(request, 'ai_insights_list.html', {'form': form})

from django.core.paginator import Paginator

def ai_insights_summary(request):
    user = request.user      
    labels = ['Warning', 'Compliment', 'Info', 'Undefined']
    if request.method == 'POST':
        filter_form = AI_InsightsCourseForm(request.POST)
        if filter_form.is_valid():
            if filter_form.data['course'] == '':
                filter_form = AI_InsightsCourseForm()
                ai_insights = AIInsights.objects.filter(user=user.id).order_by('-created_at')
                ai_insights_count = len(list(ai_insights))

                warning = ai_insights.filter(insight_type='Warning')
                compliment = ai_insights.filter(insight_type='Compliment')
                info = ai_insights.filter(insight_type='Info')

                warning_count = len(list(warning))
                compliment_count = len(list(compliment))
                info_count = len(list(info))

                data = [warning_count, compliment_count, info_count, (ai_insights_count-warning_count-compliment_count-info_count)]
                paginator = Paginator(ai_insights, 4) 
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                context = {
                    'page_ai_insights': page_obj,
                    'user': request.user,
                    'filter_form': filter_form,
                    'data': json.dumps(data),
                    'labels': json.dumps(labels),
                    'chart_name': 'All courses',
                    'is_valid': False
                    }
                return render(request, 'ai_insights_summary.html', context)
            ai_insights = AIInsights.objects.filter(user=user.id, course=filter_form.data['course']).order_by('-created_at')
            course = Course.objects.get(id=filter_form.data['course']).course_name
            ai_insights_count = len(list(ai_insights))

            warning = ai_insights.filter(insight_type='Warning')
            compliment = ai_insights.filter(insight_type='Compliment')
            info = ai_insights.filter(insight_type='Info')

            warning_count = len(list(warning))
            compliment_count = len(list(compliment))
            info_count = len(list(info))

            data = [warning_count, compliment_count, info_count, (ai_insights_count-warning_count-compliment_count-info_count)]
            paginator = Paginator(ai_insights, 4) 

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'page_ai_insights': page_obj,
                'user': request.user,
                'filter_form': filter_form,
                'data': json.dumps(data),
                'labels': json.dumps(labels),
                'chart_name': course,
                'is_valid': True
            }
            return render(request, 'ai_insights_summary.html', context)
    else:
        filter_form = AI_InsightsCourseForm()

        ai_insights = AIInsights.objects.filter(user=user.id).order_by('-created_at')

        ai_insights_count = len(list(ai_insights))

        warning = ai_insights.filter(insight_type='Warning')
        compliment = ai_insights.filter(insight_type='Compliment')
        info = ai_insights.filter(insight_type='Info')

        warning_count = len(list(warning))
        compliment_count = len(list(compliment))
        info_count = len(list(info))

        data = [warning_count, compliment_count, info_count, (ai_insights_count-warning_count-compliment_count-info_count)]
        paginator = Paginator(ai_insights, 4) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        

        context = {
            'page_ai_insights': page_obj,
            'user': request.user,
            'filter_form': filter_form,
            'data': json.dumps(data),
            'labels': json.dumps(labels),
            'chart_name': 'All courses',
            'is_valid': True
        }
    return render(request, 'ai_insights_summary.html', context)