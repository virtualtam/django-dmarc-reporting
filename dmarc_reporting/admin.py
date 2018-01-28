"""django-dmarc-reporting administration settings"""
from django.contrib import admin

from .models import (AuthenticationResult, Domain, EvaluatedFeedbackPolicy,
                     FeedbackReport, FeedbackReportRecord,
                     PublishedFeedbackPolicy, Reporter)

admin.site.register(AuthenticationResult)
admin.site.register(Domain)
admin.site.register(EvaluatedFeedbackPolicy)
admin.site.register(FeedbackReport)
admin.site.register(FeedbackReportRecord)
admin.site.register(Reporter)
admin.site.register(PublishedFeedbackPolicy)
