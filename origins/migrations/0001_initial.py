# Generated by Django 2.2.13 on 2020-07-03 19:36

import ckeditor.fields
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import modelcluster.contrib.taggit
import modelcluster.fields
import uuid
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtaildocs', '0010_document_file_hash'),
        ('wagtailimages', '0001_squashed_0021'),
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
    ]

    operations = [
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('geological_formation', models.CharField(blank=True, max_length=50, null=True, verbose_name='Formation')),
                ('geological_member', models.CharField(blank=True, max_length=50, null=True, verbose_name='Member')),
                ('geological_bed', models.CharField(blank=True, max_length=50, null=True)),
                ('older_interval', models.CharField(blank=True, max_length=50, null=True)),
                ('younger_interval', models.CharField(blank=True, max_length=50, null=True)),
                ('max_age', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('min_age', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('best_age', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('origins', models.BooleanField(default=False)),
                ('source', models.CharField(blank=True, max_length=20, null=True)),
                ('verbatim_collection_no', models.IntegerField(blank=True, null=True)),
                ('verbatim_record_type', models.CharField(blank=True, max_length=20, null=True)),
                ('verbatim_formation', models.CharField(blank=True, max_length=50, null=True)),
                ('verbatim_member', models.CharField(blank=True, max_length=50, null=True)),
                ('verbatim_lng', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('verbatim_lat', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('verbatim_collection_name', models.CharField(blank=True, max_length=200, null=True)),
                ('verbatim_collection_subset', models.CharField(blank=True, max_length=20, null=True)),
                ('verbatim_collection_aka', models.CharField(blank=True, max_length=200, null=True)),
                ('verbatim_n_occs', models.IntegerField(blank=True, null=True)),
                ('verbatim_early_interval', models.CharField(blank=True, max_length=50, null=True)),
                ('verbatim_late_interval', models.CharField(blank=True, max_length=50, null=True)),
                ('verbatim_max_ma', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('verbatim_min_ma', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('verbatim_reference_no', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Fossil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.URLField(blank=True, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('catalog_number', models.CharField(blank=True, max_length=40, null=True)),
                ('organism_id', models.CharField(blank=True, max_length=40, null=True)),
                ('nickname', models.CharField(blank=True, max_length=40, null=True)),
                ('holotype', models.BooleanField(default=False)),
                ('lifestage', models.CharField(blank=True, max_length=20, null=True)),
                ('sex', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('project_name', models.CharField(blank=True, max_length=100, null=True)),
                ('project_abbreviation', models.CharField(blank=True, max_length=10, null=True)),
                ('collection_code', models.CharField(blank=True, max_length=10, null=True)),
                ('place_name', models.CharField(blank=True, max_length=100, null=True)),
                ('locality', models.CharField(blank=True, max_length=40, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Country')),
                ('continent', models.CharField(blank=True, choices=[('Africa', 'Africa'), ('Antarctica', 'Antarctica'), ('Asia', 'Asia'), ('Australia', 'Australia'), ('Europe', 'Europe'), ('North America', 'North America'), ('South America', 'South America')], max_length=20, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('image', models.ImageField(blank=True, max_length=255, null=True, upload_to='uploads/images/origins')),
                ('source', models.CharField(blank=True, max_length=100, null=True)),
                ('created_by', models.CharField(blank=True, max_length=100, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Modified')),
                ('modified', models.DateTimeField(auto_now=True, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('origins', models.BooleanField(default=False)),
                ('verbatim_PlaceName', models.CharField(blank=True, max_length=100, null=True)),
                ('verbatim_HomininElement', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_HomininElementNotes', models.TextField(blank=True, null=True)),
                ('verbatim_SkeletalElement', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementSubUnit', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementSubUnitDescriptor', models.CharField(blank=True, max_length=100, null=True)),
                ('verbatim_SkeletalElementSide', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementPosition', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementComplete', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementClass', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_Locality', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_Country', models.CharField(blank=True, max_length=20, null=True)),
                ('verbatim_provenience', models.TextField(blank=True, null=True)),
                ('context', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='origins.Context')),
            ],
        ),
        migrations.CreateModel(
            name='FossilIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', wagtail.core.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='FossilPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', wagtail.core.fields.RichTextField()),
                ('body', wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())])),
                ('date', models.DateField(verbose_name='Post date')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('is_public', models.BooleanField(default=False)),
                ('feed_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('fossil', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='origins.Fossil')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
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
                'verbose_name': 'Identification Qualifier',
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created')),
                ('date_last_modified', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified')),
                ('problem', models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?')),
                ('problem_comment', models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True)),
                ('remarks', ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks')),
                ('last_import', models.BooleanField(default=False)),
                ('georeference_remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('name', models.CharField(blank=True, max_length=40, null=True)),
                ('alternate_names', models.TextField(blank=True, null=True)),
                ('min_ma', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('max_ma', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('formation', models.CharField(blank=True, max_length=50, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Country')),
                ('geom', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('origins', models.BooleanField(default=False)),
                ('source', models.CharField(blank=True, max_length=20, null=True)),
                ('verbatim_collection_no', models.IntegerField(blank=True, null=True)),
                ('verbatim_record_type', models.CharField(blank=True, max_length=20, null=True)),
                ('verbatim_formation', models.CharField(blank=True, max_length=50, null=True)),
                ('verbatim_lng', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('verbatim_lat', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('verbatim_collection_name', models.CharField(blank=True, max_length=200, null=True)),
                ('verbatim_collection_subset', models.CharField(blank=True, max_length=20, null=True)),
                ('verbatim_collection_aka', models.CharField(blank=True, max_length=200, null=True)),
                ('verbatim_n_occs', models.IntegerField(blank=True, null=True)),
                ('verbatim_early_interval', models.CharField(blank=True, max_length=50, null=True)),
                ('verbatim_late_interval', models.CharField(blank=True, max_length=50, null=True)),
                ('verbatim_max_ma', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('verbatim_min_ma', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('verbatim_reference_no', models.IntegerField(blank=True, null=True)),
                ('fossil_count', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SiteIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', wagtail.core.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='SitePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', wagtail.core.fields.RichTextField()),
                ('body', wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())])),
                ('date', models.DateField(verbose_name='Post date')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('is_public', models.BooleanField(default=False)),
                ('feed_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='origins.Site')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
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
                'verbose_name': 'Taxon Rank',
            },
        ),
        migrations.CreateModel(
            name='WorldBorder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('area', models.IntegerField()),
                ('pop2005', models.IntegerField(verbose_name='Population 2005')),
                ('fips', models.CharField(max_length=2, verbose_name='FIPS Code')),
                ('iso2', models.CharField(max_length=2, verbose_name='2 Digit ISO')),
                ('iso3', models.CharField(max_length=3, verbose_name='3 Digit ISO')),
                ('un', models.IntegerField(verbose_name='United Nations Code')),
                ('region', models.IntegerField(verbose_name='Region Code')),
                ('subregion', models.IntegerField(verbose_name='Sub-Region Code')),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
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
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='origins.Taxon')),
                ('rank', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='origins.TaxonRank')),
            ],
            options={
                'verbose_name': 'Taxon',
                'verbose_name_plural': 'Taxa',
                'ordering': ['rank__ordinal', 'name'],
            },
        ),
        migrations.CreateModel(
            name='SitePageTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_items', to='origins.SitePage')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origins_sitepagetag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SitePageRelatedLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document')),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_links', to='origins.SitePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SitePageCarouselItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
                ('embed_url', models.URLField(blank=True, verbose_name='Embed URL')),
                ('caption', wagtail.core.fields.RichTextField(blank=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('link_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document')),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='carousel_items', to='origins.SitePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='sitepage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='origins.SitePageTag', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.CreateModel(
            name='SiteIndexPageRelatedLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document')),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_links', to='origins.SiteIndexPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_no', models.IntegerField(blank=True, null=True)),
                ('record_type', models.CharField(blank=True, max_length=5, null=True)),
                ('ref_type', models.CharField(blank=True, max_length=201, null=True)),
                ('author1init', models.CharField(blank=True, max_length=202, null=True)),
                ('author1last', models.CharField(blank=True, max_length=203, null=True)),
                ('author2init', models.CharField(blank=True, max_length=204, null=True)),
                ('author2last', models.CharField(blank=True, max_length=205, null=True)),
                ('otherauthors', models.TextField(blank=True, null=True)),
                ('pubyr', models.CharField(blank=True, max_length=207, null=True)),
                ('reftitle', models.TextField(blank=True, null=True)),
                ('pubtitle', models.TextField(blank=True, null=True)),
                ('editors', models.TextField(blank=True, null=True)),
                ('pubvol', models.CharField(blank=True, max_length=210, null=True)),
                ('pubno', models.CharField(blank=True, max_length=211, null=True)),
                ('firstpage', models.CharField(blank=True, max_length=212, null=True)),
                ('lastpage', models.CharField(blank=True, max_length=213, null=True)),
                ('publication_type', models.CharField(blank=True, max_length=200, null=True)),
                ('language', models.CharField(blank=True, max_length=214, null=True)),
                ('doi', models.CharField(blank=True, max_length=215, null=True)),
                ('source', models.CharField(blank=True, max_length=216, null=True)),
                ('reference_pdf', models.FileField(blank=True, max_length=255, null=True, upload_to='uploads/files/origins')),
                ('fossil', models.ManyToManyField(to='origins.Fossil')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/images/origins', verbose_name='Image')),
                ('description', models.TextField(blank=True, null=True)),
                ('default_image', models.BooleanField(default=False)),
                ('fossil', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='origins.Fossil')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FossilPageTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='fossil_tagged_items', to='origins.FossilPage')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origins_fossilpagetag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FossilPageRelatedLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document')),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='fossil_related_links', to='origins.FossilPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FossilPageCarouselItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
                ('embed_url', models.URLField(blank=True, verbose_name='Embed URL')),
                ('caption', wagtail.core.fields.RichTextField(blank=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('link_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document')),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='fossil_carousel_items', to='origins.FossilPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='fossilpage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='origins.FossilPageTag', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.CreateModel(
            name='FossilIndexPageRelatedLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document')),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='fossil_related_links', to='origins.FossilIndexPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FossilElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(blank=True, max_length=100, null=True)),
                ('verbatim_PlaceName', models.CharField(blank=True, max_length=100, null=True)),
                ('verbatim_HomininElement', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_HomininElementNotes', models.TextField(blank=True, null=True)),
                ('verbatim_SkeletalElement', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementSubUnit', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementSubUnitDescriptor', models.CharField(blank=True, max_length=100, null=True)),
                ('verbatim_SkeletalElementSide', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementPosition', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementComplete', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_SkeletalElementClass', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_Locality', models.CharField(blank=True, max_length=40, null=True)),
                ('verbatim_Country', models.CharField(blank=True, max_length=20, null=True)),
                ('hominin_element', models.CharField(blank=True, max_length=40, null=True)),
                ('hominin_element_notes', models.TextField(blank=True, null=True)),
                ('skeletal_element', models.CharField(blank=True, max_length=40, null=True)),
                ('skeletal_element_subunit', models.CharField(blank=True, max_length=40, null=True)),
                ('skeletal_element_subunit_descriptor', models.CharField(blank=True, max_length=100, null=True)),
                ('skeletal_element_side', models.CharField(blank=True, max_length=40, null=True)),
                ('skeletal_element_position', models.CharField(blank=True, max_length=40, null=True)),
                ('skeletal_element_complete', models.CharField(blank=True, max_length=40, null=True)),
                ('skeletal_element_class', models.CharField(blank=True, max_length=40, null=True)),
                ('continent', models.CharField(blank=True, max_length=20, null=True)),
                ('side', models.CharField(blank=True, max_length=100, null=True)),
                ('fossil', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fossil_element', to='origins.Fossil')),
            ],
        ),
        migrations.AddField(
            model_name='fossil',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='origins.Site'),
        ),
        migrations.AddField(
            model_name='context',
            name='reference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='origins.Reference'),
        ),
        migrations.AddField(
            model_name='context',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='origins.Site'),
        ),
        migrations.CreateModel(
            name='ActiveSite',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('origins.site',),
        ),
    ]
