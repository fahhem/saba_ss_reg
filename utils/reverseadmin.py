'''
https://gist.github.com/ramusus/4343464
adminreverse from here http://djangosnippets.org/snippets/2032/
changed for working with ForeignKeys
'''
'''
reverseadmin
============
Module that makes django admin handle OneToOneFields in a better way.
 
A common use case for one-to-one relationships is to "embed" a model
inside another one. For example, a Person may have multiple foreign
keys pointing to an Address entity, one home address, one business
address and so on. Django admin displays those relations using select
boxes, letting the user choose which address entity to connect to a
person. A more natural way to handle the relationship is using
inlines. However, since the foreign key is placed on the owning
entity, django admins standard inline classes can't be used. Which is
why I created this module that implements "reverse inlines" for this
use case.
 
Example:
 
    from django.db import models
    class Address(models.Model):
        street = models.CharField(max_length = 255)
        zipcode = models.CharField(max_length = 10)
        city = models.CharField(max_length = 255)
    class Person(models.Model):
        name = models.CharField(max_length = 255)
        business_addr = models.ForeignKey(Address,
                                             related_name = 'business_addr')
        home_addr = models.OneToOneField(Address, related_name = 'home_addr')
        other_addr = models.OneToOneField(Address, related_name = 'other_addr')
 
This is how standard django admin renders it:
 
    http://img9.imageshack.us/i/beforetz.png/
 
Here is how it looks when using the reverseadmin module:
 
    http://img408.imageshack.us/i/afterw.png/
 
You use reverseadmin in the following way:
 
    from django.contrib import admin
    from django.db import models
    from models import Person
    from reverseadmin import ReverseModelAdmin
    class AddressForm(models.Form):
        pass
    class PersonAdmin(ReverseModelAdmin):
        inline_type = 'tabular'
        inline_reverse = ('business_addr', ('home_addr', AddressForm), ('other_addr' (
            'form': OtherForm
            'exclude': ()
        )))
    admin.site.register(Person, PersonAdmin)
 
inline_type can be either "tabular" or "stacked" for tabular and
stacked inlines respectively.
 
The module is designed to work with Django 1.1.1. Since it hooks into
the internals of the admin package, it may not work with later Django
versions.
'''
from django.contrib.admin import helpers, ModelAdmin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.util import flatten_fieldsets
from django.db import transaction, models
from django.db.models import OneToOneField, ForeignKey
from django.forms import ModelForm
from django.forms.formsets import all_valid
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.encoding import force_unicode
from django.utils.functional import curry
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
 
class ReverseInlineFormSet(BaseModelFormSet):
    '''
    A formset with either a single object or a single empty
    form. Since the formset is used to render a required OneToOne
    relation, the forms must not be empty.
    '''
    model = None
    parent_fk_name = ''
    def __init__(self,
                 data = None,
                 files = None,
                 instance = None,
                 prefix = None,
                 queryset = None,
                 save_as_new = False):
        try:
          object = getattr(instance, self.parent_fk_name)
        except AttributeError:
          qs = self.model.objects.filter(pk = -1)
          self.extra = 1
        else:
          qs = self.model.objects.filter(pk = object.id)
        super(ReverseInlineFormSet, self).__init__(data, files,
                                                       prefix = prefix,
                                                       queryset = qs)
        for form in self.forms:
            form.empty_permitted = False
 
def reverse_inlineformset_factory(parent_model,
                                  model,
                                  parent_fk_name,
                                  form = ModelForm,
                                  fields = None,
                                  exclude = None,
                                  formfield_callback = lambda f: f.formfield()):
    kwargs = {
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': ReverseInlineFormSet,
        'extra': 0,
        'can_delete': False,
        'can_order': False,
        'fields': fields,
        'exclude': exclude,
        'max_num': 1,
        'fields': '__all__',
    }
    FormSet = modelformset_factory(model, **kwargs)
    FormSet.parent_fk_name = parent_fk_name
    return FormSet
 
class ReverseInlineModelAdmin(InlineModelAdmin):
    '''
    Use the name and the help_text of the owning models field to
    render the verbose_name and verbose_name_plural texts.
    '''
    def __init__(self,
                 parent_model,
                 parent_fk_name,
                 model, admin_site,
                 inline_type):
        self.template = 'admin/edit_inline/%s.html' % inline_type
        self.parent_fk_name = parent_fk_name
        self.model = model
        field_descriptor = getattr(parent_model, self.parent_fk_name)
        field = field_descriptor.field
 
        self.verbose_name_plural = field.verbose_name.title()
        self.verbose_name = field.help_text
        if not self.verbose_name:
            self.verbose_name = self.verbose_name_plural
        super(ReverseInlineModelAdmin, self).__init__(parent_model, admin_site)
 
    def get_formset(self, request, obj = None, **kwargs):
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        # if exclude is an empty list we use None, since that's the actual
        # default
        exclude = (exclude + kwargs.get("exclude", [])) or None
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        return reverse_inlineformset_factory(self.parent_model,
                                             self.model,
                                             self.parent_fk_name,
                                             **defaults)
 
class ReverseModelAdmin(ModelAdmin):
    '''
    Patched ModelAdmin class. The add_view method is overridden to
    allow the reverse inline formsets to be saved before the parent
    model.
    '''
    def __init__(self, model, admin_site):
 
        super(ReverseModelAdmin, self).__init__(model, admin_site)
        if self.exclude is None:
            self.exclude = []
 
        inline_instances = []
        for field_name in self.inline_reverse:
 
            kwargs = {}
            if isinstance(field_name, tuple):
                if isinstance(field_name[1], dict):
                    kwargs = field_name[1]
                elif isinstance(field_name[1], ModelForm):
                    kwargs['form'] = field_name[1]
                field_name = field_name[0]
 
            field = model._meta.get_field(field_name)
            if isinstance(field, (OneToOneField, ForeignKey)):
                name = field.name
                parent = field.related.parent_model
                inline = ReverseInlineModelAdmin(model,
                                                 name,
                                                 parent,
                                                 admin_site,
                                                 self.inline_type)
                if kwargs:
                    inline.__dict__.update(kwargs)
                inline_instances.append(inline)
                self.exclude.append(name)
        self.tmp_inline_instances = inline_instances
    
    def get_inline_instances(self, request, obj=None):
        return self.tmp_inline_instances + super(ReverseModelAdmin, self).get_inline_instances(request, obj)
