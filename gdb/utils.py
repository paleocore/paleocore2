from gdb.models import *
from gdb.ontologies import *
sub_age_choices = clarkforkian_subages + wasatchian_subages + bridgerian_subages


def get_sub_age_list(loc):
    sal = [b.sub_age for b in Biology.objects.filter(locality=loc) if b.sub_age not in (None, '')]
    return list(set(sal))

def validate_sub_age_list(sub_age_list):
    result = []
    if not sub_age_list:
        result = [True, None]
    elif len(sub_age_list) == 1 and sub_age_list[0] in sub_age_choices:
        result = [True, sub_age_list[0]]
    elif len(sub_age_list) > 1:
        match_list = []
        for sa in sub_age_list:
            if sa in sub_age_choices:
                match_list.append(sa)
        if len(match_list) == 1:
            result = [True, match_list[0]]
        else:
            result = [False, match_list]
    else:
        result = [False, sub_age_list]
    return result


def update_locality_sub_ages():
    locs = Locality.objects.all()
    for l in locs:
        sal = get_sub_age_list(l)
        vlist = validate_sub_age_list(sal)
        if vlist[0]:
            l.sub_age = vlist[1]
            l.save()

