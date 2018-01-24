"""DMARC import utilities - Aggregated feedback reports"""
from datetime import datetime
from xml.parsers.expat import ExpatError

import xmltodict
from django.utils import timezone

from ..models import (AuthenticationResult, Domain, EvaluatedFeedbackPolicy,
                      FeedbackReport, FeedbackReportRecord,
                      PublishedFeedbackPolicy, Reporter)


class DmarcImportError(BaseException):
    """Raised when an XML report cannot be imported"""


def import_feedback_report(xml_report):
    """Import an aggregated feedback report"""
    try:
        i_data = xmltodict.parse(xml_report)
        i_feedback = i_data['feedback']
    except ExpatError as err:
        raise DmarcImportError(err)

    i_metadata = i_feedback['report_metadata']

    reporter, created = Reporter.objects.get_or_create(
        org_name=i_metadata['org_name'],
    )

    if created:
        reporter.email = i_metadata['email']
        reporter.extra_contact_info = i_metadata['extra_contact_info']
        reporter.save()

    date_begin = datetime.utcfromtimestamp(
        int(i_metadata['date_range']['begin'])
    )
    date_end = datetime.utcfromtimestamp(
        int(i_metadata['date_range']['end'])
    )

    report, created = FeedbackReport.objects.get_or_create(
        reporter=reporter,
        report_id=i_metadata['report_id'],
        date_begin=timezone.make_aware(date_begin),
        date_end=timezone.make_aware(date_end),
    )

    if not created:
        raise DmarcImportError("This report has already been imported")

    i_policy = i_feedback['policy_published']

    domain, created = Domain.objects.get_or_create(
        name=i_policy['domain'],
    )
    if created:
        domain.save()

    policy_published = PublishedFeedbackPolicy(
        domain=domain,
        alignment_dkim=i_policy['adkim'],
        alignment_spf=i_policy['aspf'],
        policy=i_policy['p'],
        subdomain_policy=i_policy['sp'],
        percentage=int(i_policy['pct']),
    )
    policy_published.save()

    report.policy_published = policy_published
    report.save()
