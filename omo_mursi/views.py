from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views import generic
import os
from .models import Occurrence
import shapefile
from .forms import UploadForm, UploadKMLForm, DownloadKMLForm, ChangeXYForm
from fastkml import kml
from pygeoif import geometry
from fastkml import Placemark, Folder, Document
from lxml import etree
from datetime import datetime
from django.contrib.gis.geos import GEOSGeometry
from zipfile import ZipFile
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from io import BytesIO
from django.core.files import File


class DownloadKMLView(generic.FormView):
    template_name = 'projects/download_kml.html'
    form_class = DownloadKMLForm
    context_object_name = 'download'
    success_url = '/projects/omo_mursi/confirmation/'

    def form_valid(self, form):
        k = kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        d = kml.Document(ns, 'docid', 'MLP Observations', 'KML Document')
        f = kml.Folder(ns, 'fid', 'MLP Observations Root Folder', 'Contains place marks for specimens and observations.')
        k.append(d)
        d.append(f)
        omo_occurrences = Occurrence.objects.all()
        for o in omo_occurrences:
            if o.geom:
                p = kml.Placemark(ns, 'id', 'name', 'description')
                # coord = utm.to_latlon(o.geom.coords[0], o.geom.coords[1], 37, 'P')
                pnt = geometry.Point(o.geom.coords[0], o.geom.coords[1])
                p.name = o.__str__()
                d = "<![CDATA[<table>"
                open_row = "<tr><td>"
                middle_row = "</td><td style='font-weight:bold'>"
                close_row = "</td></tr>"

                d += open_row
                d += ''.join(("Basis of Record", middle_row))
                d += ''.join([_f for _f in (o.basis_of_record, close_row, open_row) if _f])
                d += ''.join(("Time", middle_row))
                d += ''.join([_f for _f in (str(o.field_number), close_row, open_row) if _f])
                d += ''.join(("Item Type", middle_row))
                d += ''.join([_f for _f in (o.item_type, close_row, open_row) if _f])
                d += ''.join(("Collector", middle_row))
                d += ''.join([_f for _f in (o.collector, close_row, open_row) if _f])
                d += ''.join(("Collection Method", middle_row))
                d += ''.join([_f for _f in (o.collecting_method, close_row, open_row) if _f])
                d += ''.join(("Count", middle_row))
                d += ''.join([_f for _f in (str(o.individual_count), close_row, open_row) if _f])
                d += ''.join(("Bar Code", middle_row))
                d += ''.join([_f for _f in (str(o.barcode), close_row, open_row) if _f])
                d += ''.join(("Scientific Name", middle_row))
                d += ''.join([_f for _f in (o.item_scientific_name, close_row, open_row) if _f])
                d += ''.join(("Description", middle_row))
                d += ''.join([_f for _f in (o.item_description, close_row, open_row) if _f])
                d += ''.join(("Remarks", middle_row))
                d += ''.join([_f for _f in (o.remarks, close_row, open_row) if _f])
                d += ''.join(("In Situ", middle_row))
                d += ''.join([_f for _f in (str(o.in_situ), close_row) if _f])
                d += "</table>"
                p.description = d
                p.geometry = pnt
                f.append(p)
        r = k.to_string(prettyprint=True)
        response = HttpResponse(r, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="omo_mursi.kml"'
        return response


class UploadKMLView(generic.FormView):
    template_name = 'projects/upload_kml.html'
    form_class = UploadKMLForm
    context_object_name = 'upload'
    # For some reason reverse cannot be used to define the success_url. For example the following line raises an error.
    # e.g. success_url = reverse("projects:omo_mursi:omo_mursi_upload_confirmation")
    success_url = '/projects/omo_mursi/confirmation/'  # but this does work.

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # TODO parse the kml file more smartly to locate the first placemark and work from there.
        # TODO ingest kmz and kml. See the zipfile python library
        kml_file_upload = self.request.FILES['kmlfileUpload']  # get a handle on the file
        kml_file_upload_name = self.request.FILES['kmlfileUpload'].name  # get the file name
        # KML_file_name = kml_file_upload_name[:kml_file_upload_name.rfind('.')]  # get the file name without extension
        kml_file_extension = kml_file_upload_name[kml_file_upload_name.rfind('.')+1:]  # get the file extension

        kml_file_path = os.path.join(settings.MEDIA_ROOT)

        # Define a routine for importing placemarks from a list of placemark elements
        def import_placemarks(placemark_list):
            feature_count = 0

            for o in placemark_list:  # iterate through all the placemarks in the KML/KMZ file and process each one

                # Check to make sure that the object is a Placemark, filter out folder objects
                if type(o) is Placemark:

                    # save the placemark attribute data located in the description element as an element tree
                    table = etree.fromstring(o.description)
                    attributes = table.xpath("//text()")
                    # TODO test attributes is even length
                    attributes_dict = dict(list(zip(attributes[0::2], attributes[1::2])))

                    # Create a new, empty occurrence instance
                    omo_mursi_occ = Occurrence()

                    ###################
                    # REQUIRED FIELDS #
                    ###################

                    # Validate Basis of Record
                    if attributes_dict.get("Basis Of Record") in ("Fossil", "FossilSpecimen", "Collection"):
                        omo_mursi_occ.basis_of_record = "FossilSpecimen"
                    elif attributes_dict.get("Basis Of Record") in ("Observation", "HumanObservation"):
                        omo_mursi_occ.basis_of_record = "HumanObservation"

                    # Validate Item Type
                    item_type = attributes_dict.get("Item Type")
                    if item_type in ("Artifact", "Artifactual", "Archeology", "Archaeological"):
                        omo_mursi_occ.item_type = "Artifactual"
                    elif item_type in ("Faunal", "Fauna"):
                        omo_mursi_occ.item_type = "Faunal"
                    elif item_type in ("Floral", "Flora"):
                        omo_mursi_occ.item_type = "Floral"
                    elif item_type in ("Geological", "Geology"):
                        omo_mursi_occ.item_type = "Geological"

                    # Field Number and Year Collected
                    try:
                        # parse field number
                        omo_mursi_occ.field_number = datetime.strptime(attributes_dict.get("Time"),
                                                                       "%b %d, %Y, %I:%M %p")
                        # set the year collected from field number
                        omo_mursi_occ.year_collected = omo_mursi_occ.field_number.year
                    except ValueError:
                        omo_mursi_occ.field_number = datetime.now()
                        omo_mursi_occ.problem = True
                        try:
                            error_string = "Upload error, missing field number, using current date and time instead."
                            omo_mursi_occ.problem_comment = omo_mursi_occ.problem_comment + " " +error_string
                        except TypeError:
                            omo_mursi_occ.problem_comment = error_string

                    # Process point, comes in as well known text string
                    # Assuming point is in GCS WGS84 datum = SRID 4326
                    pnt = GEOSGeometry("POINT (" + str(o.geometry.x) + " " + str(o.geometry.y) + ")", 4326)  # WKT
                    omo_mursi_occ.geom = pnt

                    #######################
                    # NON-REQUIRED FIELDS #
                    #######################
                    omo_mursi_occ.barcode = attributes_dict.get("Barcode")
                    omo_mursi_occ.item_number = omo_mursi_occ.barcode
                    omo_mursi_occ.catalog_number = "MUR-" + str(omo_mursi_occ.item_number)
                    omo_mursi_occ.remarks = attributes_dict.get("Remarks")
                    omo_mursi_occ.item_scientific_name = attributes_dict.get("Scientific Name")
                    omo_mursi_occ.item_description = attributes_dict.get("Description")

                    # Validate Collecting Method
                    collection_method = attributes_dict.get("Collection Method")
                    if collection_method in ("Surface Standard", "Standard"):
                        omo_mursi_occ.collecting_method = "Surface Standard"
                    elif collection_method in ("Surface Intensive", "Intensive"):
                        omo_mursi_occ.collecting_method = "Surface Intensive"
                    elif collection_method in ("Surface Complete", "Complete"):
                        omo_mursi_occ.collecting_method = "Surface Complete"
                    elif collection_method in ("Exploratory Survey", "Exploratory"):
                        omo_mursi_occ.collecting_method = "Exploratory Survey"
                    elif collection_method in ("Dry Screen 5mm", "Dry Screen 5 Mm", "Dry Screen 5 mm"):
                        omo_mursi_occ.collecting_method = "Dry Screen 5mm"
                    elif collection_method in ("Dry Screen 2mm", "Dry Screen 2 Mm", "Dry Screen 2 mm"):
                        omo_mursi_occ.collecting_method = "Dry Screen 2mm"
                    elif collection_method in ("Dry Screen 1mm", "Dry Screen 1 Mm", "Dry Screen 1 mm"):
                        omo_mursi_occ.collecting_method = "Dry Screen 1mm"

                    omo_mursi_occ.collecting_method = attributes_dict.get("Collection Method")
                    omo_mursi_occ.collector = attributes_dict.get("Collector")
                    omo_mursi_occ.individual_count = attributes_dict.get("Count")

                    # In Situ
                    if attributes_dict.get("In Situ") in ('No', "NO", 'no'):
                        omo_mursi_occ.in_situ = False
                    elif attributes_dict.get("In Situ") in ('Yes', "YES", 'yes'):
                        omo_mursi_occ.in_situ = True

                    ##############
                    # Save Image #
                    ##############
                    omo_mursi_occ.save()  # need to save record before adding image in order to obtain the DB ID

                    # Now look for images if this is a KMZ
                    if kml_file_extension.lower() == "kmz":
                        # grab image names from XML element tree
                        image_file_name_list = table.xpath("//img/@src")
                        # grab the name of the first image
                        try:
                            image_file_name = image_file_name_list[0]
                            # grab the file info from the zip list
                            for file_info in kmz_file.filelist:
                                if image_file_name == file_info.orig_filename:
                                    # grab the image file itself
                                    image = kmz_file.open(image_file_name)  # get a handle on the image in the kmz file
                                    image_stream = BytesIO(image.read()) # read the image without saving to disk
                                    save_file_name = str(omo_mursi_occ.id) + "_" + image_file_name  # rename
                                    omo_mursi_occ.image.save(save_file_name, File(image_stream))  # save the image
                                    break
                        except IndexError:
                            pass

                    feature_count += 1

                elif type(o) is not Placemark:
                    raise IOError("KML File is badly formatted")

        kml_file = kml.KML()
        if kml_file_extension == "kmz":
            kmz_file = ZipFile(kml_file_upload, 'r')
            try:
                kml_document = kmz_file.open('doc.kml', 'r').read()
            except KeyError:
                print("ERROR: Didn't find doc.kml in the zipped file.")
        else:
            kml_document = open(kml_file_path + "/" + kml_file_upload_name, 'r').read()

        kml_file.from_string(kml_document)  # pass contents of kml document for parsing

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

        return super(UploadKMLView, self).form_valid(form)


class Confirmation(generic.ListView):
    template_name = 'projects/confirmation.html'
    model = Occurrence


class UploadShapefileView(generic.FormView):
    template_name = 'projects/upload_shapefile.html'
    form_class = UploadForm
    context_object_name = 'upload'
    success_url = 'confirmation'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        shapefileProper = self.request.FILES['shapefileUpload']
        shapefileIndex = self.request.FILES['shapefileIndexUpload']
        shapefileData = self.request.FILES['shapefileDataUpload']
        shapefileProperName = self.request.FILES['shapefileUpload'].name
        shapefileIndexName = self.request.FILES['shapefileIndexUpload'].name
        shapefileDataName = self.request.FILES['shapefileDataUpload'].name
        shapefileProperSaved = default_storage.save(shapefileProperName, ContentFile(shapefileProper.read()))
        shapefileIndexSaved = default_storage.save(shapefileIndexName, ContentFile(shapefileIndex.read()))
        shapefileDataSaved = default_storage.save(shapefileDataName, ContentFile(shapefileData.read()))
        shapefilePath = os.path.join(settings.MEDIA_ROOT)
        shapefileName = shapefileProperName[:shapefileProperName.rfind('.')]
        sf = shapefile.Reader(shapefilePath + "\\" + shapefileName)
        # sf = shapefile.Reader("C:\\Users\\turban\\Documents\\Development\\PyCharm\\paleocore\\media\\air_photo_areas")

        shapes = sf.shapes()
        return super(UploadShapefileView, self).form_valid(form)


def change_coordinates_view(request):
    if request.method == "POST":
        form = ChangeXYForm(request.POST)
        if form.is_valid():
            obs = Occurrence.objects.get(pk=request.POST["DB_id"])

            #coordinates = utm.to_latlon(float(request.POST["new_easting"]),
            #                            float(request.POST["new_northing"]), 37, "N")
            #pnt = GEOSGeometry("POINT (" + str(coordinates[1]) + " " + str(coordinates[0]) + ")", 4326)  # WKT
            pnt = GEOSGeometry("POINT (" + request.POST["new_easting"] + " " + request.POST["new_northing"] + ")", 32637)
            obs.geom = pnt
            obs.save()
            messages.add_message(request, messages.INFO,
                                 'Successfully Updated Coordinates For %s.' % obs.catalog_number)
            return redirect("/admin/omo_mursi/occurrence")
    else:
        selected = list(request.GET.get("ids", "").split(","))
        if len(selected) > 1:
            messages.error(request, "You can't change the coordinates of multiple points at once.")
            return redirect("/admin/omo_mursi/occurrence")
        selected_object = Occurrence.objects.get(pk=int(selected[0]))
        initial_data = {"DB_id": selected_object.id,
                        "barcode": selected_object.barcode,
                        "old_easting": selected_object.easting,
                        "old_northing": selected_object.northing,
                        "item_scientific_name": selected_object.item_scientific_name,
                        "item_description": selected_object.item_description
                        }
        the_form = ChangeXYForm(initial=initial_data)
        return render_to_response('projects/changeXY.html', {"theForm": the_form}, RequestContext(request))
