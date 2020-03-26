from django.shortcuts import render
import os
import csv
from fc_db.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos import LineString
from django.contrib.gis.geos import Point


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def fill_units():
    with open(os.path.join(BASE_DIR, 'units.csv'), 'rb') as f:
        reader = csv.reader(f)
        l = 0
        for row in reader:
            l += 1
            if l > 1:
                xyz = row[2].split(",")
                p = [None] * int(row[1])
                for n in range(1,int(row[1])+1):
                    p[n-1] = Point(float(xyz[(n-1)*3]),float(xyz[(n-1)*3+1]),float(xyz[((n-1)*3+2)]))
                if int(row[1]) == 1:
                    g = p[0]
                if int(row[1]) == 2:
                    g = LineString((p[0],p[1]))
                if int(row[1]) > 2:
                    if p[0]==p[int(row[1])-1]:
                        g = Polygon(p)
                    else:
                        g = LineString(p)
                s, created  = Excavation_unit.objects.get_or_create(unit=row[0],defaults={'extent': g})
                s.save()


def fill_xyz():
    with open(os.path.join(BASE_DIR, 'xyz.csv'), 'rb') as f:
        reader = csv.reader(f)
        l = 0
        for row in reader:
            l += 1
            if l > 1:
                s = Context.objects.get(pk = row[0])
                xyz = row[2].split(",")
                p = [None] * int(row[1])
                for n in range(1,int(row[1])+1):
                    p[n-1] = Point(float(xyz[(n-1)*3]),float(xyz[(n-1)*3+1]),float(xyz[((n-1)*3+2)]))
                if int(row[1]) == 1:
                    g = p[0]
                if int(row[1]) == 2:
                    g = LineString((p[0],p[1]))
                if int(row[1]) > 2:
                    p.append(p[0])
                    g = Polygon(p)
                s.points = g
                s.save()


def fill_context():
    with open(os.path.join(BASE_DIR, 'context.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                for n in range(1,len(row)):
                    if row[n] == 'NA':
                        row[n] = None
                    if row[n] == 'N/A':
                        row[n] = None
                    if row[n] == "":
                        row[n] = None
                s = Context(pk = row[10], collection = row[1], cat_no = row[0], unit = row[2], id_no = row[3], sector = row[4], analytical_level = row[5], level = row[6], code = row[7], exc_date = row[8], excavator = row[9])
                s.save()


def fill_photos():
    with open(os.path.join(BASE_DIR, 'photos.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                s = Photo(pk = row[0], image01 = row[1])
                s.save()


def fill_refits():
    with open(os.path.join(BASE_DIR, 'refits.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                for n in range(1,len(row)):
                    if int(row[n]) == -1:
                        row[n] = None
                s = Refits(unit = row[0], id_no = row[1], counter = row[2])
                s.save()


def fill_small_finds():
    with open(os.path.join(BASE_DIR, 'small_finds.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                if int(row[2]) == -1:
                    row[2] = None
                if int(row[3]) == -1:
                    row[3] = None
                s = Small_Find(pk = row[0], screen_size=row[1], platform_count=row[2], platform_weight=row[3])
                s.save()


def fill_small_find_weights():
    with open(os.path.join(BASE_DIR, 'tamis_weights.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                s = Small_Find_Weights(context_id = row[0], weight=row[1])
                s.save()


def fill_galet_weights():
    with open(os.path.join(BASE_DIR, 'galets.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                s = Galet_Weights(pk = row[0], weight=row[1])
                s.save()


def fill_grain():
    with open(os.path.join(BASE_DIR, 'grain.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                s = Granulometry(context_id = row[0], weight=row[1])
                s.save()


def fill_fauna():
    with open(os.path.join(BASE_DIR, 'fauna.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                for n in range(1,len(row)):
                    if row[n] == 'NA':
                        row[n] = None
                    if row[n] == 'N/A':
                        row[n] = None
                    if row[n] == "":
                        row[n] = None
                s = Fauna(pk = row[0],
                                tentative_ID = row[1],
                                genus = row[2],
                                side = row[3],
                                part = row[4],
                                portion = row[5],
                                segment = row[6],
                                bone_type = row[7])
                s.save()


def fill_lithics():
    with open(os.path.join(BASE_DIR, 'lithics.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                for n in range(1,len(row)):
                    if row[n] == 'NA':
                        row[n] = None
                    if row[n] == 'N/A':
                        row[n] = None
                    if row[n] == "":
                        row[n] = None
                    if row[n] == '-9999':
                        row[n] = None
                s = Lithic(pk = row[0],
                            dataclass = row[3],
                            raw_material = row[4],
                            support = row[5],
                            technique = row[6],
                            form = row[7],
                            fb_type = row[8],
                            fb_type_2 = row[9],
                            core_type = row[10],
                            biface_type = row[11],
                            retouched_edges = row[12],
                            retouch_intensity = row[13],
                            tf_character = row[14],
                            tf_surface = row[15],
                            tf_location = row[16],
                            platform_surface = row[17],
                            platform_exterior = row[18],
                            core_faces = row[19],
                            platforms = row[20],
                            platform_technique_1 = row[21],
                            platform_technique_2 = row[22],
                            scar_morphology = row[23],
                            cortex = row[25],
                            discard = row[26],
                            edge_damage = row[27],
                            alteration = row[28],
                            proximal_removals = row[29],
                            scar_length = row[30],
                            length = row[31],
                            width = row[37],
                            thickness = row[39],
                            platform_width = row[45],
                            platform_thickness = row[46],
                            small_pw = row[47],
                            bulb = row[48],
                            epa = row[49],
                            weight = row[50])
                s.save()


def debugger(request):
    debug_message = os.path.join(BASE_DIR, 'context.csv')
    return render(request, 'cc/debugger.html',{'debug_message': debug_message})


def populate_context(request):
    fill_context()
    return HttpResponseRedirect('../admin/')


def populate_lithics(request):
    fill_lithics()
    return HttpResponseRedirect('../admin/')


def populate_small_finds(request):
    fill_small_finds()
    return HttpResponseRedirect('../admin/')


def populate_photos(request):
    fill_photos()
    return HttpResponseRedirect('../admin/')


def populate_xyz(request):
    fill_xyz()
    return HttpResponseRedirect('../admin/')


def populate_units(request):
    fill_units()
    return HttpResponseRedirect('../admin/')


def populate_database(request):
    fill_context()
    fill_small_finds()
    fill_small_find_weights()
    fill_lithics()
    fill_photos()
    fill_fauna()
    fill_galet_weights()
    fill_grain()
    fill_refits()
    fill_context()
    fill_xyz()
    fill_units()
    return HttpResponseRedirect('../admin/')

def home(request):
    return HttpResponseRedirect('../admin/')

