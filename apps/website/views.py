from django.conf import settings
from lib.jinjasupport import render_to_response

def index(request):
  if request.user.is_authenticated():
    return render_to_response("website/index.html", {})
  else:
    return render_to_response("website/index_anonymous.html", {})
