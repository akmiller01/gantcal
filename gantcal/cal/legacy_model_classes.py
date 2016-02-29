from django.db import models
from django.db.models.fields import Field

class MyBooleanField(models.BooleanField):

    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "MyBooleanField"

    def db_type(self, connection):
        return "text"

    def to_python(self, value):
        if value in (True, False): return value
        if value in ('t', 'True', 'true', '1', '\x01'): return True  
        if value in ('f', 'False', 'false', '0', '\x00'): return False

    def get_db_prep_value(self, value, connection,prepared=False):
        value = super(MyBooleanField, self).get_db_prep_value(value, connection, prepared)
        return 'true' if value else 'false'

class BooleanField(Field):
    empty_strings_allowed = False
    default_error_messages = {
        'invalid': ("'%(value)s' value must be either True or False."),
    }
    description = ("Boolean (Either True or False)")

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super(BooleanField, self).__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super(BooleanField, self).check(**kwargs)
        errors.extend(self._check_null(**kwargs))
        return errors

    def _check_null(self, **kwargs):
        if getattr(self, 'null', False):
            return [
                checks.Error(
                    'BooleanFields do not accept null values.',
                    hint='Use a NullBooleanField instead.',
                    obj=self,
                    id='fields.E110',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(BooleanField, self).deconstruct()
        del kwargs['blank']
        return name, path, args, kwargs

    def get_internal_type(self):
        return "BooleanField"

    def to_python(self, value):
        if value in (True, False):
            # if value is 1 or 0 than it's equal to True or False, but we want
            # to return a true bool for semantic reasons.
            return bool(value)
        if value in ('t', 'True', 'true', '1'):
            return True
        if value in ('f', 'False', 'false', '0'):
            return False
        raise exceptions.ValidationError(
            self.error_messages['invalid'],
            code='invalid',
            params={'value': value},
        )

    def get_prep_lookup(self, lookup_type, value):
        # Special-case handling for filters coming from a Web request (e.g. the
        # admin interface). Only works for scalar values (not lists). If you're
        # passing in a list, you might as well make things the right type when
        # constructing the list.
        if value in ('1', '0'):
            value = bool(int(value))
        return super(BooleanField, self).get_prep_lookup(lookup_type, value)

    def get_prep_value(self, value):
        value = super(BooleanField, self).get_prep_value(value)
        if value is None:
            return None
        return bool(value)

    def formfield(self, **kwargs):
        # Unlike most fields, BooleanField figures out include_blank from
        # self.null instead of self.blank.
        if self.choices:
            include_blank = not (self.has_default() or 'initial' in kwargs)
            defaults = {'choices': self.get_choices(include_blank=include_blank)}
        else:
            defaults = {'form_class': forms.BooleanField}
        defaults.update(kwargs)
        return super(BooleanField, self).formfield(**defaults)
    
class Theme(models.Model):
    title = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(max_length=255,unique=True,editable=False)
    description = models.TextField(null=True,blank=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super(Theme, self).save(*args, **kwargs)
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i' % (
                slugify(self.title), self.id
            )
        super(Theme, self).save(*args, **kwargs)