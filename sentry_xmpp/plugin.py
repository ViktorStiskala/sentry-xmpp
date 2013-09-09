# coding=utf-8
from sentry.plugins import Plugin
from sentry.utils.http import absolute_uri
import sentry_xmpp
from django import forms
from django.core.validators import email_re, ValidationError
from django.core.urlresolvers import reverse
import re
import requests
from urlparse import urljoin
split_re = re.compile(r'\s*,\s*|\s+')


class XMPPSiteConfigurationForm(forms.Form):
    url = forms.URLField(label='API URL', help_text='API URL to which requests are send. It must include http:// or https://')
    name = forms.CharField(label='Authentication name', help_text='Optional authentication to HTTP server', required=False)
    password = forms.CharField(label='Authentication password', required=False, widget=forms.PasswordInput)


class XMPPConfigurationForm(forms.Form):
    send_to = forms.CharField(label='Send to', required=False,
        help_text='Enter one or more JIDs separated by commas or lines.',
        widget=forms.Textarea(attrs={
            'placeholder': 'you@example.com'}))

    def clean_send_to(self):
        value = self.cleaned_data['send_to']
        jids = filter(bool, split_re.split(value))

        for jid in jids:
            if not email_re.match(jid):
                raise ValidationError('%s is not a valid e-mail address.' % jid)

        return ','.join(jids)


class XMPPSender(Plugin):
    title = 'XMPP'
    slug = 'xmpp'
    description = 'Plugin sending error messages using XMPP. Intended for use with Jabber bot'
    conf_title = 'XMPP'
    version = sentry_xmpp.VERSION
    project_default_enabled = True
    project_conf_form = XMPPConfigurationForm
    project_conf_template = 'sentry_xmpp/project_configuration.html'
    site_conf_form = XMPPSiteConfigurationForm

    author = 'Viktor Stískala'

    # def __init__(self, min_level=0, include_loggers=None, exclude_loggers=None, *args, **kwargs):
    #     super(XMPPSender, self).__init__(*args, **kwargs)
    #     self.min_level = min_level
    #     self.include_loggers = include_loggers
    #     self.exclude_loggers = exclude_loggers

    # def get_group_url(self, group):
    #     return absolute_uri(reverse('sentry-group', args=[
    #         group.team.slug,
    #         group.project.slug,
    #         group.id,
    #     ]))
    #
    # def post_process(self, group, event, is_new, is_sample, **kwargs):
    #     if is_new:
    #         url = self.get_group_url(group)
    #         send_to = self.get_option('send_to', event.project)
    #         jids = filter(bool, split_re.split(send_to))
    #         for jid in jids:
    #             data = {"text": "In project %s there was an error %s\nIf you want to know more, visit: %s" % (event.project.name, event.message, url), "to": jid}
    #             name = self.get_option('name', event.project)
    #             passwd = self.get_option('passwd', event.project)
    #
    #             if name and passwd:
    #                 requests.post(urljoin(self.get_option('url', event.project), '/message/'), data=data, auth=(name, passwd))
    #             else:
    #                 requests.post(urljoin(self.get_option('url', event.project), '/message/'), data=data)
