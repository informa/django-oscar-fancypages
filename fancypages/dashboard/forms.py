from django import forms
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

from treebeard.forms import MoveNodeForm

from fancypages.widgets import SelectWidgetRadioFieldRenderer

Page = get_model('fancypages', 'Page')


class PageForm(MoveNodeForm):

    class Meta:
        model = Page
        # the fields in the MP_Node model have to be added here because
        # we change the meta class which overwrites all settings for
        # the form in django-treebeard
        exclude = ('path', 'depth', 'numchild', 'slug', 'relative_url')


class WidgetCreateSelectForm(forms.Form):
    widget_code = forms.ChoiceField(
        label=_("Add a new widget:"),
        widget=forms.RadioSelect(renderer=SelectWidgetRadioFieldRenderer)
    )

    def __init__(self, *args, **kwargs):
        super(WidgetCreateSelectForm, self).__init__(*args, **kwargs)
        choices = get_model('fancypages', 'Widget').get_available_widgets()
        self.fields['widget_code'].choices = choices

        if len(choices):
            self.fields['widget_code'].initial = choices[0][0]


class WidgetUpdateSelectForm(forms.Form):
    widget_code = forms.ChoiceField(label=_("Edit widget:"))

    def __init__(self, container, *args, **kwargs):
        super(WidgetUpdateSelectForm, self).__init__(*args, **kwargs)

        widget_choices = []
        for widget in container.widgets.select_subclasses():
            widget_choices.append((widget.id, unicode(widget)))

        self.fields['widget_code'].choices = widget_choices


class WidgetForm(forms.ModelForm):
    class Meta:
        exclude = ('container',)
        widgets = {
            'display_order': forms.HiddenInput()
        }


class AssetWidgetForm(WidgetForm):
    asset_id = forms.IntegerField(widget=forms.HiddenInput())
    asset_type = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AssetWidgetForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']
        self.asset = instance.image_asset
        if instance and instance.image_asset:
            self.fields['asset_id'].initial = instance.image_asset.id
            self.fields['asset_type'].initial = instance.image_asset.asset_type

    def clean(self):
        asset_type = self.cleaned_data.get('asset_type', '')
        model = get_model('assets', asset_type)
        if model is None:
            raise forms.ValidationError(
                "asset type %s is invalid" % asset_type
            )

        asset_id = self.cleaned_data.get('asset_id', None)
        try:
            self.asset = model.objects.get(id=asset_id)
        except model.DoesNotExist:
            raise forms.ValidationError(
                "asset with ID %s does not exist" % asset_id
            )
        return self.cleaned_data

    def save(self, commit=True):
        instance = super(AssetWidgetForm, self).save(commit=False)

        asset_id = self.cleaned_data['asset_id']
        model = get_model('assets', self.cleaned_data['asset_type'])

        instance.image_asset = model.objects.get(id=asset_id)

        if commit:
            instance.save()
        return instance

    class Meta:
        abstract = True


class TextWidgetForm(WidgetForm):
    class Meta:
        exclude = ('container',)
        widgets = {
            'display_order': forms.HiddenInput(),
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class TitleTextWidgetForm(WidgetForm):
    class Meta:
        exclude = ('container',)
        widgets = {
            'display_order': forms.HiddenInput(),
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class ImageWidgetForm(AssetWidgetForm):
    asset_id = forms.IntegerField(widget=forms.HiddenInput())
    asset_type = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        exclude = ('container', 'image_asset')
        widgets = {
            'display_order': forms.HiddenInput(),
        }


class ImageAndTextWidgetForm(AssetWidgetForm):
    asset_id = forms.IntegerField(widget=forms.HiddenInput())
    asset_type = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        exclude = ('container', 'image_asset')
        widgets = {
            'display_order': forms.HiddenInput(),
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class TwoColumnLayoutWidgetForm(WidgetForm):
    left_width = forms.IntegerField(
        widget=forms.TextInput(attrs={
            'data-min': 1,
            # the max value is restricted to '11' in JS but we need the actual
            # max value there so this is the way to pass it through
            'data-max': 12,
        }),
        label=_("Proportion of columns")
    )


class TabWidgetForm(WidgetForm):

    def __init__(self, *args, **kwargs):
        super(TabWidgetForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']
        if instance:
            for tab in instance.tabs.all():
                field_name = "tab_title_%d" % tab.id
                self.fields[field_name] = forms.CharField()
                self.fields[field_name].initial = tab.title
                self.fields[field_name].label = _("Tab title")

    def save(self):
        instance = super(TabWidgetForm, self).save()

        for tab in instance.tabs.all():
            field_name = "tab_title_%d" % tab.id
            tab.title = self.cleaned_data[field_name]
            tab.save()

        return instance
