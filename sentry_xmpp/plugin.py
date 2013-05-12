# coding=utf-8
from sentry.plugins.bases.notify import NotificationConfigurationForm
import sentry_xmpp
from sentry.plugins import Plugin
from django import forms

class MailConfigurationForm(NotificationConfigurationForm):
    send_to = forms.CharField(label='Send to', required=False,
        help_text='Enter one or more emails separated by commas or lines.',
        widget=forms.Textarea(attrs={
            'placeholder': 'you@example.com'}))

    def clean_send_to(self):
        value = self.cleaned_data['send_to']
        return ','.join(value)

class XMPPSender(Plugin):
    title = 'XMPP'
    slug = 'xmpp'
    description = 'Plugin sending error messages using XMPP. Intended for use with Jabber bot'
    version = sentry_xmpp.VERSION
    project_conf_form = MailConfigurationForm

    author = 'Viktor Stískala'

    def widget(self, request, group, **kwargs):
        return "<p>Absolutely useless widget</p>"