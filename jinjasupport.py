#copied from http://www.djangosnippets.org/snippets/1241/ and adapted to work
from django.conf import settings
from django.template.context import Context
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

template_dirs = getattr(settings, 'TEMPLATE_DIRS')

jenv = DjangoEnvironment(
  line_statement_prefix = '#',
  line_comment_prefix = '##',
  loader=FileSystemLoader(template_dirs)
)

