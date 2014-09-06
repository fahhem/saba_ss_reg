# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(default=b'CA', max_length=255)),
                ('zip_code', localflavor.us.models.USPostalCodeField(max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FM', b'Federated States of Micronesia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MH', b'Marshall Islands'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PW', b'Palau'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('home_phone', localflavor.us.models.PhoneNumberField(max_length=20)),
                ('father_email', models.EmailField(max_length=75)),
                ('mother_email', models.EmailField(max_length=75)),
                ('other_relationship', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('phone_number', localflavor.us.models.PhoneNumberField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(max_length=255)),
                ('middle_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('birthday', models.DateField()),
                ('gender', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('school_grade', models.CharField(max_length=5, choices=[(b'11', b'11'), (b'10', b'10'), (b'KG', b'Kindergarten'), (b'1', b'1'), (b'3', b'3'), (b'2', b'2'), (b'5', b'5'), (b'4', b'4'), (b'7', b'7'), (b'6', b'6'), (b'9', b'9'), (b'PK', b'Pre-K'), (b'8', b'8')])),
                ('doctor_name', models.CharField(max_length=255)),
                ('doctor_contact', localflavor.us.models.PhoneNumberField(max_length=20)),
                ('allergies', models.TextField()),
                ('medication', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='emergencycontact',
            name='authorized',
            field=models.ManyToManyField(related_name=b'+', to='student_reg.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emergencycontact',
            name='father',
            field=models.ForeignKey(related_name=b'+', to='student_reg.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emergencycontact',
            name='mother',
            field=models.ForeignKey(related_name=b'+', to='student_reg.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emergencycontact',
            name='other',
            field=models.ForeignKey(to='student_reg.Person'),
            preserve_default=True,
        ),
    ]
