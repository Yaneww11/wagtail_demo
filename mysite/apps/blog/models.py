from datetime import date

from django.db import models
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + ["intro"]

    def get_context(self, request, **kwargs):
        context = super(BlogIndexPage, self).get_context(request, **kwargs)

        # Get the list of live event pages that are descendants of this page
        events = BlogPage.objects.live().descendant_of(self)

        # Filter events list to get ones that are either
        # running now or start in the future
        events = events.filter(date__gte=date.today())

        # Order by date
        events = events.order_by('date')
        context['events'] = events  # Changed from [12, 213] to actual events
        closest_ancestor = self.get_closest_ancestor
        context['closest_ancestor'] = closest_ancestor
        return context  # Return context dictionary instead of events

    def get_closest_ancestor(self):
        # Find the closest ancestor which is an event index
        return self.get_ancestors().type(BlogIndexPage).last()


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + ["date", "intro", "body"]

