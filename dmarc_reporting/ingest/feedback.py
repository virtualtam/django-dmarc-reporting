"""DMARC import utilities - Aggregated feedback reports"""
from datetime import datetime
from xml.parsers.expat import ExpatError

import xmltodict
from django.utils import timezone

from ..models import (AuthenticationResult, Domain, EvaluatedFeedbackPolicy, FeedbackReport,
                      FeedbackReportRecord, PublishedFeedbackPolicy, Reporter)


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
        reporter.email = i_metadata.get('email', '')
        reporter.extra_contact_info = i_metadata.get('extra_contact_info', '')
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

    subdomain_policy = i_policy.get('sp', PublishedFeedbackPolicy.NONE)
    if not subdomain_policy:
        subdomain_policy = PublishedFeedbackPolicy.NONE

    policy_published = PublishedFeedbackPolicy(
        domain=domain,
        alignment_dkim=i_policy['adkim'],
        alignment_spf=i_policy['aspf'],
        policy=i_policy['p'],
        subdomain_policy=subdomain_policy,
        percentage=int(i_policy['pct']),
    )
    policy_published.save()

    report.policy_published = policy_published
    report.save()

    if isinstance(i_feedback['record'], list):
        for i_record in i_feedback['record']:
            import_feedback_report_record(report, i_record)
    else:
        import_feedback_report_record(report, i_feedback['record'])


def import_feedback_report_record(report, record_dict):
    """Import a feedback report record"""
    header_from, created = Domain.objects.get_or_create(
        name=record_dict['identifiers']['header_from'],
    )
    if created:
        header_from.save()

    try:
        envelope_from, created = Domain.objects.get_or_create(
            name=record_dict['identifiers']['envelope_from'],
        )
        if created:
            envelope_from.save()
    except KeyError:
        envelope_from = None

    i_row = record_dict['row']
    record = FeedbackReportRecord(
        report=report,
        source_ip=i_row['source_ip'],
        count=int(i_row['count']),
        header_from=header_from,
        envelope_from=envelope_from,
    )
    record.save()

    i_policy = i_row['policy_evaluated']
    policy = EvaluatedFeedbackPolicy(
        record=record,
        disposition=i_policy['disposition'],
        dkim_pass=True if i_policy['dkim'] == 'pass' else False,
        spf_pass=True if i_policy['spf'] == 'pass' else False,
    )
    policy.save()

    for result_type, results in record_dict['auth_results'].items():
        if isinstance(results, list):
            for result in results:
                import_feedback_record_result(record, result_type, result)
        else:
            import_feedback_record_result(record, result_type, results)


def import_feedback_record_result(record, result_type, result):
    """Import a feedback report record authentication result"""
    domain, created = Domain.objects.get_or_create(
        name=result['domain'],
    )
    if created:
        domain.save()

    auth_result = AuthenticationResult(
        domain=domain,
        record=record,
        result_type=result_type,
        result=result['result'],
        scope=result.get('scope', ''),
        selector=result.get('selector', ''),
    )
    auth_result.save()
