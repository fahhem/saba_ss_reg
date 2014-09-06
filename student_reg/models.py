from django.db import models
from localflavor.us import models as usmodels

GENDER_CHOICES = [
  ('M', 'Male'),
  ('F', 'Female'),
]

GRADE_CHOICES = [
  ('PK', "Pre-K"),
  ('KG', "Kindergarten"),
] + [(str(g), str(g)) for g in range(1, 13)]

class Person(models.Model):
  first_name = models.CharField(max_length=255)
  last_name = models.CharField(max_length=255)
  phone_number = usmodels.PhoneNumberField(null=True, blank=True)

class EmergencyContact(models.Model):
  address = models.CharField(max_length=255)
  city = models.CharField(max_length=255)
  state = models.CharField(max_length=255, default='CA')
  zip_code = models.CharField(max_length=12)
  home_phone = usmodels.PhoneNumberField()
  father = models.OneToOneField(Person, related_name='+', null=True)
  father_email = models.EmailField(null=True, blank=True)
  mother = models.OneToOneField(Person, related_name='+', null=True)
  mother_email = models.EmailField(null=True, blank=True)
  other = models.OneToOneField(Person)
  other_relationship = models.CharField(max_length=255)
  authorized = models.TextField(null=True, blank=True)

class Student(models.Model):
  registration_date = models.DateTimeField(auto_now_add=True)
  first_name = models.CharField(max_length=255)
  middle_name = models.CharField(max_length=255, null=True, blank=True)
  last_name = models.CharField(max_length=255)
  birthday = models.DateField()
  gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
  school_grade = models.CharField(max_length=5, choices=GRADE_CHOICES)
  doctor_name = models.CharField(max_length=255)
  doctor_contact = usmodels.PhoneNumberField()
  allergies = models.TextField(null=True, blank=True)
  medication = models.TextField(null=True, blank=True)
  emergency_info = models.ForeignKey(EmergencyContact)

