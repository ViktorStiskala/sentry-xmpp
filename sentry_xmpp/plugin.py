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
	url = forms.CharField(label='API URL', help_text='API URL to which requests are send. It must include http:// or https://')
	name = forms.CharField(label='Athentication name', help_text='Optional authentication to HTTP server', required=False)
	passwd = forms.CharField(label='Athetnication password', required=False)

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
				name = self.get_option('name', event.project)
				passwd = self.get_option('passwd', event.project)
				if name and passwd:
					requests.post(self.get_option('url', event.project), data=data, auth=(name, passwd))
				else:
					requests.post(self.get_option('url', event.project), data=data)
