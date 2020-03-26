from django import forms
from .models import Occurrence


class UploadKMLForm(forms.Form):
    kmlfileUpload = forms.FileField(
        label='Upload a kml/kmz file, *.kml or *.kmz ',
    )


class DownloadKMLForm(forms.Form):
    FILE_TYPE_CHOICES = (('1', 'KML',), ('2', 'KMZ',))
    kmlfileDownload = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect,
        choices=FILE_TYPE_CHOICES,
        label="File Type: "
    )


class UploadForm(forms.Form):
    shapefileUpload = forms.FileField(
        label='Upload a shape file, *.shp',
    )
    shapefileIndexUpload = forms.FileField(
        label='Upload a shape file index, *.shx',
    )
    shapefileDataUpload = forms.FileField(
        label='Upload shape file data, *.dbf',
    )

class ChangeXYForm(forms.ModelForm):
    class Meta:
        model = Occurrence
        fields = ["barcode", "item_scientific_name", "item_description"]
    DB_id = forms.IntegerField( max_value=100000)
    old_easting = forms.DecimalField(max_digits=12)
    old_northing = forms.DecimalField(max_digits=12)
    new_easting = forms.DecimalField(max_digits=12)
    new_northing = forms.DecimalField(max_digits=12)
