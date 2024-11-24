from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Certificate
from django.core.paginator import Paginator

def certificate_summary(request):
    user = request.user  
    certificates = Certificate.objects.filter(user=user.id)
    paginator = Paginator(certificates, 8) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'certificate_summary.html', context)

@login_required
def certificate_pdf(request,id):
    certificate = Certificate.objects.get(id=id)
    context = {
        'certificate': certificate
    }
    return render(request, 'certificate_pdf.html', context)
