# -*- coding: utf-8 -*-
import os
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.fields import IntegerField
from django.forms.models import ModelForm
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.widgets import NumberInputWidget, MultipleInlineStylesWidget
from .plugin_base import BootstrapPluginBase
from . import settings


class CarouselSlidesForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '2', 'style': 'width: 4em;'}),
        label=_('Slides'),
        help_text=_('Number of slides for this carousel.'))


class CarouselPlugin(BootstrapPluginBase):
    name = _("Carousel")
    form = CarouselSlidesForm
    default_css_class = 'carousel'
    default_css_attributes = ('options',)
    parent_classes = ['BootstrapColumnPlugin']
    render_template = os.path.join('cms', settings.CMS_CASCADE_TEMPLATE_DIR, 'carousel.html')
    default_inline_styles = {'overflow': 'hidden'}
    fields = ('num_children', 'glossary',)
    DEFAULT_CAROUSEL_ATTRIBUTES = {'data-ride': 'carousel'}
    OPTION_CHOICES = (('slide', _("Animate")), ('pause', _("Pause")), ('wrap', _("Wrap")),)
    glossary_fields = (
        PartialFormField('interval',
            NumberInputWidget(attrs={'size': '2', 'style': 'width: 4em;', 'min': '1'}),
            label=_("Interval"),
            initial=5,
            help_text=_("Change slide after this number of seconds."),
        ),
        PartialFormField('options',
            widgets.CheckboxSelectMultiple(choices=OPTION_CHOICES),
            label=_('Options'),
            initial=['slide', 'wrap', 'pause'],
            help_text=_("Adjust interval for the carousel."),
        ),
        PartialFormField('inline_styles',
            MultipleInlineStylesWidget(['height']),
            label=_('Inline Styles'),
            help_text=_('Height of carousel.'),
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_children().count()
        return ungettext_lazy('with {0} slide', 'with {0} slides', num_cols).format(num_cols)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(CarouselPlugin, cls).get_css_classes(obj)
        if 'slide' in obj.glossary.get('options', []):
            css_classes.append('slide')
        return css_classes

    @classmethod
    def get_html_attributes(cls, obj):
        html_attributes = super(CarouselPlugin, cls).get_html_attributes(obj)
        html_attributes.update(cls.DEFAULT_CAROUSEL_ATTRIBUTES)
        html_attributes['data-interval'] = 1000 * int(obj.glossary.get('interval', 5))
        options = obj.glossary.get('options', [])
        html_attributes['data-pause'] = 'pause' in options and 'hover' or 'false'
        html_attributes['data-wrap'] = 'wrap' in options and 'true' or 'false'
        return html_attributes

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(CarouselPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, CarouselSlidePlugin)

plugin_pool.register_plugin(CarouselPlugin)


class CarouselSlidePlugin(BootstrapPluginBase):
    name = _("Slide")
    default_css_class = 'item'
    parent_classes = ['CarouselPlugin']

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(CarouselSlidePlugin, cls).get_css_classes(obj)
        if obj.get_previous_sibling() is None:
            css_classes.append('active')
        return css_classes

plugin_pool.register_plugin(CarouselSlidePlugin)
