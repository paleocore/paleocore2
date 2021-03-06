# Generated by Django 2.2.13 on 2020-07-10 19:43

import ckeditor.fields
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IdentificationQualifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('name', models.CharField(blank=True, max_length=15, unique=True)),
                ('qualified', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '{app_label.upper()} ID Qualifier',
                'verbose_name_plural': '{app_label.upper()} ID Qualifiers',
            },
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('georeference_remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('formation', models.CharField(blank=True, max_length=50, null=True)),
                ('member', models.CharField(blank=True, max_length=50, null=True)),
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('collection_code', models.CharField(blank=True, max_length=10, null=True)),
                ('locality_number', models.IntegerField(blank=True, null=True)),
                ('sublocality', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('stratigraphic_section', models.CharField(blank=True, max_length=50, null=True)),
                ('upper_limit_in_section', models.IntegerField(blank=True, null=True)),
                ('lower_limit_in_section', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('error_notes', models.CharField(blank=True, max_length=255, null=True)),
                ('notes', models.CharField(blank=True, max_length=254, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('date_last_modified', models.DateTimeField(auto_now=True, verbose_name='Date Last Modified')),
            ],
            options={
                'verbose_name': '{app_label.upper()} Locality',
                'verbose_name_plural': '{app_label.upper()} Localities',
                'ordering': ('locality_number', 'sublocality'),
            },
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('georeference_remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('date_recorded', models.DateTimeField(blank=True, help_text='Date and time the item was observed or collected.', null=True, verbose_name='Date Rec')),
                ('year_collected', models.IntegerField(blank=True, help_text='The year, event or field campaign during which the item was found.', null=True, verbose_name='Year')),
                ('barcode', models.IntegerField(blank=True, help_text='For collected items only.', null=True, verbose_name='Barcode')),
                ('basis_of_record', models.CharField(blank=True, help_text='e.g. Observed item or Collected item', max_length=50, verbose_name='Basis of Record')),
                ('field_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Field Number')),
                ('item_type', models.CharField(blank=True, max_length=255, verbose_name='Item Type')),
                ('item_scientific_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sci Name')),
                ('item_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Description')),
                ('item_count', models.IntegerField(blank=True, default=1, null=True, verbose_name='Item Count')),
                ('collector', models.CharField(blank=True, max_length=50, null=True, verbose_name='Collector')),
                ('finder', models.CharField(blank=True, max_length=50, null=True, verbose_name='Finder')),
                ('collecting_method', models.CharField(blank=True, max_length=50, null=True, verbose_name='Collecting Method')),
                ('item_number', models.IntegerField(blank=True, null=True, verbose_name='Item #')),
                ('item_part', models.CharField(blank=True, max_length=10, null=True, verbose_name='Item Part')),
                ('cat_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Cat Number')),
                ('disposition', models.CharField(blank=True, max_length=255, null=True, verbose_name='Disposition')),
                ('preparation_status', models.CharField(blank=True, max_length=50, null=True, verbose_name='Prep Status')),
                ('collection_remarks', models.TextField(blank=True, max_length=255, null=True, verbose_name='Collection Remarks')),
                ('stratigraphic_formation', models.CharField(blank=True, max_length=255, null=True, verbose_name='Formation')),
                ('stratigraphic_member', models.CharField(blank=True, max_length=255, null=True, verbose_name='Member')),
                ('analytical_unit_1', models.CharField(blank=True, max_length=255, null=True)),
                ('analytical_unit_2', models.CharField(blank=True, max_length=255, null=True)),
                ('analytical_unit_3', models.CharField(blank=True, max_length=255, null=True)),
                ('analytical_unit_found', models.CharField(blank=True, max_length=255, null=True)),
                ('analytical_unit_likely', models.CharField(blank=True, max_length=255, null=True)),
                ('analytical_unit_simplified', models.CharField(blank=True, max_length=255, null=True)),
                ('in_situ', models.BooleanField(default=False)),
                ('ranked', models.BooleanField(default=False)),
                ('weathering', models.SmallIntegerField(blank=True, null=True)),
                ('surface_modification', models.CharField(blank=True, max_length=255, null=True, verbose_name='Surface Mod')),
                ('geology_remarks', models.TextField(blank=True, max_length=500, null=True, verbose_name='Geol Remarks')),
                ('collection_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='Collection Code')),
                ('drainage_region', models.CharField(blank=True, max_length=255, null=True, verbose_name='Drainage Region')),
                ('image', models.FileField(blank=True, max_length=255, null=True, upload_to='uploads/images/hrp')),
            ],
            options={
                'verbose_name': 'HRP Occurrence',
                'verbose_name_plural': 'HRP Occurrences',
                'ordering': ['collection_code', 'locality', 'item_number', 'item_part'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('last_name', models.CharField(blank=True, max_length=256, null=True, verbose_name='Last Name')),
                ('first_name', models.CharField(blank=True, max_length=256, null=True, verbose_name='First Name')),
            ],
            options={
                'verbose_name': 'HRP Person',
                'verbose_name_plural': 'HRP People',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='TaxonRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('plural', models.CharField(max_length=50, unique=True)),
                ('ordinal', models.IntegerField(unique=True)),
            ],
            options={
                'verbose_name': 'PSR Taxon Rank',
                'verbose_name_plural': 'PSR Taxon Ranks',
            },
        ),
        migrations.CreateModel(
            name='Archaeology',
            fields=[
                ('occurrence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='psr.Occurrence')),
                ('find_type', models.CharField(blank=True, max_length=255, null=True)),
                ('length_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('width_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
            ],
            options={
                'verbose_name': 'PSR Archaeology',
                'verbose_name_plural': 'PSR Archaeology',
            },
            bases=('psr.occurrence',),
        ),
        migrations.CreateModel(
            name='Geology',
            fields=[
                ('occurrence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='psr.Occurrence')),
                ('find_type', models.CharField(blank=True, max_length=255, null=True)),
                ('dip', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('strike', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('color', models.CharField(blank=True, max_length=255, null=True)),
                ('texture', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'PSR Geology',
                'verbose_name_plural': 'PSR Geology',
            },
            bases=('psr.occurrence',),
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('label', models.CharField(blank=True, help_text='For a species, the name field contains the specific epithet and the label contains the full\n    scientific name, e.g. Homo sapiens, name = sapiens, label = Homo sapiens', max_length=244, null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='psr.Taxon')),
                ('rank', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='psr.TaxonRank')),
            ],
            options={
                'verbose_name': '{app_label.upper()} Taxon',
                'verbose_name_plural': '{app_label.upper()} Taxa',
            },
        ),
        migrations.AddField(
            model_name='occurrence',
            name='found_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='occurrence_found_by', to='psr.Person'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='locality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='psr.Locality'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='recorded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='occurrence_recorded_by', to='psr.Person'),
        ),
        migrations.CreateModel(
            name='Biology',
            fields=[
                ('occurrence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='psr.Occurrence')),
                ('sex', models.CharField(blank=True, max_length=50, null=True, verbose_name='Sex')),
                ('life_stage', models.CharField(blank=True, max_length=50, null=True, verbose_name='Life Stage')),
                ('size_class', models.CharField(blank=True, max_length=50, null=True, verbose_name='Size Class')),
                ('verbatim_taxon', models.CharField(blank=True, max_length=1024, null=True)),
                ('verbatim_identification_qualifier', models.CharField(blank=True, max_length=255, null=True)),
                ('taxonomy_remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('type_status', models.CharField(blank=True, max_length=50, null=True)),
                ('fauna_notes', models.TextField(blank=True, max_length=64000, null=True)),
                ('identification_qualifier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hrp_id_qualifier_bio_occurrences', to='psr.IdentificationQualifier')),
                ('qualifier_taxon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hrp_qualifier_taxon_bio_occurrences', to='psr.Taxon')),
                ('taxon', models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='hrp_taxon_bio_occurrences', to='psr.Taxon')),
            ],
            options={
                'verbose_name': 'PSR Biology',
                'verbose_name_plural': 'PSR Biology',
            },
            bases=('psr.occurrence',),
        ),
    ]
