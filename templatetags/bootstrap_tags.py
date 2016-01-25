from django.template.base import kwarg_re, FilterExpression
import re

__author__ = 'danil'

from django import template
from django.template import Template, Context, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.template.loader import get_template

register = template.Library()

def render_template_to_unicode(template, context=None):
    """
    Render a Template to unicode
    """
    if not isinstance(template, Template):
        template = get_template(template)
    if context is None:
        context = {}
    return template.render(Context(context))

# @register.simple_tag()
# def bootstrap_remove_modal(*args, **kwargs):
#     return render_template_to_unicode('commons/templatetags/remove_modal.html')

@register.inclusion_tag('commons/templatetags/remove_modal.html')
def bootstrap_remove_modal(*args, **kwargs):
    return {}

# RegEx for quoted string
QUOTED_STRING = re.compile(r'^["\'](?P<noquotes>.+)["\']$')

def handle_var(value, context):
    """
    Handle template tag variable
    """
    # Resolve FilterExpression and Variable immediately
    if isinstance(value, FilterExpression) or isinstance(value, Variable):
        return value.resolve(context)
    # Return quoted strings unquoted
    # http://djangosnippets.org/snippets/886
    stringval = QUOTED_STRING.search(value)
    if stringval:
        return stringval.group('noquotes')
    # Resolve variable or return string value
    try:
        return Variable(value).resolve(context)
    except VariableDoesNotExist:
        return value

def parse_token_contents(parser, token):
    """
    Parse template tag contents
    """
    bits = token.split_contents()
    tag = bits.pop(0)
    args = []
    kwargs = {}
    asvar = None
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]
    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError('Malformed arguments to tag "{}"'.format(tag))
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))
    return {
        'tag': tag,
        'args': args,
        'kwargs': kwargs,
        'asvar': asvar,
    }

@register.tag('bootstrap_modal')
def bootstrap_modal(parser, token):
    kwargs = parse_token_contents(parser, token)
    nodelist_body = parser.parse(('bootstrap_modal_buttons', 'end_bootstrap_modal'))
    token = parser.next_token()
    if token.contents == 'bootstrap_modal_buttons':
        nodelist_buttons = parser.parse(('end_bootstrap_modal',))
        parser.delete_first_token()
    else:
        nodelist_buttons = None

    return ModalNode(nodelist_body, nodelist_buttons, **kwargs)

MODAL_HEADER = """
    <div class="modal fade" id="%(id)s" tabindex="-1" role="dialog" aria-labelledby="editModalLabel">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title">%(title)s</h4>
          </div>
          <div class="modal-body">
"""
MODAL_END_BODY = """
    </div>
    <div class="modal-footer">
"""

MODAL_DEFAULT_BUTTONS = """
    <button type="submit" class="btn btn-primary">Save</button>
    <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
"""

MODAL_FOOTER = """
          </div>
        </div>
      </div>
    </div>
"""

class ModalNode(template.Node):
    def __init__(self, nodelist_body, nodelist_buttons, tag, args, kwargs, asvar):
        self.nodelist_body = nodelist_body
        self.nodelist_buttons = nodelist_buttons
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        output_kwargs = {}
        for key in self.kwargs:
            output_kwargs[key] = handle_var(self.kwargs[key], context)

        modal_id = output_kwargs.get('id', 'default_id')
        title = output_kwargs.get('title', 'TITLE')

        if self.nodelist_buttons is None:
            modal_buttons = MODAL_DEFAULT_BUTTONS
        else:
            modal_buttons = self.nodelist_buttons.render(context)

        return MODAL_HEADER % {'id': modal_id, 'title': title} \
               + self.nodelist_body.render(context) \
               + MODAL_END_BODY \
               + modal_buttons \
               + MODAL_FOOTER