from django.shortcuts import render

import os

from django.conf import settings
from django.views import generic
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, loader, response
from django.contrib import messages
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.files.base import ContentFile
from .models import Occurrence, Biology, Archaeology, Geology, Person, Taxon, IdentificationQualifier, StratigraphicUnit
from .forms import UploadKMLForm, DownloadKMLForm, ChangeXYForm, Occurrence2Biology
from .utilities import match_taxon, match_element


from fastkml import kml
from fastkml import Placemark, Folder, Document
from lxml import etree
from datetime import datetime
from dateutil.parser import parse
# import utm
from zipfile import ZipFile
# from shapely.geometry import Point


class DownloadKMLView(generic.FormView):
    template_name = 'projects/download_kml.html'
    form_class = DownloadKMLForm
    context_object_name = 'download'
    success_url = '/projects/lgrp/confirmation/'

    def form_valid(self, form):
        k = kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        d = kml.Document(ns, 'docid', 'MLP Observations', 'KML Document')
        f = kml.Folder(ns, 'fid', 'MLP Observations Root Folder',
                       'Contains place marks for specimens and observations.')
        k.append(d)
        d.append(f)
        occurrences = Occurrence.objects.all()
        for o in occurrences:
            if o.geom:
                p = kml.Placemark(ns, 'id', 'name', 'description')
                # coord = utm.to_latlon(o.geom.coords[0], o.geom.coords[1], 37, 'P')
                pnt = Point(o.geom.coords[0], o.geom.coords[1])
                p.name = o.__str__()
                d = "<![CDATA[<table>"
                openrow = "<tr><td>"
                middlerow = "</td><td style='font-weight:bold'>"
                closerow = "</td></tr>"

                d += openrow
                d += ''.join(("Basis of Record", middlerow))
                d += ''.join(filter(None, (o.basis_of_record, closerow, openrow)))
                d += ''.join(("Time", middlerow))
                d += ''.join(filter(None, (str(o.date_recorded), closerow, openrow)))
                d += ''.join(("Item Type", middlerow))
                d += ''.join(filter(None, (o.item_type, closerow, openrow)))
                d += ''.join(("Collector", middlerow))
                d += ''.join(filter(None, (o.collector, closerow, openrow)))
                d += ''.join(("Collection Method", middlerow))
                d += ''.join(filter(None, (o.collecting_method, closerow, openrow)))
                d += ''.join(("Count", middlerow))
                d += ''.join(filter(None, (str(o.individual_count), closerow, openrow)))
                d += ''.join(("Bar Code", middlerow))
                d += ''.join(filter(None, (str(o.barcode), closerow, openrow)))
                d += ''.join(("Scientific Name", middlerow))
                d += ''.join(filter(None, (o.item_scientific_name, closerow, openrow)))
                d += ''.join(("Description", middlerow))
                d += ''.join(filter(None, (o.item_description, closerow, openrow)))
                d += ''.join(("Remarks", middlerow))
                d += ''.join(filter(None, (o.remarks, closerow, openrow)))
                d += ''.join(("In Situ", middlerow))
                d += ''.join(filter(None, (str(o.in_situ), closerow)))
                d += "</table>"
                p.description = d
                p.geometry = pnt
                f.append(p)
        r = k.to_string(prettyprint=True)
        response = HttpResponse(r, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="lgrp.kml"'
        return response


class ImportKMZ(generic.FormView):
    template_name = 'admin/lgrp/occurrence/import_kmz.html'
    form_class = UploadKMLForm
    context_object_name = 'upload'
    success_url = '../?last_import__exact=1'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # TODO parse the kml file more smartly to locate the first placemark and work from there.
        kml_file_upload = self.request.FILES['kmlfileUpload']  # get a handle on the file

        kml_file_upload_name = self.request.FILES['kmlfileUpload'].name  # get the file name
        # kml_file_name = kml_file_upload_name[:kml_file_upload_name.rfind('.')]  # get the file name no extension
        kml_file_extension = kml_file_upload_name[kml_file_upload_name.rfind('.')+1:]  # get the file extension

        kml_file_path = os.path.join(settings.MEDIA_ROOT)

        # Define a routine for importing Placemarks from a list of placemark elements
        def import_placemarks(kml_placemark_list):
            """
            A procedure that reads a KML placemark list and saves the data into the django database
            :param kml_placemark_list:
            :return:
            """
            occurrence_count, archaeology_count, biology_count, geology_count = [0,0,0,0]
            Occurrence.objects.all().update(last_import=False)  # Toggle off all last imports
            for o in kml_placemark_list:

                # Check to make sure that the object is a Placemark, filter out folder objects
                if type(o) is Placemark:
                    # Step 1 - parse the xml and copy placemark attributes to a dictionary
                    table = etree.fromstring(o.description)  # get the table element with all the data from the xml.
                    attributes = table.xpath("//text()|//img")  # get all text values and image tags from xml string
                    # TODO test attributes is even length
                    # Create a diction ary from the attribute list. The list has key value pairs as alternating
                    # elements in the list, the line below takes the first and every other elements and adds them
                    # as keys, then the second and every other element and adds them as values.
                    # e.g.
                    # attributes[0::2] = ["Basis of Record", "Time", "Item Type" ...]
                    # attributes[1::2] = ["Collection", "May 27, 2017, 10:12 AM", "Faunal" ...]
                    # zip creates a list of tuples  = [("Basis of Record", "Collection), ...]
                    # which is converted to a dictionary.
                    attributes_dict = dict(zip(attributes[0::2], attributes[1::2]))

                    # Step 2 - Create a new Occurrence object (or subtype)
                    lgrp_occ = None
                    # Determine the appropriate subtype and initialize
                    item_type = attributes_dict.get("Item Type")
                    occurrence_count += 1
                    if item_type in ("Artifact", "Artifactual", "Archeology", "Archaeological"):
                        lgrp_occ = Archaeology()
                        archaeology_count += 1
                    elif item_type in ("Faunal", "Fauna", "Floral", "Flora"):
                        lgrp_occ = Biology()
                        biology_count +=1
                    elif item_type in ("Geological", "Geology"):
                        lgrp_occ = Geology()
                        geology_count += 1

                    # Step 3 - Copy attributes from dictionary to Occurrence object, validate as we go.
                    # Improve by checking each field to see if it has a choice list. If so validate against choice
                    # list.

                    # Verbatim Data - save a verbatim copy of the original kml placemark attributes.
                    lgrp_occ.verbatim_kml_data = attributes

                    # Validate Basis of Record
                    if attributes_dict.get("Basis Of Record") in ("Fossil", "FossilSpecimen", "Collection"):
                        lgrp_occ.basis_of_record = "Collection"
                    elif attributes_dict.get("Basis Of Record") in ("Observation", "HumanObservation"):
                        lgrp_occ.basis_of_record = "Observation"

                    # Validate Item Type
                    item_type = attributes_dict.get("Item Type")
                    if item_type in ("Artifact", "Artifactual", "Archeology", "Archaeological"):
                        lgrp_occ.item_type = "Artifactual"
                    elif item_type in ("Faunal", "Fauna"):
                        lgrp_occ.item_type = "Faunal"
                    elif item_type in ("Floral", "Flora"):
                        lgrp_occ.item_type = "Floral"
                    elif item_type in ("Geological", "Geology"):
                        lgrp_occ.item_type = "Geological"

                    # Date Recorded
                    try:
                        # parse the time
                        lgrp_occ.date_recorded = parse(attributes_dict.get("Time"))
                        # set the year collected form field number
                        lgrp_occ.year_collected = lgrp_occ.date_recorded.year
                    except ValueError:
                        # If there's a problem getting the fieldnumber, use the current date time and set the
                        # problem flag to True.
                        lgrp_occ.date_recorded = datetime.now()
                        lgrp_occ.problem = True
                        try:
                            error_string = "Upload error, missing field number, using current date and time instead."
                            lgrp_occ.problem_comment = lgrp_occ.problem_comment + " " + error_string
                        except TypeError:
                            lgrp_occ.problem_comment = error_string

                    # Process point, comes in as well known text string
                    # Assuming point is in GCS WGS84 datum = SRID 4326
                    pnt = GEOSGeometry("POINT (" + str(o.geometry.x) + " " + str(o.geometry.y) + ")", 4326)  # WKT
                    lgrp_occ.geom = pnt

                    scientific_name_string = attributes_dict.get("Scientific Name")
                    lgrp_occ.item_scientific_name = scientific_name_string
                    if lgrp_occ.item_scientific_name:
                        match, match_count, match_list = match_taxon(lgrp_occ)
                        if match and match_count == 1:
                            lgrp_occ.taxon = match_list[0]

                    lgrp_occ.item_description = attributes_dict.get("Description")
                    if lgrp_occ.item_description:
                        match, match_count, match_list = match_element(lgrp_occ)
                        if match and match_count ==1:
                            lgrp_occ.element = lgrp_occ.item_description.lower()

                    #######################
                    # NON-REQUIRED FIELDS #
                    #######################
                    lgrp_occ.barcode = attributes_dict.get("Barcode")
                    lgrp_occ.item_number = lgrp_occ.barcode
                    lgrp_occ.collection_remarks = attributes_dict.get("Collecting Remarks")
                    lgrp_occ.geology_remarks = attributes_dict.get("Geology Remarks")

                    lgrp_occ.collecting_method = attributes_dict.get("Collection Method")
                    finder_string = attributes_dict.get("Finder")
                    lgrp_occ.finder = finder_string
                    # import person object, validated against look up data in Person table
                    lgrp_occ.finder_person, created = Person.objects.get_or_create(name=finder_string)

                    collector_string = attributes_dict.get("Collector")
                    lgrp_occ.collector = collector_string
                    # import person object, validated against look up data in Person table
                    lgrp_occ.collector_person, created = Person.objects.get_or_create(name=collector_string)

                    lgrp_occ.individual_count = attributes_dict.get("Count")

                    if attributes_dict.get("In Situ") in ('No', "NO", 'no'):
                        lgrp_occ.in_situ = False
                    elif attributes_dict.get("In Situ") in ('Yes', "YES", 'yes'):
                        lgrp_occ.in_situ = True

                    if attributes_dict.get("Ranked Unit") in ('No', "NO", 'no'):
                        lgrp_occ.ranked = False
                    elif attributes_dict.get("Ranked Unit") in ('Yes', "YES", 'yes'):
                        lgrp_occ.ranked = True

                    unit_found_string = attributes_dict.get("Unit Found")
                    unit_likely_string = attributes_dict.get("Unit Likely")
                    lgrp_occ.analytical_unit_found = unit_found_string
                    lgrp_occ.analytical_unit_likely = unit_likely_string
                    lgrp_occ.analytical_unit_1 = attributes_dict.get("Unit 1")
                    lgrp_occ.analytical_unit_2 = attributes_dict.get("Unit 2")
                    lgrp_occ.analytical_unit_3 = attributes_dict.get("Unit 3")

                    # import statigraphy object, validate against look up data in Stratigraphy table
                    lgrp_occ.unit_found, created = StratigraphicUnit.objects.get_or_create(name=unit_found_string)
                    lgrp_occ.unit_likly, created = StratigraphicUnit.objects.get_or_create(name=unit_likely_string)

                    # Save Occurrence before saving media. Need id to rename media files
                    lgrp_occ.last_import = True
                    lgrp_occ.save()

                    # Save image
                    if kml_file_extension.lower() == "kmz":
                        # grab image names from XML
                        image_names = table.xpath("//img/@src")
                        # grab the name of the first image
                        # Future: add functionality to import multiple images
                        if image_names and len(image_names) == 1:  # This will break if image_names is None
                            image_name = image_names[0]
                            # Check that the image name is in the kmz file list
                            kmz_file.filenames = [f.orig_filename for f in kmz_file.filelist]
                            if image_name in kmz_file.filenames:
                                # etch the kmz image file object, this is a ZipInfo object not a File object
                                image_file_obj = next(f for f in kmz_file.filelist if f.orig_filename == image_name)
                                # fetch the upload directory from the model definition
                                upload_dir = Biology._meta.get_field('image').upload_to
                                # update image name to include upload path and occurrence id
                                # e.g. /uploads/images/lgrp/14775_188.jpg
                                new_image_name = os.path.join(upload_dir, str(lgrp_occ.id)+'_'+image_name)
                                # Save the image
                                lgrp_occ.image.save(new_image_name, ContentFile(kmz_file.read(image_file_obj)))

                elif type(o) is not Placemark:
                    raise IOError("KML File is badly formatted")
            if occurrence_count == 1:
                message_string = '1 occurrence'
            if occurrence_count > 1:
                message_string = '{} occurrences'.format(occurrence_count)
            messages.add_message(self.request, messages.INFO,
                                 'Successfully imported {} occurrences'.format(message_string))

        kml_file = kml.KML()
        if kml_file_extension == "kmz":
            kmz_file = ZipFile(kml_file_upload, 'r')
            kml_document = kmz_file.open('doc.kml', 'r').read()
        else:
            # read() loads entire file as one string
            kml_document = open(kml_file_path + "/" + kml_file_upload_name, 'r').read()

        kml_file.from_string(kml_document)  # pass contents of kml string to kml document instance for parsing

        # get the top level features object (this is essentially the layers list)
        level1_elements = list(kml_file.features())

        # Check that the kml file is well-formed with a single document element.
        if len(level1_elements) == 1 and type(level1_elements[0]) == Document:
            document = level1_elements[0]

            #  If well-formed document, check if the file has folders, which correspond to layers
            level2_elements = list(document.features())
            if len(level2_elements) == 1 and type(level2_elements[0]) == Folder:
                folder = level2_elements[0]

                #  If a single folder is present import placemarks from that folder
                #  Get features from the folder
                level3_elements = list(folder.features())
                #  Check that the features are Placemarks. If they are, import them
                if len(level3_elements) >= 1 and type(level3_elements[0]) == Placemark:
                    placemark_list = level3_elements
                    import_placemarks(placemark_list)

            elif len(level2_elements) >= 1 and type(level2_elements[0]) == Placemark:
                placemark_list = level2_elements
                import_placemarks(placemark_list)

        return super(ImportKMZ, self).form_valid(form)


class ChangeCoordinates(generic.FormView):
    template_name = 'admin/lgrp/occurrence/changeXY.html'
    form_class= ChangeXYForm
    current_id = None

    def get_success_url(self):
        if self.current_id:
            surl = '../{}/change'.format(self.current_id)
        else:
            surl = '../'
        return surl

    def get(self, request, *args, **kwargs):
        if 'ids' in request.GET:
            selected = request.GET['ids'].split(',')
            if len(selected) > 1:
                messages.error(request, "You can't change the coordinates of multiple points at once.")
                if request.META['HTTP_REFERER']:
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    return redirect('../')
            else:
              return super(ChangeCoordinates, self).get(self, request, args=args, kwargs=kwargs)

    def get_initial(self):
        initial = {}
        if self.request.GET:
            selected = self.request.GET['ids'].split(',')
            selected_object = Occurrence.objects.get(pk=int(selected[0]))
            initial['DB_id'] = selected_object.id
            initial['barcode'] = selected_object.barcode
            initial['old_easting'] = selected_object.easting
            initial['old_northing'] = selected_object.northing
            initial['item_scientific_name'] = selected_object.item_scientific_name
            initial['item_description'] = selected_object.item_description
        return initial

    def form_valid(self, form):
        if form.is_valid():
            obs = Occurrence.objects.get(pk=form.cleaned_data['DB_id'])
            self.current_id = obs.id
            if form.cleaned_data['new_easting'] and form.cleaned_data['new_northing']:
                utm_pnt = Point(float(form.cleaned_data['new_easting']), float(form.cleaned_data['new_northing']), srid=32637)
                gcs_pnt = utm_pnt.transform(4326, clone=True)
            obs.geom = gcs_pnt
            obs.save()
            messages.add_message(self.request, messages.INFO,
                                 'Successfully Updated Coordinates For {}.'.format(obs.catalog_number()))
        return super(ChangeCoordinates, self).form_valid(form)


def change_coordinates_view(request):
    if request.method == "POST":
        form = ChangeXYForm(request.POST)
        if form.is_valid():
            obs = Occurrence.objects.get(pk=request.POST["DB_id"])
            if request.POST['new_easting'] and request.POST['new_northing']:
                utm_pnt = Point(request.POST['new_easting'], request.POST['new_northing'], srid=32637)
                gcs_pnt = utm_pnt.transform(4326, clone=True)
            obs.geom = gcs_pnt
            obs.save()
            messages.add_message(request, messages.INFO,
                                 'Successfully Updated Coordinates For %s.' % obs.catalog_number())
            return redirect("../", RequestContext(request))
    else:
        selected = list(request.GET.get("ids", "").split(","))
        if len(selected) > 1:
            messages.error(request, "You can't change the coordinates of multiple points at once.")
            return redirect("../")
        selected_object = Occurrence.objects.get(pk=int(selected[0]))
        initial_data = {"DB_id": selected_object.id,
                        "barcode": selected_object.barcode,
                        "old_easting": selected_object.easting,
                        "old_northing": selected_object.northing,
                        "item_scientific_name": selected_object.item_scientific_name,
                        "item_description": selected_object.item_description
                        }
        the_form = ChangeXYForm(initial=initial_data)
        return render_to_response('admin/lgrp/occurrence/changeXY.html', {"theForm": the_form}, RequestContext(request))


def occurrence2biology_view(request):
    if request.method == "POST":
        form = Occurrence2Biology(request.POST)
        if form.is_valid():
            occurrence_object = Occurrence.objects.get(barcode__exact=request.POST["barcode"])
            if occurrence_object.item_type in ('Faunal', 'Floral'):
                taxon = Taxon.objects.get(pk=request.POST["taxon"])
                id_qual = IdentificationQualifier.objects.get(pk=request.POST["identification_qualifier"])
                new_biology = Biology(barcode=occurrence_object.barcode,
                                      item_type=occurrence_object.item_type,
                                      basis_of_record=occurrence_object.basis_of_record,
                                      collecting_method=occurrence_object.collecting_method,
                                      date_recorded=occurrence_object.date_recorded,
                                      taxon=taxon,
                                      identification_qualifier=id_qual,
                                      geom=occurrence_object.geom
                                      )
                for key in occurrence_object.__dict__.keys():
                    new_biology.__dict__[key] = occurrence_object.__dict__[key]

                occurrence_object.delete()
                new_biology.save()
                messages.add_message(request, messages.INFO,
                                     'Successfully converted occurrence to biology.')
            else:
                pass
                messages.error(request, "Can only convert items of type Faunal or Floral")
            return redirect("/admin/lgrp/occurrence")
    else:
        selected = list(request.GET.get("ids", "").split(","))
        if len(selected) > 1:
            messages.add_message(request, messages.INFO, "Do you wish to update all the following occurrences?")
            return redirect("/admin/lgrp/occurrence")
        selected_object = Occurrence.objects.get(pk=int(selected[0]))
        initial_data = {
                        "barcode": selected_object.barcode,
                        "catalog_number": selected_object.catalog_number,
                        "basis_of_record": selected_object.basis_of_record,
                        "item_type": selected_object.item_type,
                        "collector": selected_object.collector,
                        "collecting_method": selected_object.collecting_method,
                        "date_recorded": selected_object.date_recorded,
                        "year_collected": selected_object.year_collected,
                        "item_scientific_name": selected_object.item_scientific_name,
                        "item_description": selected_object.item_description
                        }
        the_form = Occurrence2Biology(initial=initial_data)
        return render_to_response('projects/occurrence2biology.html', {"theForm": the_form, "initial_data": initial_data}, RequestContext(request))



