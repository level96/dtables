# coding: utf-8

from dtables.tables import DTable
from dtables.columns import StringColumn

# from example.models import Poll
# from example.models import Choice


class MyTable(DTable):
    id = StringColumn(accessor='id', verbose_name='Id')
    poll = StringColumn(accessor='poll.name', verbose_name='Poll Name')
    choice_name = StringColumn(accessor='name', verbose_name='Choice')
    choice_count = StringColumn(accessor='count', verbose_name='Choice Count')
    date_created = StringColumn(accessor='date_created', verbose_name='Date Created')