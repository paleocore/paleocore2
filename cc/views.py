from django.shortcuts import render
import os
import csv
from cc.models import Excavation_unit, Context, Lithic, Small_Find, Photo, Lithics_with_Photos
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
                s, created = Excavation_unit.objects.get_or_create(unit=row[0],defaults={'extent': g})
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
                s = Context(pk=row[0], cat_no=row[1], unit=row[2], id_no=row[3], level=row[4], code=row[5], excavator=row[6], exc_date=row[7], exc_time=row[8])
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


def fill_small_finds():
    with open(os.path.join(BASE_DIR, 'small_finds.csv'), 'rb') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            n += 1
            if n > 1:
                for n in range(1,len(row)):
                    if int(row[n]) == -1:
                        row[n] = None
                s = Small_Find(pk = row[0], coarse_stone_weight = row[1], coarse_fauna_weight = row[2], fine_stone_weight = row[3], fine_fauna_weight = row[4])
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
                    if row[n] == 'N/':
                        row[n] = None
                    if row[n] == ' N/':
                        row[n] = None
                    if row[n] == '/A':
                        row[n] = None
                    if row[n] == 'N':
                        row[n] = None
                    if row[n] == "-1":
                        row[n] = None

                s = Lithic(pk = row[0],
                            dataclass = row[3],
                            cortex = row[4],
                            technique = row[5],
                            alteration = row[6],
                            edge_damage = row[7],
                            fb_type = row[8],
                            fb_type_2 = row[9],
                            fb_type_3 = row[10],
                            platform_surface = row[11],
                            platform_exterior = row[12],
                            form = row[13],
                            scar_morphology = row[14],
                            retouched_edges = row[15],
                            retouch_intensity = row[16],
                            reprise = row[17],
                            length = row[18],
                            width = row[19],
                            maximum_width = row[20],
                            thickness = row[21],
                            platform_width = row[22],
                            platform_thickness = row[23],
                            raw_material = row[24],
                            exterior_surface = row[25],
                            exterior_type = row[26],
                            weight = row[27],
                            platform_technique = row[28],
                            platform_angle = row[29],
                            multiple = row[30],
                            epa = row[31],
                            core_shape = row[32],
                            core_blank = row[33],
                            core_surface_percentage = row[34],
                            proximal_removals = row[35],
                            prepared_platforms = row[36],
                            flake_direction = row[37],
                            scar_length = row[38],
                            scar_width = row[39])
                s.save()

def debugger(request):
    debug_message = os.path.join(BASE_DIR, 'context.csv')
    return render(request, 'cc/debugger.html',{'debug_message': debug_message})


def populate_database(request):
    fill_context()
    fill_small_finds()
    fill_lithics()
    fill_photos()
    fill_context()
    fill_xyz()
    fill_units()
    return HttpResponseRedirect('../admin/')

def home(request):
    return HttpResponseRedirect('../admin/')

