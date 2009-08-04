from django.conf import settings
from django import forms
from django.forms.widgets import Input
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

def register(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      new_user = form.save()
      return HttpResponseRedirect("/")
  else:
    form = UserCreationForm()
  return render_to_response("users/register.html", {'form': form})