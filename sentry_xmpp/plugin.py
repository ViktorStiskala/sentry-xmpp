# coding=utf-8
from sentry.plugins.bases.notify import NotificationPlugin
from sentry.utils.http import absolute_uri
import sentry_xmpp
from django import forms
from django.core.validators import email_re, ValidationError
from django.core.urlresolvers import reverse
import re
import requests
split_re = re.compile(r'\s*,\s*|\s+')


class XMPPConfigurationForm(forms.Form):
	send_to = forms.CharField(label='Send to', required=False,
		help_text='Enter one or more JIDs separated by commas or lines.',
		widget=forms.Textarea(attrs={
			'placeholder': 'you@example.com'}))
	domain = forms.CharField(label='API Domain', help_text='API domain to which requests are send.')

	def clean_send_to(self):
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

	def __init__(self, min_level=0, include_loggers=None, exclude_loggers=None, *args, **kwargs):
		super(XMPPSender, self).__init__(*args, **kwargs)
		self.min_level = min_level
		self.include_loggers = include_loggers
		self.exclude_loggers = exclude_loggers

	def get_group_url(self, group):
		return absolute_uri(reverse('sentry-group', args=[
			group.team.slug,
			group.project.slug,
			group.id,
		]))

	def post_process(self, group, event, is_new, is_sample, **kwargs):
		if is_new:
			url = self.get_group_url(group)
			send_to = self.get_option('send_to', event.project)
			jids = filter(bool, split_re.split(send_to))
			for jid in jids:
				data = {"type": "message", "text": "In project %s there was an error %s\nIf you want to know more, visit: %s" % (event.project.name, event.message, url), "to": jid}
				url = 'http://%s/' % self.get_option('domain', event.project)
				requests.post(url, data=data)
