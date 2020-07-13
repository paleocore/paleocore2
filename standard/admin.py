from django.contrib import admin
from .models import Term, Project, ProjectTerm, TermCategory
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist


class ProjectTermInline(admin.TabularInline):
    model = ProjectTerm
    extra = 1
    ordering = 'project',
    readonly_fields = 'native_project',
    fields = 'project', 'native', 'mapping',


class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'term_ordering', 'definition', 'native_project',
                    'category','class_category', 'iri_link', 'is_class', 'is_subclass',
                    'status')
    list_display_links = ['name']
    list_filter = ['projects', 'class_category', 'is_class', 'is_subclass', 'status']
    list_editable = ['term_ordering', 'category', 'class_category']
    list_select_related = ['data_type', 'category', 'class_category', 'status']
    read_only_fields = ['get_projects', ]
    ordering = ['term_ordering',]
    search_fields = ['name', 'projectterm__mapping' ]
    inlines = (ProjectTermInline, )
    list_per_page = 200

    def iri_link(self, obj):
        link = obj.iri
        return mark_safe(u'<a href="{link}" target=_blank>{text}</a>'.format(link=link, text=obj.iri))


class TermCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['term_count',]
    list_display = ('name', 'uri', 'description', 'parent', 'term_count')
    list_filter = ['is_occurrence']
    ordering = ('name',)


class TermMappingAdmin(admin.ModelAdmin):
    list_display = ['id', 'term_ordering', 'project', 'mapping', 'term_definition',
                    'native_project', 'term_link', 'native', 'category', 'min_set', 'max_set']
    list_filter = ['project', 'term__category', 'native', 'min_set', 'max_set']
    ordering = ['term__term_ordering']
    list_editable = ['min_set', 'max_set']

    @staticmethod
    def term_link(obj):
        link = reverse('admin:standard_term_change', args=[obj.term.id])
        return mark_safe(u'<a href="{link}">{text}</a>'.format(link=link, text=obj.term.name))

    @staticmethod
    def iri_link(obj):
        link = obj.term.iri
        return mark_safe(u'<a href="{link}" target=_blank>{text}</a>'.format(link=link, text=obj.term.iri))

    @staticmethod
    def category(obj):
        try:
            category_name = obj.term.category.name
        except AttributeError:
            category_name = None
        except ObjectDoesNotExist:
            category_name = None
        return category_name


admin.site.register(Term, TermAdmin)
admin.site.register(TermCategory, TermCategoryAdmin)
admin.site.register(ProjectTerm, TermMappingAdmin)
admin.site.register(Project)
