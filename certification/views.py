# certification/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Certification
from .forms import CertificationForm
# certification/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Certification
from .forms import CertificationForm
from datetime import datetime

def certification_detail(request, pk):
    certification = Certification.objects.get(pk=pk)
    context = {
        'recipient_name': certification.user.username,
        'course_name': certification.course.course_name,
        'description': certification.description,
        'awarded_date': certification.awarded_date.strftime("%B %d, %Y") if certification.awarded_date else "Not specified",
        'year': datetime.now().year,
    }
    return render(request, 'certification/certificate_template.html', context)
def certification_list(request):
    certifications = Certification.objects.all()
    paginator = Paginator(certifications, 5)  # 5 certifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'certification/certification_list.html', {'page_obj': page_obj})

# def certification_detail(request, pk):
#     certification = get_object_or_404(Certification, pk=pk)
#     return render(request, 'certification/certification_detail.html', {'certification': certification})

def certification_delete(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    if request.method == 'POST':
        certification.delete()
        return redirect('certification:certification_list')
    return render(request, 'certification/certification_confirm_delete.html', {'certification': certification})


def certification_create(request):
    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save(commit=False)
            if form.cleaned_data['certificate_option'] == 'html':
                certification.certificate_file = None  # Clear the file field if HTML is used
            else:
                certification.certificate_html = ''  # Clear HTML field if file is uploaded
            certification.save()
            return redirect('certification:certification_list')
    else:
        form = CertificationForm()
    return render(request, 'certification/certification_form.html', {'form': form})

def certification_update(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES, instance=certification)
        if form.is_valid():
            certification = form.save(commit=False)
            if form.cleaned_data['certificate_option'] == 'html':
                certification.certificate_file = None  # Clear the file field if HTML is used
            else:
                certification.certificate_html = ''  # Clear HTML field if file is uploaded
            certification.save()
            return redirect('certification:certification_list')
    else:
        form = CertificationForm(instance=certification)
    return render(request, 'certification/certification_form.html', {'form': form})
