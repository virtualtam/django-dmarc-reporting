"""Unitary tests for DMARC aggregated feedback report import"""
# pylint:disable=redefined-outer-name
import xml.etree.ElementTree as ET

import pytest

from ..models import (AuthenticationResult, Domain, EvaluatedFeedbackPolicy,
                      FeedbackReport, FeedbackReportRecord,
                      PublishedFeedbackPolicy, Reporter)
from .feedback import DmarcImportError, import_feedback_report


@pytest.fixture
def report_metadata():
    """DMARC reporter"""
    meta = ET.Element('report_metadata')
    org = ET.SubElement(meta, 'org_name')
    org.text = 'Scroogle'
    email = ET.SubElement(meta, 'email')
    email.text = 'mailer@scroogle.net'
    extra = ET.SubElement(meta, 'extra_contact_info')
    extra.text = 'http://scroogle.net'
    rid = ET.SubElement(meta, 'report_id')
    rid.text = '1234'
    dates = ET.SubElement(meta, 'date_range')
    beg = ET.SubElement(dates, 'begin')
    beg.text = '1513663203'
    end = ET.SubElement(dates, 'end')
    end.text = '1513749603'
    return meta


@pytest.fixture
def published_policy():
    """Published domain policy"""
    policy = ET.Element('policy_published')
    domain = ET.SubElement(policy, 'domain')
    domain.text = 'domain.tld'
    adkim = ET.SubElement(policy, 'adkim')
    adkim.text = 'r'
    aspf = ET.SubElement(policy, 'aspf')
    aspf.text = 'r'
    pol = ET.SubElement(policy, 'p')
    pol.text = 'none'
    sub_pol = ET.SubElement(policy, 'sp')
    sub_pol.text = 'none'
    pct = ET.SubElement(policy, 'pct')
    pct.text = '100'
    return policy


@pytest.fixture
def feedback_record():
    """Result record"""
    # pylint: disable=too-many-locals
    record = ET.Element('record')

    row = ET.SubElement(record, 'row')
    sip = ET.SubElement(row, 'source_ip')
    sip.text = '10.1.173.7'
    count = ET.SubElement(row, 'count')
    count.text = '5'
    policy = ET.SubElement(row, 'policy_evaluated')
    disposition = ET.SubElement(policy, 'disposition')
    disposition.text = 'none'
    dkim = ET.SubElement(policy, 'dkim')
    dkim.text = 'pass'
    spf = ET.SubElement(policy, 'spf')
    spf.text = 'pass'

    identifiers = ET.SubElement(record, 'identifiers')
    header_from = ET.SubElement(identifiers, 'header_from')
    header_from.text = 'domain.tld'
    envelope_from = ET.SubElement(identifiers, 'envelope_from')
    envelope_from.text = 'domain.tld'

    auth_results = ET.SubElement(record, 'auth_results')
    au_dkim = ET.SubElement(auth_results, 'dkim')
    dkim_domain = ET.SubElement(au_dkim, 'domain')
    dkim_domain.text = 'domain.tld'
    dkim_selector = ET.SubElement(au_dkim, 'selector')
    dkim_selector.text = 'dkim'
    dkim_result = ET.SubElement(au_dkim, 'result')
    dkim_result.text = 'pass'
    au_spf = ET.SubElement(auth_results, 'spf')
    spf_domain = ET.SubElement(au_spf, 'domain')
    spf_domain.text = 'domain.tld'
    spf_scope = ET.SubElement(au_spf, 'scope')
    spf_scope.text = 'mfrom'
    spf_result = ET.SubElement(au_spf, 'result')
    spf_result.text = 'pass'

    return record


@pytest.fixture
def feedback_report(report_metadata, published_policy, feedback_record):
    """Dummy aggregated feedbak report"""
    meta = report_metadata
    policy = published_policy
    record = feedback_record

    feedback = ET.Element('feedback')
    feedback.append(meta)
    feedback.append(policy)
    feedback.append(record)
    feedback.append(record)

    return feedback


@pytest.mark.django_db
def test_import_single_report(feedback_report):
    """Import a DMARC aggregated feedback report"""
    # pylint: disable=too-many-locals,too-many-statements
    feedback = feedback_report

    import_feedback_report(ET.tostring(feedback))

    reporter = Reporter.objects.get(pk=1)
    assert reporter.org_name == 'Scroogle'
    assert reporter.email == 'mailer@scroogle.net'
    assert reporter.extra_contact_info == 'http://scroogle.net'

    domain = Domain.objects.get(pk=1)
    assert domain.name == 'domain.tld'

    policy_published = PublishedFeedbackPolicy.objects.get(pk=1)
    assert policy_published.domain == domain
    assert policy_published.alignment_dkim == 'r'
    assert policy_published.alignment_spf == 'r'
    assert policy_published.policy == 'none'
    assert policy_published.subdomain_policy == 'none'
    assert policy_published.percentage == 100

    report = FeedbackReport.objects.get(pk=1)
    assert report.reporter == reporter
    assert report.report_id == '1234'
    assert report.policy_published == policy_published

    record1 = FeedbackReportRecord.objects.get(pk=1)
    assert record1.report == report
    assert record1.source_ip == '10.1.173.7'
    assert record1.count == 5
    assert record1.header_from == domain
    assert record1.envelope_from == domain

    policy1 = EvaluatedFeedbackPolicy.objects.get(record=record1)
    assert policy1.record == record1
    assert policy1.disposition == 'none'
    assert policy1.dkim_pass is True
    assert policy1.spf_pass is True

    dkim_result1 = AuthenticationResult.objects.get(
        record=record1,
        result_type='dkim'
    )
    assert dkim_result1.domain == domain
    assert dkim_result1.record == record1
    assert dkim_result1.result == 'pass'
    assert dkim_result1.selector == 'dkim'
    assert dkim_result1.scope == ''

    spf_result1 = AuthenticationResult.objects.get(
        record=record1,
        result_type='spf'
    )
    assert spf_result1.domain == domain
    assert spf_result1.record == record1
    assert spf_result1.result == 'pass'
    assert spf_result1.selector == ''
    assert spf_result1.scope == 'mfrom'

    record2 = FeedbackReportRecord.objects.get(pk=2)
    assert record2.report == report
    assert record2.source_ip == '10.1.173.7'
    assert record2.count == 5
    assert record2.header_from == domain
    assert record2.envelope_from == domain

    policy2 = EvaluatedFeedbackPolicy.objects.get(record=record2)
    assert policy2.record == record2
    assert policy2.disposition == 'none'
    assert policy2.dkim_pass is True
    assert policy2.spf_pass is True

    dkim_result2 = AuthenticationResult.objects.get(
        record=record2,
        result_type='dkim'
    )
    assert dkim_result2.domain == domain
    assert dkim_result2.record == record2
    assert dkim_result2.result == 'pass'
    assert dkim_result2.selector == 'dkim'
    assert dkim_result2.scope == ''

    spf_result2 = AuthenticationResult.objects.get(
        record=record2,
        result_type='spf'
    )
    assert spf_result2.domain == domain
    assert spf_result2.record == record2
    assert spf_result2.result == 'pass'
    assert spf_result2.selector == ''
    assert spf_result2.scope == 'mfrom'


@pytest.mark.django_db
def test_import_report_twice(feedback_report):
    """Attempt importing the same report twice"""
    feedback = feedback_report

    import_feedback_report(ET.tostring(feedback))

    with pytest.raises(DmarcImportError):
        import_feedback_report(ET.tostring(feedback))


def test_import_report_malformed():
    """Attempt importing a malformed XML document"""
    with pytest.raises(DmarcImportError):
        import_feedback_report('<malform></ed>')
