from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory

from labster.models import Lab
from labster_search.models import LabKeyword


class LabKeywordForm(forms.ModelForm):

    display_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control"}))
    display_rank = forms.FloatField(widget=forms.TextInput(attrs={'class': "form-control"}))

    class Meta:
        models = LabKeyword
        fields = (
            'display_name',
        )

    def __init__(self, *args, **kwargs):
        super(LabKeywordForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['display_rank'].initial = self.instance.rank / 100.0

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        kwargs['commit'] = False
        obj = super(LabKeywordForm, self).save(*args, **kwargs)
        obj.keyword = data['display_name'].lower().strip()
        obj.rank = int(data['display_rank'] * 100)
        obj.save()
        return obj


class BaseLabKeywordFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        queryset = LabKeyword.objects\
            .filter(
                keyword_type=LabKeyword.KEYWORD_PRIMARY,
                source=LabKeyword.SOURCE_MANUAL)\
            .exclude(display_name='').order_by('-rank')
        kwargs['queryset'] = queryset
        super(BaseLabKeywordFormSet, self).__init__(*args, **kwargs)


LabKeywordFormSet = inlineformset_factory(
    Lab, LabKeyword, form=LabKeywordForm, formset=BaseLabKeywordFormSet)
