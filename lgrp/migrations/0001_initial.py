# Generated by Django 2.2.5 on 2020-03-24 22:55

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
            name='CollectionCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('drainage_region', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': '06-LGRP Collection Code',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Hydrology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('length', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('size', models.IntegerField(blank=True, null=True)),
                ('map_sheet', models.CharField(blank=True, max_length=50, null=True)),
                ('geom', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
            ],
            options={
                'verbose_name': '11-LGRP Hydrology',
                'verbose_name_plural': '11-LGRP Hydrology',
            },
        ),
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
                'verbose_name': '10-LGRP ID Qualifier',
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
                ('field_number', models.CharField(blank=True, max_length=50, null=True)),
                ('basis_of_record', models.CharField(blank=True, choices=[('Collection', 'Collection'), ('Observation', 'Observation')], max_length=50, verbose_name='Basis of Record')),
                ('item_type', models.CharField(blank=True, choices=[('Artifactual', 'Artifactual'), ('Faunal', 'Faunal'), ('Floral', 'Floral'), ('Geological', 'Geological')], max_length=255, verbose_name='Item Type')),
                ('item_scientific_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sci Name')),
                ('item_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Description')),
                ('item_count', models.IntegerField(blank=True, default=1, null=True)),
                ('collector', models.CharField(blank=True, choices=[('LGRP Team', 'LGRP Team'), ('K.E. Reed', 'K.E. Reed'), ('S. Oestmo', 'S. Oestmo'), ('L. Werdelin', 'L. Werdelin'), ('C.J. Campisano', 'C.J. Campisano'), ('D.R. Braun', 'D.R. Braun'), ('Tomas', 'Tomas'), ('J. Rowan', 'J. Rowan'), ('B. Villamoare', 'B. Villamoare'), ('C. Seyoum', 'C. Seyoum'), ('E. Scott', 'E. Scott'), ('E. Locke', 'E. Locke'), ('J. Harris', 'J. Harris'), ('I. Lazagabaster', 'I. Lazagabaster'), ('I. Smail', 'I. Smail'), ('D. Garello', 'D. Garello'), ('E.N. DiMaggio', 'E.N. DiMaggio'), ('W.H. Kimbel', 'W.H. Kimbel'), ('J. Robinson', 'J. Robinson'), ('M. Bamford', 'M. Bamford'), ('Zinash', 'Zinash'), ('D. Feary', 'D. Feary'), ('D. I. Garello', 'D. I. Garello')], max_length=50, null=True)),
                ('finder', models.CharField(blank=True, choices=[('LGRP Team', 'LGRP Team'), ('K.E. Reed', 'K.E. Reed'), ('S. Oestmo', 'S. Oestmo'), ('L. Werdelin', 'L. Werdelin'), ('C.J. Campisano', 'C.J. Campisano'), ('D.R. Braun', 'D.R. Braun'), ('Tomas', 'Tomas'), ('J. Rowan', 'J. Rowan'), ('B. Villamoare', 'B. Villamoare'), ('C. Seyoum', 'C. Seyoum'), ('E. Scott', 'E. Scott'), ('E. Locke', 'E. Locke'), ('J. Harris', 'J. Harris'), ('I. Lazagabaster', 'I. Lazagabaster'), ('I. Smail', 'I. Smail'), ('D. Garello', 'D. Garello'), ('E.N. DiMaggio', 'E.N. DiMaggio'), ('W.H. Kimbel', 'W.H. Kimbel'), ('J. Robinson', 'J. Robinson'), ('M. Bamford', 'M. Bamford'), ('Zinash', 'Zinash'), ('D. Feary', 'D. Feary'), ('D. I. Garello', 'D. I. Garello'), ('Afar', 'Afar')], max_length=50, null=True)),
                ('collecting_method', models.CharField(blank=True, choices=[('Survey', 'Survey'), ('Wet Screen', 'Wet Screen'), ('Crawl survey', 'Crawl survey'), ('Transect survey', 'Transect survey'), ('Dry Screen', 'Dry Screen'), ('Excavation', 'Excavation')], max_length=50, null=True)),
                ('locality_number', models.IntegerField(blank=True, null=True, verbose_name='Locality')),
                ('item_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Item #')),
                ('item_part', models.CharField(blank=True, max_length=10, null=True, verbose_name='Item Part')),
                ('old_cat_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Old Cat Number')),
                ('disposition', models.CharField(blank=True, max_length=255, null=True)),
                ('preparation_status', models.CharField(blank=True, max_length=50, null=True)),
                ('collection_remarks', models.TextField(blank=True, max_length=500, null=True)),
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
                ('weathering', models.SmallIntegerField(blank=True, choices=[(0, '0 - unweathered'), (1, '1 - parallel cracking'), (2, '2 - flaking'), (3, '3 - rough'), (4, '4 - fibrous'), (5, '5 - crumbling')], null=True)),
                ('surface_modification', models.CharField(blank=True, max_length=255, null=True)),
                ('geology_remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('collection_code', models.CharField(blank=True, choices=[('AA', 'AA'), ('AM', 'AM'), ('AM12', 'AM12'), ('AS', 'AS'), ('AT', 'AT'), ('BD', 'BD'), ('BG', 'BG'), ('BR', 'BR'), ('DK', 'DK'), ('FD', 'FD'), ('GR', 'GR'), ('HD', 'HD'), ('HS', 'HS'), ('KG', 'KG'), ('KL', 'KL'), ('KT', 'KT'), ('LD', 'LD'), ('LG', 'LG'), ('LN', 'LN'), ('LS', 'LS'), ('MF', 'MF'), ('NL', 'NL'), ('OI', 'OI'), ('SS', 'SS')], max_length=20, null=True)),
                ('drainage_region', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.FileField(blank=True, max_length=255, null=True, upload_to='uploads/images/lgrp')),
                ('verbatim_kml_data', models.TextField(blank=True, null=True)),
                ('related_catalog_items', models.CharField(blank=True, max_length=50, null=True, verbose_name='Related Catalog Items')),
                ('coll_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lgrp.CollectionCode')),
            ],
            options={
                'verbose_name': '01-LGRP Occurrence',
                'verbose_name_plural': '01-LGRP Occurrences',
                'ordering': ['collection_code', 'item_number', 'item_part'],
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
            ],
            options={
                'verbose_name': '05-LGRP Person',
                'verbose_name_plural': '05-LGRP People',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StratigraphicUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('age_ma', models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('facies_type', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': '07-LGRP Stratigraphic Unit',
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
                'verbose_name': '08-LGRP Taxon Rank',
            },
        ),
        migrations.CreateModel(
            name='Archaeology',
            fields=[
                ('occurrence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lgrp.Occurrence')),
                ('find_type', models.CharField(blank=True, max_length=255, null=True)),
                ('length_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('width_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
            ],
            options={
                'verbose_name': '02-LGRP Archaeology',
                'verbose_name_plural': '02-LGRP Archaeology',
            },
            bases=('lgrp.occurrence',),
        ),
        migrations.CreateModel(
            name='Geology',
            fields=[
                ('occurrence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lgrp.Occurrence')),
                ('find_type', models.CharField(blank=True, max_length=255, null=True)),
                ('dip', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('strike', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('color', models.CharField(blank=True, max_length=255, null=True)),
                ('texture', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': '04-LGRP Geology',
                'verbose_name_plural': '04-LGRP Geology',
            },
            bases=('lgrp.occurrence',),
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
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lgrp.Taxon')),
                ('rank', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lgrp.TaxonRank')),
            ],
            options={
                'verbose_name': '09-LGRP Taxon',
                'verbose_name_plural': '09-LGRP Taxa',
                'ordering': ['rank__ordinal', 'name'],
            },
        ),
        migrations.AddField(
            model_name='occurrence',
            name='collector_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_collector', to='lgrp.Person'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='finder_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_finder', to='lgrp.Person'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='unit_found',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='occurrence_unit_found', to='lgrp.StratigraphicUnit'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='unit_likely',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='occurrence_unit_likely', to='lgrp.StratigraphicUnit'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='unit_simplified',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='occurrence_unit_simplified', to='lgrp.StratigraphicUnit'),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/images')),
                ('description', models.TextField(blank=True, null=True)),
                ('occurrence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='occurrence_images', to='lgrp.Occurrence')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='uploads/files')),
                ('description', models.TextField(blank=True, null=True)),
                ('occurrence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='occurrence_files', to='lgrp.Occurrence')),
            ],
        ),
        migrations.CreateModel(
            name='Biology',
            fields=[
                ('occurrence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lgrp.Occurrence')),
                ('sex', models.CharField(blank=True, max_length=50, null=True)),
                ('life_stage', models.CharField(blank=True, max_length=50, null=True)),
                ('biology_remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('verbatim_taxon', models.CharField(blank=True, max_length=1024, null=True)),
                ('verbatim_identification_qualifier', models.CharField(blank=True, max_length=255, null=True)),
                ('taxonomy_remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('identified_by', models.CharField(blank=True, choices=[('D. Braun', 'D. Braun'), ('J. Thompson', 'J. Thompson'), ('E. Scott', 'E. Scott'), ('E. Locke', 'E. Locke'), ('A.E. Shapiro', 'A.E. Shapiro'), ('A.W. Gentry', 'A.W. Gentry'), ('B.J. Schoville', 'B.J. Schoville'), ('B.M. Latimer', 'B.M. Latimer'), ('C. Denys', 'C. Denys'), ('C.A. Lockwood', 'C.A. Lockwood'), ('D. Geraads', 'D. Geraads'), ('D.C. Johanson', 'D.C. Johanson'), ('E. Delson', 'E. Delson'), ('B. Villmoare', 'B. Villmoare'), ('E.S. Vrba', 'E.S. Vrba'), ('F.C. Howell', 'F.C. Howell'), ('G. Petter', 'G. Petter'), ('G. Suwa', 'G. Suwa'), ('G.G. Eck', 'G.G. Eck'), ('H.B. Krentza', 'H.B. Krentza'), ('H.B. Wesselman', 'H.B. Wesselman'), ('H.B.S. Cooke', 'H.B.S. Cooke'), ('Institute Staff', 'Institute Staff'), ('J.C. Rage', 'J.C. Rage'), ('K.E. Reed', 'K.E. Reed'), ('L.A. Werdelin', 'L.A. Werdelin'), ('L.J. Flynn', 'L.J. Flynn'), ('M. Sabatier', 'M. Sabatier'), ('M.E. Lewis', 'M.E. Lewis'), ('N. Fessaha', 'N. Fessaha'), ('P. Brodkorb', 'P. Brodkorb'), ('R. Bobe-Quinteros', 'R. Bobe-Quinteros'), ('R. Geze', 'R. Geze'), ('R.L. Bernor', 'R.L. Bernor'), ('S.R. Frost', 'S.R. Frost'), ('T.D. White', 'T.D. White'), ('T.K. Nalley', 'T.K. Nalley'), ('V. Eisenmann', 'V. Eisenmann'), ('W.H. Kimbel', 'W.H. Kimbel'), ('Z. Alemseged', 'Z. Alemseged'), ('S. Oestmo', 'S. Oestmo'), ('J. Rowan', 'J. Rowan'), ('C.J. Campisano', 'C.J. Campisano'), ('J. Robinson', 'J. Robinson'), ('I. Smail', 'I. Smail'), ('I. Lazagabaster', 'I. Lazagabaster'), ('A. Rector', 'A. Rector')], max_length=100, null=True)),
                ('year_identified', models.IntegerField(blank=True, null=True)),
                ('type_status', models.CharField(blank=True, max_length=50, null=True)),
                ('fauna_notes', models.TextField(blank=True, max_length=64000, null=True)),
                ('side', models.CharField(blank=True, choices=[('L', 'L'), ('R', 'R'), ('Indeterminate', 'Indeterminate'), ('L+R', 'L+R')], max_length=50, null=True)),
                ('element', models.CharField(blank=True, choices=[('astragalus', 'astragalus'), ('bacculum', 'bacculum'), ('bone (indet.)', 'bone (indet.)'), ('calcaneus', 'calcaneus'), ('canine', 'canine'), ('capitate', 'capitate'), ('carapace', 'carapace'), ('carpal (indet.)', 'carpal (indet.)'), ('carpal/tarsal', 'carpal/tarsal'), ('carpometacarpus', 'carpometacarpus'), ('carpus', 'carpus'), ('chela', 'chela'), ('clavicle', 'clavicle'), ('coccyx', 'coccyx'), ('coprolite', 'coprolite'), ('cranium', 'cranium'), ('cranium w/horn core', 'cranium w/horn core'), ('cuboid', 'cuboid'), ('cubonavicular', 'cubonavicular'), ('cuneiform', 'cuneiform'), ('dermal plate', 'dermal plate'), ('egg shell', 'egg shell'), ('endocast', 'endocast'), ('ethmoid', 'ethmoid'), ('femur', 'femur'), ('fibula', 'fibula'), ('frontal', 'frontal'), ('hamate', 'hamate'), ('horn core', 'horn core'), ('humerus', 'humerus'), ('hyoid', 'hyoid'), ('Ilium', 'Ilium'), ('incisor', 'incisor'), ('innominate', 'innominate'), ('ischium', 'ischium'), ('lacrimal', 'lacrimal'), ('long bone ', 'long bone '), ('lunate', 'lunate'), ('mandible', 'mandible'), ('manus', 'manus'), ('maxilla', 'maxilla'), ('metacarpal', 'metacarpal'), ('metapodial', 'metapodial'), ('metatarsal', 'metatarsal'), ('molar', 'molar'), ('nasal', 'nasal'), ('navicular', 'navicular'), ('naviculocuboid', 'naviculocuboid'), ('occipital', 'occipital'), ('ossicone', 'ossicone'), ('parietal', 'parietal'), ('patella', 'patella'), ('pes', 'pes'), ('phalanx', 'phalanx'), ('pisiform', 'pisiform'), ('plastron', 'plastron'), ('premaxilla', 'premaxilla'), ('premolar', 'premolar'), ('pubis', 'pubis'), ('radioulna', 'radioulna'), ('radius', 'radius'), ('rib', 'rib'), ('sacrum', 'sacrum'), ('scaphoid', 'scaphoid'), ('scapholunar', 'scapholunar'), ('scapula', 'scapula'), ('scute', 'scute'), ('sesamoid', 'sesamoid'), ('shell', 'shell'), ('skeleton', 'skeleton'), ('skull', 'skull'), ('sphenoid', 'sphenoid'), ('sternum', 'sternum'), ('talon', 'talon'), ('talus', 'talus'), ('tarsal (indet.)', 'tarsal (indet.)'), ('tarsometatarsus', 'tarsometatarsus'), ('tarsus', 'tarsus'), ('temporal', 'temporal'), ('tibia', 'tibia'), ('tibiotarsus', 'tibiotarsus'), ('tooth (indet.)', 'tooth (indet.)'), ('trapezium', 'trapezium'), ('trapezoid', 'trapezoid'), ('triquetrum', 'triquetrum'), ('ulna', 'ulna'), ('vertebra', 'vertebra'), ('vomer', 'vomer'), ('zygomatic', 'zygomatic')], max_length=50, null=True)),
                ('element_modifier', models.CharField(blank=True, choices=[('articulated', 'articulated'), ('caudal', 'caudal'), ('cervical', 'cervical'), ('coccygeal', 'coccygeal'), ('distal', 'distal'), ('intermediate', 'intermediate'), ('lower', 'lower'), ('lumbar', 'lumbar'), ('manual', 'manual'), ('manual distal', 'manual distal'), ('manual intermediate', 'manual intermediate'), ('manual proximal', 'manual proximal'), ('pedal', 'pedal'), ('pedal distal', 'pedal distal'), ('pedal intermediate', 'pedal intermediate'), ('pedal proximal', 'pedal proximal'), ('proximal', 'proximal'), ('sacral', 'sacral'), ('thoracic', 'thoracic'), ('upper', 'upper'), ('indeterminate', 'indeterminate')], max_length=50, null=True)),
                ('element_portion', models.CharField(blank=True, choices=[('almost complete', 'almost complete'), ('anterior', 'anterior'), ('basal', 'basal'), ('complete', 'complete'), ('diaphysis', 'diaphysis'), ('diaphysis+distal', 'diaphysis+distal'), ('diaphysis+proximal', 'diaphysis+proximal'), ('distal', 'distal'), ('dorsal', 'dorsal'), ('epiphysis', 'epiphysis'), ('fragment', 'fragment'), ('fragments', 'fragments'), ('indeterminate', 'indeterminate'), ('lateral', 'lateral'), ('medial', 'medial'), ('midsection', 'midsection'), ('midsection+basal', 'midsection+basal'), ('midsection+distal', 'midsection+distal'), ('posterior', 'posterior'), ('proximal', 'proximal'), ('symphysis', 'symphysis'), ('ventral', 'ventral')], max_length=50, null=True)),
                ('element_number', models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('3(medial)', '3(medial)'), ('4', '4'), ('4(lateral)', '4(lateral)'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('2-7', '2-7'), ('8-12', '8-12'), ('indeterminate', 'indeterminate')], max_length=50, null=True)),
                ('element_remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('tooth_upper_or_lower', models.CharField(blank=True, max_length=50, null=True)),
                ('tooth_number', models.CharField(blank=True, max_length=50, null=True)),
                ('tooth_type', models.CharField(blank=True, max_length=50, null=True)),
                ('uli1', models.BooleanField(default=False)),
                ('uli2', models.BooleanField(default=False)),
                ('uli3', models.BooleanField(default=False)),
                ('uli4', models.BooleanField(default=False)),
                ('uli5', models.BooleanField(default=False)),
                ('uri1', models.BooleanField(default=False)),
                ('uri2', models.BooleanField(default=False)),
                ('uri3', models.BooleanField(default=False)),
                ('uri4', models.BooleanField(default=False)),
                ('uri5', models.BooleanField(default=False)),
                ('ulc', models.BooleanField(default=False)),
                ('urc', models.BooleanField(default=False)),
                ('ulp1', models.BooleanField(default=False)),
                ('ulp2', models.BooleanField(default=False)),
                ('ulp3', models.BooleanField(default=False)),
                ('ulp4', models.BooleanField(default=False)),
                ('urp1', models.BooleanField(default=False)),
                ('urp2', models.BooleanField(default=False)),
                ('urp3', models.BooleanField(default=False)),
                ('urp4', models.BooleanField(default=False)),
                ('ulm1', models.BooleanField(default=False)),
                ('ulm2', models.BooleanField(default=False)),
                ('ulm3', models.BooleanField(default=False)),
                ('urm1', models.BooleanField(default=False)),
                ('urm2', models.BooleanField(default=False)),
                ('urm3', models.BooleanField(default=False)),
                ('lli1', models.BooleanField(default=False)),
                ('lli2', models.BooleanField(default=False)),
                ('lli3', models.BooleanField(default=False)),
                ('lli4', models.BooleanField(default=False)),
                ('lli5', models.BooleanField(default=False)),
                ('lri1', models.BooleanField(default=False)),
                ('lri2', models.BooleanField(default=False)),
                ('lri3', models.BooleanField(default=False)),
                ('lri4', models.BooleanField(default=False)),
                ('lri5', models.BooleanField(default=False)),
                ('llc', models.BooleanField(default=False)),
                ('lrc', models.BooleanField(default=False)),
                ('llp1', models.BooleanField(default=False)),
                ('llp2', models.BooleanField(default=False)),
                ('llp3', models.BooleanField(default=False)),
                ('llp4', models.BooleanField(default=False)),
                ('lrp1', models.BooleanField(default=False)),
                ('lrp2', models.BooleanField(default=False)),
                ('lrp3', models.BooleanField(default=False)),
                ('lrp4', models.BooleanField(default=False)),
                ('llm1', models.BooleanField(default=False)),
                ('llm2', models.BooleanField(default=False)),
                ('llm3', models.BooleanField(default=False)),
                ('lrm1', models.BooleanField(default=False)),
                ('lrm2', models.BooleanField(default=False)),
                ('lrm3', models.BooleanField(default=False)),
                ('indet_incisor', models.BooleanField(default=False)),
                ('indet_canine', models.BooleanField(default=False)),
                ('indet_premolar', models.BooleanField(default=False)),
                ('indet_molar', models.BooleanField(default=False)),
                ('indet_tooth', models.BooleanField(default=False)),
                ('deciduous', models.BooleanField(default=False)),
                ('um_tooth_row_length_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('um_1_length_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('um_1_width_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('um_2_length_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('um_2_width_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('um_3_length_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('um_3_width_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('lm_tooth_row_length_mm', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('lm_1_length', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('lm_1_width', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('lm_2_length', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('lm_2_width', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('lm_3_length', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('lm_3_width', models.DecimalField(blank=True, decimal_places=8, max_digits=38, null=True)),
                ('identification_qualifier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lgrp_id_qualifier_bio_occurrences', to='lgrp.IdentificationQualifier')),
                ('qualifier_taxon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lgrp_qualifier_taxon_bio_occurrences', to='lgrp.Taxon')),
                ('taxon', models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='lgrp_taxon_bio_occurrences', to='lgrp.Taxon')),
            ],
            options={
                'verbose_name': '03-LGRP Biology',
                'verbose_name_plural': '03-LGRP Biology',
            },
            bases=('lgrp.occurrence',),
        ),
    ]
