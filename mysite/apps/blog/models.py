from datetime import date

from django import forms
from django.db import models
from django.http.response import Http404
from django.shortcuts import render
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import MultiFieldPanel, FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable
from wagtail.search import index
from wagtail.url_routing import RouteResult


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + ["intro"]

    def get_context(self, request, **kwargs):
        context = super(BlogIndexPage, self).get_context(request, **kwargs)
        context['blogpages'] = self.get_children().live().order_by('-first_published_at')

        # Get the list of live event pages that are descendants of this page
        events = BlogPage.objects.live().descendant_of(self)
        events = events.filter(date__gte=date.today())

        events = events.order_by('date')
        context['events'] = events
        closest_ancestor = self.get_closest_ancestor
        context['closest_ancestor'] = closest_ancestor
        return context

    def get_closest_ancestor(self):
        # Find the closest ancestor which is an event index
        return self.get_ancestors().type(Page).last()

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    authors = ParentalManyToManyField('snippets.Author', blank=True)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            "date",
            FieldPanel("authors", widget=forms.CheckboxSelectMultiple),
        ], heading="Blog information"),
        "intro", "body", "gallery_images"
    ]

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(
        BlogPage,
        related_name="gallery_images",
        on_delete=models.CASCADE,
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )

    caption = models.CharField(max_length=250, blank=True)

    admin_form_fields = ["image", "caption"]

class Echoer(Page):
    template = "blog/echoer.html"  # Explicitly set the template

    def route(self, request, path_components):
        if path_components:
            data_value = request.GET
            return RouteResult(self, kwargs={
                'path_components': path_components,
                'get_params': data_value
            })
        else:
            if self.live:
                # tell Wagtail to call self.serve() with no further args
                return RouteResult(self)
            else:
                raise Http404

    def serve(self, request, path_components=[], get_params=None):
        return render(request, self.template, {
            'page': self,
            'echo': ' '.join(path_components),
            'get_params': get_params,
        })

