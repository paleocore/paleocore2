from django.shortcuts import render_to_response
from django.template import RequestContext
from standard.models import Term, Project, CompareView, TermView, ProjectView, TermCategory
from django.db.models import Q
from standard.forms import TermViewForm  # RelateProjectsForm, RelateTermsForm
from django.forms.models import modelform_factory
import json
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django import forms
from django.contrib.auth import authenticate,login
from django.shortcuts import get_object_or_404
from django.views import generic
from django.urls import reverse
from django.contrib.auth.decorators import permission_required


class PaleocoreTermsIndexView(generic.ListView):
    template_name = 'standard/terms.html'
    context_object_name = 'terms'

    def get_queryset(self):
        """Return a list of terms for Paleocore"""
        # get just the non-class paleocore terms, which get added to the context as terms
        paleocore_terms = Term.objects.filter(projects__name='pc').order_by('category', 'name')
        paleocore_terms = paleocore_terms.exclude(is_class=True)
        return paleocore_terms

    def get_context_data(self, **kwargs):
        # supplement the context by adding a list of class terms

        # get the original context
        context = super(PaleocoreTermsIndexView, self).get_context_data(**kwargs)

        # get a queryset of just paleocore classes
        paleocore_classes = Term.objects.filter(projects__name='pc').filter(is_class=True).order_by('term_ordering')

        # add them to the context, which now contains elements for terms and classes
        context['classes'] = paleocore_classes
        return context


class TermsIndexView(generic.ListView):
    template_name = 'standard/terms.html'
    context_object_name = 'terms'

    def get_queryset(self):
        # build a query set of terms for a given project. The project_name is passed from standard/urls.py
        project = get_object_or_404(Project, name=self.kwargs['project_name'])

        """Return a list of terms for the current project"""
        return project.get_terms().exclude(is_class=True).order_by('verbatim_category', 'name')

    def get_context_data(self, **kwargs):
        # supplement the context by adding a list of class terms

        # get the original context
        context = super(TermsIndexView, self).get_context_data(**kwargs)

        # get a queryset of just paleocore classes
        project = get_object_or_404(Project, name=self.kwargs['project_name'])
        project_classes = project.get_verbatim_categories()
        # project_classes = project.get_terms().filter(is_class=True).order_by('category', 'name')
        # paleocore_classes = Term.objects.filter(projects__name='pc').order_by('category', 'name')
        # paleocore_classes = paleocore_classes.filter(is_class=True)

        # add them to the context, which now contains elements for terms and classes
        context['classes'] = project_classes
        context['project'] = project
        return context



def standard(request):
    categories = TermCategory.objects.all()
    nCategories = categories.count()
    indices = range(1,nCategories)
    # zip the iterables into one so they can be iterated in tandem in the template
    categories_indices = zip(categories,indices)
    return render_to_response('standard.html', {"categories_indices": categories_indices}, RequestContext(request))


def classes(request,category):
    matching_terms = None
    matching_class = None
    try:
        matching_class = TermCategory.objects.get(pk=category)
        matching_terms = Term.objects.filter(category=category,project__exact=5)

    except:
        pass

    return render_to_response("classes.html", {"matching_terms":matching_terms,"matching_class": matching_class},
                              RequestContext(request))


def ontologyTree(request,categoryID=0):

    return render_to_response("ontologyTree.html", {"categoryID":categoryID},
                              RequestContext(request))


def ontology(request):
    return render_to_response("ontology.html",
                            {},
                              RequestContext(request))
#
#     return render_to_response("ontologyTree.html",
#                             {"categoryID":categoryID},
#                               RequestContext(request))
# def ontology(request):
#     return render_to_response("ontology.html",
#                             {},
#                               RequestContext(request))
#
# def verticalOntologyTree(request):
#     return render_to_response("verticalOntologyTree.html",
#                             {},
#                               RequestContext(request))
#


def ontologyJSONtree(request):

    response = HttpResponse(content_type='application/json')

    theParents=[]
    theChildren=[]
    categories = TermCategory.objects.filter(tree_visibility=True)
    for category in categories:
        if category.parent:
            theParents.append(category.parent.id)
            theChildren.append(category.id)
        else:
            theParents.append("NONE")
            theChildren.append(category.id)
    links=zip(theParents, theChildren)
    parents, children = zip(*links)

    def get_nodes(node):
        d = {}

        if get_parent(node) != "NONE":
            d["name"] = TermCategory.objects.get(pk=node).name
            d["URL"] = "/standard/ontology/" + str(node)
            d["categoryID"] = node
        else:
            try:
                d["name"] = TermCategory.objects.get(pk=node).name
                d["URL"] = "/standard/ontology/" + str(node)
                d["categoryID"] = node
            except:
                d["name"] = ""
                d["URL"] = "/standard/ontology/"
                d["categoryID"] = ""

        if get_children(node):
            d['children'] = [get_nodes(child) for child in get_children(node)]
        return d

    def get_children(node):
        return [x[1] for x in links if x[0] == node]

    def get_parent(node):
        try:
            return [x[0] for x in links if x[1] == node][0]
        except:
            return "NONE"

    tree = get_nodes("NONE")

    response.write(json.dumps(tree, indent=4))

    return response


def terms(request):
    # cms_terms_intro = ContentItem.objects.get(name='terms_intro')

    m = CompareView()
    if request.method == 'POST':
        form = TermViewForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            m.showColumns = cd['showColumns']
            m.showProjects = cd['showProjects']
            m.showCategories = cd['showCategories']
            projects = Project.objects.filter(~Q(id=cd['baseProject'].id))
            m.projects = sorted(projects, key=lambda project: project.relatedTermCount(), reverse=True)
            m.baseProject = Project.objects.get(id=cd['baseProject'].id)
            for term in m.baseProject.terms():
                if term.category in m.showCategories:
                    termView = TermView()
                    termView.name = term.name
                    termView.id = term.id
                    termView.definition = term.definition
                    termView.data_type = term.data_type
                    m.termViews.append(termView)
                    for termRelationship in term.term_relationships.all():
                        projectView = ProjectView()
                        projectView.name = termRelationship.related_term.project.name
                        projectView.relatedTermRelationship = termRelationship
                        termView.projectsWithRelatedTerms.append(projectView)
        #request.session['compareView'] = m
    else:
        if request.session.get('compareView'):
            m = request.session['compareView']
            form = TermViewForm(initial = { 'baseProject' : m.baseProject.id, 'showProjects' : m.showProjects, 'showColumns' : m.showColumns} )
        else:
            form = TermViewForm()
    return render_to_response('standard/terms.html', {'m': m, 'form': form}, RequestContext(request))

def fetchAll(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def term(request, id):
    t = Term.objects.get(id=id)
    pCount = Project.objects.count()
    return render_to_response('term.html', {'t': t, 'pCount': pCount}, RequestContext(request))

@permission_required("standard.add_Term",login_url="/login/")
def addTerm(request,referringCategory=None):

    initialValues={"project":5,"status":2}
    if referringCategory:
        initialValues["category"] = referringCategory
        theCategory = TermCategory.objects.get(pk=referringCategory)

    termForm = modelform_factory(Term, exclude=("U",), widgets={"controlled_vocabulary":forms.Textarea})

    if request.method == "POST":
        form = termForm(request.POST)
        if form.is_valid():
            savedCategory = form.cleaned_data["category"].id
            form.save()
            messages.add_message(request, messages.INFO, 'Success! Term was saved.')
            return HttpResponseRedirect(reverse('standard:ontologyClass', args=(savedCategory,)))
        else:
            messages.add_message(request, messages.INFO, 'Please correct the errors below.')

    else:
        form = termForm(initial = initialValues)#initial values are Paleocore for project and "standard" for status

    return render_to_response('addTerm.html',
                              {"form":form, "referringCategory":theCategory},
                              RequestContext(request))
# def term(request, id):
#     t = Term.objects.get(id=id)
#     pCount = Project.objects.count()
#     return render_to_response('terms.html', {'t': t, 'pCount': pCount}, RequestContext(request))

@permission_required("standard.add_TermCategory",login_url="/login/")
def addClass(request):
    termCategoryForm = modelform_factory(TermCategory,widgets={"description":forms.Textarea})
    if request.method == "POST":
        form = termCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Success! Class was saved.')
            return HttpResponseRedirect(reverse("standard:ontology"))
        else:
            messages.add_message(request, messages.INFO, 'Please correct the errors below.')
    else:
        form = termCategoryForm()



    return render_to_response('addClass.html',
                              {"form":form},
                              RequestContext(request))

