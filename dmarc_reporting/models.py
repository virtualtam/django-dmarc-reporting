"""django-dmarc-reporting models"""
# pylint: disable=too-few-public-methods
from django.db import models


class Reporter(models.Model):
    """DMARC report issuer"""

    org_name = models.CharField(
        max_length=50,
        unique=True,
    )
    email = models.EmailField()
    extra_contact_info = models.CharField(
        max_length=254,
        blank=True
    )


class Domain(models.Model):
    """Internet Domain Name"""

    name = models.CharField(
        max_length=254,
        unique=True,
    )


class PublishedFeedbackPolicy(models.Model):
    """DMARC policy published for a given domain"""

    NONE = 'none'
    QUARANTINE = 'quarantine'
    REJECT = 'reject'
    POLICY_CHOICES = (
        (NONE, NONE),
        (QUARANTINE, QUARANTINE),
        (REJECT, REJECT),
    )

    RELAXED = 'r'
    STRICT = 's'
    POLICY_ALIGNMENT_CHOICES = (
        (RELAXED, "relaxed"),
        (STRICT, "strict"),
    )

    domain = models.ForeignKey(
        Domain,
        on_delete=models.CASCADE,
    )
    alignment_dkim = models.CharField(
        max_length=1,
        choices=POLICY_ALIGNMENT_CHOICES,
        default=RELAXED,
    )
    alignment_spf = models.CharField(
        max_length=1,
        choices=POLICY_ALIGNMENT_CHOICES,
        default=RELAXED,
    )
    policy = models.CharField(
        max_length=10,
        choices=POLICY_CHOICES,
        default=NONE,
    )
    subdomain_policy = models.CharField(
        max_length=10,
        choices=POLICY_CHOICES,
        default=NONE,
    )
    percentage = models.IntegerField(default=100)


class FeedbackReport(models.Model):
    """DMARC aggregated feedback report"""

    reporter = models.ForeignKey(
        Reporter,
        on_delete=models.CASCADE,
    )
    report_id = models.CharField(max_length=254)
    date_begin = models.DateTimeField()
    date_end = models.DateTimeField()
    policy_published = models.OneToOneField(
        PublishedFeedbackPolicy,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta():
        """FeedbackReport model metadata"""

        unique_together = (('reporter', 'report_id'),)


class FeedbackReportRecord(models.Model):
    """DMARC aggregated feedback report record"""

    report = models.ForeignKey(
        FeedbackReport,
        on_delete=models.CASCADE,
    )
    source_ip = models.GenericIPAddressField()
    count = models.PositiveIntegerField()
    header_from = models.ForeignKey(
        'Domain',
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True,
    )
    envelope_from = models.ForeignKey(
        'Domain',
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True,
    )


class EvaluatedFeedbackPolicy(models.Model):
    """Evaluated DMARC policy"""

    record = models.OneToOneField(
        FeedbackReportRecord,
        on_delete=models.CASCADE,
    )
    disposition = models.CharField(max_length=20)
    dkim_pass = models.BooleanField()
    spf_pass = models.BooleanField()


class AuthenticationResult(models.Model):
    """DKIM and SPF authentication result"""

    DKIM = 'dkim'
    SPF = 'spf'
    TYPE_CHOICE = (
        (DKIM, DKIM),
        (SPF, SPF),
    )

    FAIL = 'fail'
    PASS = 'pass'
    SOFTFAIL = 'softfail'
    RESULT_CHOICE = (
        (FAIL, FAIL),
        (PASS, PASS),
        (SOFTFAIL, SOFTFAIL),
    )

    domain = models.ForeignKey(
        Domain,
        on_delete=models.CASCADE,
    )
    record = models.ForeignKey(
        FeedbackReportRecord,
        on_delete=models.CASCADE,
    )
    result_type = models.CharField(
        max_length=8,
        choices=TYPE_CHOICE,
        default=DKIM,
    )
    result = models.CharField(
        max_length=4,
        choices=RESULT_CHOICE,
        default=FAIL,
    )
    selector = models.CharField(max_length=20)
    scope = models.CharField(max_length=20)
