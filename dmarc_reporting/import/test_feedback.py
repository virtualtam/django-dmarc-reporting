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
def feedback_report(report_metadata, published_policy):
    """Dummy aggregated feedbak report"""
    meta = report_metadata
    policy = published_policy

    feedback = ET.Element('feedback')
    feedback.append(meta)
    feedback.append(policy)

    return feedback


@pytest.mark.django_db
def test_import_single_report(feedback_report):
    """Import a DMARC aggregated feedback report"""
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


@pytest.mark.django_db
def test_import_twice(feedback_report):
    """Attempt importing the same report twice"""
    feedback = feedback_report

    import_feedback_report(ET.tostring(feedback))

    with pytest.raises(DmarcImportError):
        import_feedback_report(ET.tostring(feedback))


def test_import_malformed():
    """Attempt importing a malformed XML document"""
    with pytest.raises(DmarcImportError):
        import_feedback_report('<malform></ed>')
