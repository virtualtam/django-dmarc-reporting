"""django-dmarc-reporting views"""
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from .models import Domain


@login_required
def domains_list(request):
    """List domains whose reports have been imported"""
    return render(
        request,
        'dmarc_reporting/domains_list.html',
        {
            'domains': Domain.objects.annotate(
                num_reports=Count('publishedfeedbackpolicy')
            ).filter(num_reports__gt=0),
        }
    )
