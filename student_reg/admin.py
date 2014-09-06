# -*- coding: utf8 -*-
from django import forms
from django.db import models
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from utils.reverseadmin import ReverseModelAdmin

from .models import Student, EmergencyContact, Person
from .views import EmergencyContactForm, PersonForm

NOTES = '''
Please review the dress code, attendance, and other policies described in the
SAB informational brochure. In particular, please note the following:
<ul style="list-style:circle">
<li>Parents and family members, who enter the SAB premises to drop off or pick
up their children, or to participate in SAB events, are also required to adhere
to the SAB dress code.</li>

<li>Regular attendance and punctuality are required. The assembly preceding
classes and prayer following classes are both part of the weekly school session
and barring exceptional cases, students must attend this entire school
session.</li>
</ul>

<p>As parent/guardian of the student whose name appears above, I hereby release
and waive any claim against School of Ahlul’Bait (SAB), Shi’a Muslim
Association of Bay Area (SABA), as well as SAB / SABA officers, directors,
agents, employees, and volunteers for any damage or injury suffered by the
students on account of or in connection with the student’s participation in
school related activities.

This Waiver and Release of Liability shall operate as a complete waiver and
release for any personal injury, missing person, death, and waiver of property
or other damage or loss, including loss of use, which may arise in connection
with the student’s participation in the school related activity. I acknowledge
that I am aware of the risks associated with the school related activities,
whether the risks are by reason of preparation for participation,
transportation of the students, exposing the students to the elements and to
general public, or otherwise exposing the students to risks which may or may
not be generally associated with the school related activities.

I also agree to adhere to the dress code policy and other general policies of
School of Ahlul’Bait as described in the SAB informational brochure to the best
of my abilities.
'''
LIABILITY = '''
My signature authorizes SAB in the case of an emergency to provide medical
treatment by the local on call doctor for SABA. I also acknowledge and agree
that Shi’a Association of Bay Area (SABA) and the School of Ahlul'Bait faculty
cannot be held responsible in any way, nor assume any liability whatsoever, for
acts of any delays, changes, modifications, negligence, non performance due to
the breakdown of machinery and equipment OR due to disturbance, strike, riots
or wars wherever declared or not OR due to any other cause which is beyond the
control of the said parties.
'''

class PlainTextWidget(forms.Widget):
    def __init__(self, text):
        self._text = text
        super(PlainTextWidget, self).__init__()
    def render(self, _name, value, attrs):
        return mark_safe(self._text)

class BaseStudentAdminForm(forms.ModelForm):
  class Meta:
    model = Student
    fields = '__all__'
  emergency_info_id = forms.ModelChoiceField(
          widget=forms.HiddenInput(), queryset=EmergencyContact.objects.all(),
          required=False)
  authorized_people = forms.CharField(widget=forms.Textarea(), required=False)
  notes = forms.CharField(widget=PlainTextWidget(NOTES), label='Notes and Waiver')
  liability = forms.CharField(widget=PlainTextWidget(LIABILITY), label='Liability and Responsibility')
extra_fields = {f.name: f.formfield() for f in EmergencyContact._meta.fields}
extra_fields['address'].widget.attrs['size'] = 50
prefix_person_fields = lambda prefix: SortedDict([
    (prefix+'-'+f.name, f.formfield()) for f in Person._meta.fields
    if not isinstance(f, models.AutoField)])
extra_fields['father'].widget = forms.HiddenInput()
extra_fields['father'].required = False
extra_fields.update(prefix_person_fields('father'))
extra_fields['father_email'].label = 'Email'

extra_fields['mother'].widget = forms.HiddenInput()
extra_fields['mother'].required = False
extra_fields.update(prefix_person_fields('mother'))
extra_fields['mother_email'].label = 'Email'

extra_fields['other'].widget = forms.HiddenInput()
extra_fields['other'].required = False
extra_fields.update(prefix_person_fields('other'))
extra_fields['other_relationship'].label = 'Relationship'
StudentAdminForm = type('StudentAdminForm', (BaseStudentAdminForm,), extra_fields)

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    pass

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
  def name(self, obj):
      return '%s %s' % (obj.first_name, obj.last_name)
  def father_name(self, obj):
      return '%s %s' % (obj.emergency_info.father.first_name, obj.emergency_info.father.last_name)
  father_name.short_description = "Father's name"
  def mother_name(self, obj):
      return '%s %s' % (obj.emergency_info.mother.first_name, obj.emergency_info.mother.last_name)
  mother_name.short_description = "Mother's name"
  list_display = ('name', 'father_name', 'mother_name')
  search_fields = [
      'first_name', 'last_name',
      'emergency_info__father__first_name', 'emergency_info__father__last_name',
      'emergency_info__mother__first_name', 'emergency_info__mother__last_name',
      'emergency_info__other__first_name', 'emergency_info__other__last_name',
  ]

  form = StudentAdminForm
  fieldsets = [
    (None, {
      'fields': [
          ('first_name', 'middle_name'),
          'last_name',
          ('birthday', 'gender', 'school_grade'),
          ('doctor_name', 'doctor_contact'),
          'allergies', 'medication'
      ],
    }),
    ('Emergency Response Information', {
        'fields': ['emergency_info_id', 'address', ('city', 'state', 'zip_code'), 'home_phone']}),
    ('Father', {'fields': ['father', prefix_person_fields('father').keys(), 'father_email'],}),
    ('Mother', {'fields': ['mother', prefix_person_fields('mother').keys(), 'mother_email'],}),
    ('Emergency Contact other than either parent', {
        'fields': ['other', prefix_person_fields('other').keys(), 'other_relationship'],}),
    ('Authorized people', {
        'description': 'First and last names of people authorized to pick up your child/ren (list one per line)',
        'fields': ['authorized_people'],
    }),
    ('Important', {'fields': ['notes', 'liability']}),
  ]

  def get_form(self, request, obj=None, **kwargs):
    form = super(StudentAdmin, self).get_form(request, obj=obj, **kwargs)
    if not obj:
        # It's empty, so it's ready.
        return form

    # Can't be get_changeform_initial_data because we need obj.
    def form_maker(*args, **kwargs):
        form_instance = form(*args, **kwargs)
        print form_instance.initial
        initial = form_instance.initial
        # Fill in non-student values.
        form_instance.data['emergency_info_id'] = obj.emergency_info.id
        for field in EmergencyContact._meta.fields:
            if not isinstance(field, models.CharField):
                continue
            initial[field.name] = getattr(obj.emergency_info, field.name)

        initial['father'] = obj.emergency_info.father.id
        for field_name, field in prefix_person_fields('father').iteritems():
            initial[field_name] = getattr(obj.emergency_info.father, field_name.split('-', 1)[1])
        initial['mother'] = obj.emergency_info.mother.id
        for field_name, field in prefix_person_fields('mother').iteritems():
            initial[field_name] = getattr(obj.emergency_info.mother, field_name.split('-', 1)[1])
        initial['other'] = obj.emergency_info.other.id
        for field_name, field in prefix_person_fields('other').iteritems():
            initial[field_name] = getattr(obj.emergency_info.other, field_name.split('-', 1)[1])
        initial['authorized_people'] = '\n'.join([
            ' '.join(names).strip()
            for names in obj.emergency_info.authorized.values_list('first_name', 'last_name')])
        # print initial
        return form_instance
    return form_maker

  def save_model(self, request, obj, form, change):
    # print request,obj,form,change
    ec = None
    father = mother = other = None
    if change:
        ec = EmergencyContact.objects.get(id=request.POST['emergency_info_id'])
        if 'father' in request.POST:
            father = Person.objects.get(id=request.POST['father'])
        if 'mother' in request.POST:
            mother = Person.objects.get(id=request.POST['mother'])
        other = Person.objects.get(id=request.POST['other'])
    ec = EmergencyContactForm(request.POST, instance=ec)
    father = PersonForm(request.POST, prefix='father', instance=father)
    mother = PersonForm(request.POST, prefix='mother', instance=mother)
    other = PersonForm(request.POST, prefix='other', instance=other)
    ec = ec.save(commit=False)
    if father.is_valid():
        ec.father = father.save()
    if mother.is_valid():
        ec.mother = mother.save()
    if not ec.father and not ec.mother:
        raise ValidationError('Student requires at least one parent.')
    ec.other = other.save()
    ec.save()
    for line in request.POST['authorized_people'].split('\n'):
        if not line.strip():
            continue
        fname, lname = (' ' + line).rsplit(' ', 1)
        ec.authorized.get_or_create(first_name=fname.strip(), last_name=lname.strip())
    obj.emergency_info = ec
    obj.save()

  def response_add(self, request, obj, post_url_continue=None):
    meta = self.model._meta
    return HttpResponseRedirect(reverse(
        'admin:saved_redirect', kwargs={'id': obj.id}, current_app=self.admin_site.name))
  response_change = response_add

  def get_urls(self):
    from django.conf.urls import url
    urls = super(StudentAdmin, self).get_urls()
    urls = [
      url(r'^saved/(?P<id>\d+)/$', self.admin_site.admin_view(self.saved_view), name='saved_redirect'),
    ] + urls
    return urls

  def saved_view(self, request, id):
    opts = self.model._meta
    next = reverse('admin:%s_%s_changelist' % (opts.app_label, opts.model_name))
    return TemplateResponse(request, 'admin/saved.html', {'id': id, 'next': next})

