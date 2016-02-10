# coding: utf-8

from django.shortcuts import render

from example.models import Choice
from example.tables import MyTable


def index(request):
    table = MyTable(Choice.objects.all(), request=request)
    return render(request, 'index.html', {
        'table': table
    })