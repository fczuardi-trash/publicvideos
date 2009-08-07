#main code from http://www.djangosnippets.org/snippets/1241/ and adapted to work
#render_to_response from http://lethain.com/entry/2008/jul/22/replacing-django-s-template-language-with-jinja2/ and adapted to work
from django.conf import settings
from django.template.context import Context
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from jinja2 import FileSystemLoader, Environment, Template

class DjangoTemplate(Template):
  def render(self, *args, **kwargs):
    if args and isinstance(args[0], Context):
      for d in reversed(args[0].dicts):
        kwargs.update(d)
      args = []
    return super(DjangoTemplate, self).render(*args, **kwargs)

class DjangoEnvironment(Environment):
  template_class = DjangoTemplate
  template_dirs = getattr(settings,'TEMPLATE_DIRS')
  default_mimetype = getattr(settings, 'DEFAULT_CONTENT_TYPE')
  env = Environment(loader=FileSystemLoader(template_dirs))

template_dirs = getattr(settings, 'TEMPLATE_DIRS')
jenv = DjangoEnvironment(
  line_statement_prefix = '#',
  line_comment_prefix = '##',
  loader=FileSystemLoader(template_dirs)
)
# our hacky replacement for the Django's {% url %} tag, see https://bugs.launchpad.net/publicvideos/+bug/409678
jenv.globals['url'] = reverse

def render_to_response(filename, context={},mimetype=getattr(settings, 'DEFAULT_CONTENT_TYPE')):
  template = jenv.get_template(filename)
  rendered = template.render(**context)
  return HttpResponse(rendered,mimetype=mimetype)