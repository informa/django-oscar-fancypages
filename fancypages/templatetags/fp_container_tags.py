from django import template
from django.db.models import get_model
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.models import ContentType


register = template.Library()


class FancyContainerNode(template.Node):

    def __init__(self, container_name):
        self.container_name = template.Variable(container_name)

    def render(self, context):
        """
        Render the container provided by the ``container_name`` variable
        name in this node. If a node with this name exists in the
        context, the context variable will be used as container. Otherwise,
        we try to retrieve a container based on the variable name using
        the ``object`` variable in the context.
        """
        container = None
        try:
            container = self.container_name.resolve(context)
        except template.VariableDoesNotExist:
            try:
                container = get_model('fancypages', 'Container').get_container_by_name(
                    context['object'],
                    self.container_name.var,
                )
            except KeyError:
                return u''

        if not container:
            return u''

        extra_ctx = {
            'container': container,
            'edit_mode': context.get('edit_mode', False),
        }

        form = context.get("widget_create_form", None)
        if form:
            extra_ctx['widget_create_form'] = form

        return container.render(
            context.get('request', None),
            **extra_ctx
        )


@register.tag
def fancypages_container(parser, token):
    # split_contents() knows not to split quoted strings.
    args = token.split_contents()

    if len(args) < 2:
        raise template.TemplateSyntaxError(
            "%r tag requires at least one arguments" \
            % token.contents.split()[0]
        )

    tag_name, args = args[:1], args[1:]
    container_name = args.pop(0)
    return FancyContainerNode(container_name)


@register.simple_tag(takes_context=True)
def get_customise_url(context, instance=None):
    if not instance:
        instance = context.get('object', None)

    if instance is None:
        return u''

    try:
        content_type = ContentType.objects.get_for_model(instance)
    except AttributeError:
        return u''

    try:
        return reverse('fp-dashboard:content-customise', kwargs={
            'content_type_pk': content_type.id,
            'pk': instance.id,
        })
    except NoReverseMatch:
        return u''


@register.simple_tag(takes_context=True)
def get_preview_url(context, instance=None):
    if not instance:
        instance = context.get('object', None)

    if instance is None:
        return u''

    try:
        content_type = ContentType.objects.get_for_model(instance)
    except AttributeError:
        return u''

    try:
        return reverse('fp-dashboard:content-preview', kwargs={
            'content_type_pk': content_type.id,
            'pk': instance.id,
        })
    except NoReverseMatch:
        return u''