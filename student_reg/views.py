from __future__ import absolute_import
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required

from student_reg.models import Student, EmergencyContact, Person

def index(request):
  return TemplateResponse(request, 'index.html')


# FORMS
from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelform_factory, inlineformset_factory
from localflavor.us import forms as usforms
class StudentForm(forms.ModelForm):
  class Meta:
    model = Student
    exclude = ('registration_date',)

class EmergencyContactForm(forms.ModelForm):
  class Meta:
    model = EmergencyContact
    exclude = ('state', 'father', 'mother', 'other', 'authorized')
  zip_code = usforms.USZipCodeField()

class PersonForm(forms.ModelForm):
  class Meta:
    model = Person
    fields = '__all__'

AuthorizationFormSet = formset_factory(
    Student, modelform_factory(Person, exclude=('phone_number',)))

@login_required
def query(request):
  if request.method == 'POST':
    raise ''
  else:
    student_form = StudentForm(prefix='stu')
    emerg_contact = EmergencyContactForm(prefix='eme')
    father = PersonForm(prefix='father')
    mother = PersonForm(prefix='mother')
    other = PersonForm(prefix='other')
    authorized = AuthorizationFormSet()
  ctx = {
    'student': student_form, 'emerg_contact': emerg_contact,
    'father': father, 'mother': mother, 'other': other,
    'authorized': authorized,
  }
  return TemplateResponse(request, 'student_reg/query.html', ctx)
