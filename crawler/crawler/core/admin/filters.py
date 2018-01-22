from django.contrib import admin
from crawler.constants import STATES, PRESERVATION_TAGS
from crawler.scraping.models import preservation_tag_model
from crawler.utils import pickattr

class ShouldPreserveFilter(admin.SimpleListFilter):
    title = 'need of preservation'
    parameter_name = 'should_preserve'

    def lookups(self, request, model_admin):
        return (
            ('0', 'No'),
            ('1', 'Yes'),
        )
    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
    def queryset(self, request, queryset):
        value = self.value()
        if value == '1':
            states = (
                STATES.PRESERVATION.PRESERVE,
                STATES.PRESERVATION.STORED,
            )
            queryset = queryset.filter(
                preservation_state__in=states
            )
        return queryset

class PreservationTypeFilter(admin.SimpleListFilter):
    title = 'Preservation tags detected'
    parameter_name = 'preservation_tags'
    def lookups(self, request, model_admin):
        keywords = (
            (PRESERVATION_TAGS.PRIORITY, 'priority'),
            (PRESERVATION_TAGS.RELEASE_DATE, 'release_date'),
            (PRESERVATION_TAGS.NOT_FOUND_ONLY,'notfound_only')
        )
        return keywords

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            PreservationModel = preservation_tag_model(value)
            tag_qs = PreservationModel.objects.filter(article__in=queryset)
            articles_ids = list(set(pickattr(tag_qs, 'article_id')))
            queryset = queryset.filter(pk__in=articles_ids)

        return queryset
