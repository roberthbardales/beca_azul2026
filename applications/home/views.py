from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'home/index.html'


def permission_denied(request, exception=None):
    return render(request, '403.html', status=403)
