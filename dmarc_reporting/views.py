"""django-dmarc-reporting views"""
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from .models import Domain, FeedbackReport


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


@login_required
def feedback_reports(request, domain_pk):
    """List feedback reports for a given domain"""
    domain = Domain.objects.get(pk=domain_pk)
    reports = FeedbackReport.objects.filter(policy_published__domain=domain).order_by('-date_end')

    return render(
        request,
        'dmarc_reporting/feedback_reports.html',
        {
            'domain': domain,
            'reports': reports,
        }
    )
