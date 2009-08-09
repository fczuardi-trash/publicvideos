from __future__ import with_statement

import sys, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
base = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base, os.path.pardir, os.path.pardir))

from videos.models import *
from django.db import models
from django.db import connection as conn