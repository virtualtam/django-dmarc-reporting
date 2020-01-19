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

    def __str__(self):
        return self.org_name


class Domain(models.Model):
    """Internet Domain Name"""

    name = models.CharField(
        max_length=254,
        unique=True,
    )

    def __str__(self):
        return self.name


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

    def __str__(self):
        return "%s - (adkim=%s, aspf=%s, p=%s, sp=%s, pct=%d)" % (
            self.domain,
            self.alignment_dkim,
            self.alignment_spf,
            self.policy,
            self.subdomain_policy,
            int(self.percentage),
        )

    class Meta():
        """Model metadata"""

        verbose_name_plural = "Published feedback policies"


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

    def __str__(self):
        return "%s - %s" % (self.reporter, self.report_id)

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

    def __str__(self):
        return "%s - %s" % (self.report, self.source_ip)


class EvaluatedFeedbackPolicy(models.Model):
    """Evaluated DMARC policy"""

    record = models.OneToOneField(
        FeedbackReportRecord,
        on_delete=models.CASCADE,
    )
    disposition = models.CharField(max_length=20)
    dkim_pass = models.BooleanField()
    spf_pass = models.BooleanField()

    def __str__(self):
        return "%s - (disposition=%s, dkim=%s, spf=%s)" % (
            self.record,
            self.disposition,
            self.dkim_pass,
            self.spf_pass,
        )

    class Meta():
        """Model metadata"""

        verbose_name_plural = "Evaluated feedback policies"


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
        max_length=8,
        choices=RESULT_CHOICE,
        default=FAIL,
    )
    selector = models.CharField(max_length=20)
    scope = models.CharField(max_length=20)

    def __str__(self):
        if self.selector:
            return "%s - (%s=%s, selector=%s)" % (
                self.domain,
                self.result_type,
                self.result,
                self.selector
            )
        if self.scope:
            return "%s - (%s=%s, scope=%s)" % (
                self.domain,
                self.result_type,
                self.result,
                self.scope
            )
        return "%s - (%s=%s)" % (
            self.domain,
            self.result_type,
            self.result,
        )
