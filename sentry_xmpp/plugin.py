# coding=utf-8
from sentry.models import Option
from sentry.plugins import Plugin
import sentry_xmpp
from django import forms
from django.core.validators import email_re, ValidationError
import re
import requests
from urlparse import urljoin
split_re = re.compile(r'\s*,\s*|\s+')


class XMPPSiteConfigurationForm(forms.Form):
    url = forms.URLField(label='API URL', help_text='API URL to which requests are send. It must include http:// or https://')
    name = forms.CharField(label='Authentication name', help_text='Optional authentication to HTTP server', required=False)
    password = forms.CharField(label='Authentication password', required=False, widget=forms.PasswordInput(render_value=True))


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

    def get_form_initial(self, project=None):
        if project is None:
            return {option.key[5:]: option.value for option in Option.objects.filter(key__startswith='xmpp:')}
        return super(XMPPSender, self).get_form_initial(project)

    def get_option(self, key, project=None, user=None):
        """
        Simple tweak to overcome strange behavior of metadata cache
        """
        if project is None and user is None:
            options = {o.key: o.value for o in Option.objects.filter(key__startswith=self._get_option_key(''))}
            try:
                return options[self._get_option_key(key)]
            except KeyError:
                return ''
        return super(XMPPSender, self).get_option(key, project, user)

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        if is_new:
            log_url = group.get_absolute_url()

            send_to = self.get_option('send_to', event.project)
            jids = filter(bool, split_re.split(send_to))

            for jid in jids:
                data = {
                    'to': jid,
                    'text': '"{e.message}" in project "{e.project.name}" {url}'.format(e=event, url=log_url),
                }

                # optional HTTP auth
                kwargs = {}
                if self.get_option('name'):
                    kwargs['auth'] = (self.get_option('name'), self.get_option('passwd'))

                requests.post(urljoin(self.get_option('url'), '/message/'), data=data, **kwargs)
