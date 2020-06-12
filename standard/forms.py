from django import forms
from standard.models import Project, TermCategory

SHOW_COLUMNS = (
    ('definition', 'Field Definitions'),
    ('type', 'Field Types'),
)


class TermViewForm(forms.Form):
    baseProject = forms.ModelChoiceField(Project.objects.all(), label="Base Project:")
    showColumns = forms.MultipleChoiceField(required=False,label="Show Columns:", widget=forms.CheckboxSelectMultiple(), choices=SHOW_COLUMNS,)
    showProjects = forms.ModelMultipleChoiceField(Project.objects.all(), label="Show Projects:", widget=forms.CheckboxSelectMultiple())
    showCategories = forms.ModelMultipleChoiceField(TermCategory.objects.all(), required=False, label="Show Categories:", widget=forms.CheckboxSelectMultiple())

