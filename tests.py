from django.core import mail
from django.template.defaultfilters import slugify
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from ct_groups.models import CTGroup, GroupMembership, CTPost, CTEvent, \
	PERM_CHOICE_EDITOR, PERM_CHOICE_GROUP_MEMBER, process_digests
from ct_template.models import ClinTemplate
import datetime

def _delay(seconds):
	t = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
	while t > datetime.datetime.now():
		pass

class CTTemplateTest(TestCase):

	def _make_group(self, name, is_public=True):
		"""docstring for _make_group"""
		group = CTGroup(
			name = name,
			slug = slugify(name),
			# note = models.TextField(blank=True),
			# tags = TagField(),
			is_public = is_public
		)
		group.save()
		return group
	
	def _make_user(self, username):
		"""docstring for _make_user"""
		user, created = User.objects.get_or_create(
			username=username,
			first_name=username.capitalize(),
			last_name='Hoojie',
			email='%s@ganzie.com' % username
			)
		return user
	
	def _make_membership(self, user, group, is_active=True, is_editor=False, updates='single'):
		"""docstring for _make_membership"""
		member = GroupMembership(user=user, group=group)
		member.is_active = is_active
		member.is_editor = is_editor
		member.post_updates = updates
		member.tool_updates = updates
		member.save()
		return member

	def setUp(self):
		group1 = self._make_group('Test group one')
		group2 = self._make_group('Test group two')
		group3 = self._make_group('Test group three')
		user = self._make_user('shuggie')
		member = self._make_membership(user, group1, False)
		user = self._make_user('francie')
		member = self._make_membership(user, group2, False)
		user = self._make_user('ella')
		member = self._make_membership(user, group2, True, True)
		member = self._make_membership(user, group3)
		user = self._make_user('josie')
		member = self._make_membership(user, group1, True, True, 'digest')
		member = self._make_membership(user, group2, True, True, 'digest')
		member = self._make_membership(user, group3, True, True, 'digest')
		user = self._make_user('hubert')
		member = self._make_membership(user, group2, True, False, 'digest')
		


	def test_template(self):
		"""
		.
		"""
		group1 = CTGroup.objects.get(name='Test group one')
		group2 = CTGroup.objects.get(name='Test group two')
		user = self._make_user('chic')
		
		template = ClinTemplate(xmlmodel=ct_xml, workgroup=group2)
		template.save()
		template.add_comment("i001", "a big fat comment", user)
		template.add_comment("i001", "another big fat comment ", user)
		# print template.get_comment(c)
		
		self.assertEquals(len(mail.outbox), 2)
		self.assertEquals(mail.outbox[0].subject, '[example.com] Test group two update')
		self.assertEquals(len(mail.outbox[0].bcc), 1)

		mail.outbox = []
		self.failUnlessEqual(CTEvent.objects.count(), 2)
		process_digests()
		self.assertEquals(len(mail.outbox), 1)
		# print
		# print mail.outbox[0].bcc
		# print mail.outbox[0].subject
		# print mail.outbox[0].body
		# print
		# print mail.outbox[1].bcc
		# print mail.outbox[1].subject
		# print mail.outbox[1].body
		
		# events should be cleared
		self.failUnlessEqual(CTEvent.objects.count(), 0)
		
		

ct_xml = """		<!DOCTYPE clinicaltemplate SYSTEM "dcm.dtd">
		<clinicaltemplate>
		    <metadata>
		        <note>Observation: Level of consciousness by using the the Glasgow Coma Scale.</note>
		        <template_id>glasgow-coma-scale</template_id>
		        <label>Glasgow Coma Scale</label>
		        <version>061</version>
		        <status>draft</status>
		        <source>results4care.nl</source>
		    </metadata>
		    <item id="i001" label="Total Glasgow Coma Scale Score" valueType="integer">
		          <review_comments>
		            <review_comment id="i001:c0" author="guest" author_type="anonymous" review_date="20061115T1259">Test comment 0
		            </review_comment>
		            <review_comment id="i001:c1" author="guest" author_type="anonymous" review_date="20061115T1402">Test comment 1
		            </review_comment>
		        </review_comments></item>
		    <item id="i010" label="Eye opening" valueType="ordinal_list">
		        <valueset>
		            <value score="4">Spontaneous</value>
		            <value score="3">To speech</value>
		            <value score="2">To pain</value>
		            <value score="1">No response</value>
		            <value score="C">Not possible to determine</value>
		        </valueset>
		    </item>
		    <item id="i020" label="Best verbal response" valueType="ordinal_list" widget="radioset">
		        <valueset>
		            <value score="6">To verbal command: obeys</value>
		            <value score="5">To painful stimulus: localizes pain</value>
		            <value score="4">Flexion-withdrawal</value>
		            <value score="3">Flexion-abnormal</value>
		            <value score="2">Extension</value>
		            <value score="1">No response</value>
		            <value score="P">Paralysis</value>
		        </valueset>
		    </item>
		    <item id="i030" label="Best motor response" valueType="ordinal_list">
		        <valueset>
		            <value score="5">Oriented and converses</value>
		            <value score="4">Disoriented and converses</value>
		            <value score="3">Inappropriate words</value>
		            <value score="2">Incomprehensible sounds</value>
		            <value score="1">No response</value>
		            <value score="T">Tube/Tracheotomy</value>
		        </valueset>
		    </item>
		</clinicaltemplate>
"""
		