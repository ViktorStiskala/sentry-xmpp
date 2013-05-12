# coding=utf-8
from sentry.plugins.bases.notify import NotificationPlugin
import sentry_xmpp
from django import forms
from django.core.validators import email_re, ValidationError
import re
split_re = re.compile(r'\s*,\s*|\s+')


class XMPPConfigurationForm(forms.Form):
	send_to = forms.CharField(label='Send to', required=False,
		help_text='Enter one or more JIDs separated by commas or lines.',
		widget=forms.Textarea(attrs={
			'placeholder': 'you@example.com'}))

	def clean_send_to(self):
		print 'something'
		value = self.cleaned_data['send_to']
		jids = filter(bool, split_re.split(value))

		for jid in jids:
			if not email_re.match(jid):
				raise ValidationError('%s is not a valid e-mail address.' % jid)

		return ','.join(jids)


class XMPPSender(NotificationPlugin):
	title = 'XMPP'
	slug = 'xmpp'
	description = 'Plugin sending error messages using XMPP. Intended for use with Jabber bot'
	version = sentry_xmpp.VERSION
	project_conf_form = XMPPConfigurationForm

	author = 'Viktor Stískala'

	def __init__(self, min_level=0, include_loggers=None, exclude_loggers=None,
				send_to=None, *args, **kwargs):
		super(XMPPSender, self).__init__(*args, **kwargs)
		self.min_level = min_level
		self.include_loggers = include_loggers
		self.exclude_loggers = exclude_loggers
		self.send_to = send_to

	def post_process(self, group, event, is_new, is_sample, **kwargs):
		print kwargs, self.send_to, group, event, is_new, is_sample