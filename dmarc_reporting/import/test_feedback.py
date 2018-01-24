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
    extra.text='http://scroogle.net'
    rid = ET.SubElement(meta, 'report_id')
    rid.text = '1234'
    dates = ET.SubElement(meta, 'date_range')
    beg = ET.SubElement(dates, 'begin')
    beg.text = '1513663203'
    end = ET.SubElement(dates, 'end')
    end.text = '1513749603'
    return meta


@pytest.fixture
def feedback_report(report_metadata):
    """Dummy aggregated feedbak report"""
    meta = report_metadata

    feedback = ET.Element('feedback')
    feedback.append(meta)

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
