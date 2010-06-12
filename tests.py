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
		member = self._make_membership(user, group1, True, False, 'digest')
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

		template1 = ClinTemplate(xmlmodel=incl_xml, workgroup=group1)
		template1.save()
		
		template2 = ClinTemplate(xmlmodel=ct_xml, workgroup=group2)
		template2.save()
		template2.included_templates.add(template1)
		template2.save()
		# print template2.metadata
		# print template2.name
		template1.add_comment("i001", "a big fat comment", user)
		template1.add_comment("i001", "another big fat comment ", user)
		# print template.get_comment(c)
		self.assertEquals(template2.label, 'Glasgow Coma Scale')
		# self.assertEquals(template2.metadata.get('template_id', 'no label set'), 'glasgow-coma-scale')
		# print template2.metadata['template_id'].text

		self.assertEquals(len(mail.outbox), 2)
		self.assertEquals(mail.outbox[0].subject, '[example.com] Test group two update')
		self.assertEquals(len(mail.outbox[0].bcc), 1)

		mail.outbox = []
		self.failUnlessEqual(CTEvent.objects.count(), 4)
		process_digests()
		self.assertEquals(len(mail.outbox), 2)
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
		
		

ct_xml = """
	<clinicaltemplate>
	    <metadata>
	        <item id="m010" label="note">Observation: Level of consciousness by using the the Glasgow Coma Scale.</item>
	        <item id="m020" label="template_id">glasgow-coma-scale</item>
	        <item id="m030" label="label">Glasgow Coma Scale</item>
	        <item id="m040" label="version">061</item>
	        <item id="m050" label="status">draft</item>
	        <item id="m060" label="source">results4care.nl</item>
	    </metadata>
		<model>
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
			<item id="i040" label="Skin problems" valueType="include_template" include="infant-skin-problems"></item>
		</model>
		<documentation>
			<item id="d001" label="Purpose" markup="textile">

				To record and monitor the level of consciousness of a patient (NVICV, 2008).

				Het vaststellen en bewaken van het bewustzijnsniveau van een patient (NVICV, 2008).

				h3. Reason

				Measuring the level of consciousness is important for the diagnoses, the prognosis and for follow-up of the condition of the patient.

				Het meten van het bewustzijnsniveau is bealngrijk voor de diagnose, de prognose en het volgen van de conditie van de patient.

				h3. Target Users

				Monitoring patients (NVICV, 2010):
				- after intracranial surgery
				- in case of neurological disorders (CVA, encefalitis, meningitis)
				- the level of consciousness with trauma patients
				- after intoxication with substances which can influence the level of consciousness

		        <review_comments>
					<review_comment author="Derek Hoy" author_type="member" id="d001:c0" review_date="20100421T0105">commentosos.</review_comment>
					<review_comment author="William Goossen" author_type="member" id="d001:c1" review_date="20100427T2316">comontosos whiskeyanos perplexos Fryske Hynder
						http://www.usheitdistillery.nl/welkom.html </review_comment>
					<review_comment author="Derek Hoy" author_type="member" id="d001:c2" review_date="20100429T1330">lorem ipsum etc etc</review_comment>
					<review_comment author="Derek Hoy" author_type="member" id="d001:c3" review_date="20100429T1338">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</review_comment>
					<review_comment author="William Goossen" author_type="member" id="d001:c4" review_date="20100604T1109">Derek, I still miss here a set of content areas such as instructions, references, interpretations, care process. Can you add these too?</review_comment>
				</review_comments>
		</item>

		<item id="d002" label="Evidence Base" markup="textile">

			The Glasgow Coma Scale is used to record and monitor the level of consciousness of patients with a lowered consciousness because of brain injury. Measuring the level of consciousness is important for the diagnoses, the prognosis and for follow-up of the condition of the patient. The latter to be able to detect a further drop of consciousness, on time, so action can be taken. There are separate directions of use for adults and children. This model describes the use of the GCS for adults. For children there is developed an adapted Pediatric Glasgow Coma Scale (PGCS). This is described in a separated DCM.

			The developers are the first to report the Glasgow Coma Scale as a scale to record coma after trauma (Teasdale en Jennett, 1974). The Glasgow Coma Scale is an international accepted scale which gives a good estimate of the severity of the brain injury. This results in the fact that in the 'CBO richtlijn: ernstig traumatisch hersenletsel' (2002) (guideline for severe traumatic brain injury), the Glasgow Coma Scale is the only instrument for determining the level of consciousness within this category of patients that is mentioned. All abstract words with which a drop of consciousness is described is actually a 'translation' of what one can observe with the patient, this means what the patient does, spontaneous or after stimulation. The gain of the Glasgow Coma Scale is that this scale only reflects what the patient does, in simple terms (Bruining, Lauwers &amp;amp; Thijs, 1991). For 'CVA-ketenzorg' (CVA Chain of Care Information System) the description and evaluation of Meijer (2004) are applicable. He listed a couple of instruments concerning prognosis and that way optimized the route of the CVA patient through the Chain of Care. Moreover the psychometric traits of the instruments have been analysed, among others based on Wade (1994).
		</item>
		
		
		</documentation>
	</clinicaltemplate>
"""
incl_xml="""
	<clinicaltemplate>
		<metadata>
	        <item id="m010" label="note">This is a simple summary which will normally be used as part of a larger template.</item>
	        <item id="m020" label="template_id">infant-skin-problems</item>
	        <item id="m030" label="label">Infant skin problems</item>
	        <item id="m040" label="version">0.1</item>
	        <item id="m050" label="status">draft</item>
	        <item id="m060" label="source">NHS Tayside community systems</item>
		</metadata>
		<model>
		    <item id="i001" label="Infant skin problems" select="multi_select" valueType="nominal_list">
		        <valueset>
		            <value>Dryness</value>
		            <value>Rash</value>
		            <value>Scabies</value>
		            <value>Ringworm</value>
		            <value>Thrush</value>
		            <value>Impetigo</value>
		        </valueset>
		    <review_comments><review_comment author="guest" author_type="anonymous" review_date="20071016T1445">From a data standards viewpoint items such as this would cause problems as there are 2 concepts within the values, ie skin symptoms and skin diseases.
		Rgds
		Alison Wallis</review_comment></review_comments></item>
		</model>
	</clinicaltemplate>
"""		