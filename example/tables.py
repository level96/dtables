# coding: utf-8

from dtables.tables import DTable
from dtables.columns import StringColumn

# from example.models import Poll
# from example.models import Choice


class MyTable(DTable):
    poll = StringColumn(field='poll_name', accessor='poll.name', verbose_name='Poll Name')
    choice_name = StringColumn(field='name', accessor='name', verbose_name='Choice')
    choice_count = StringColumn(field='count', accessor='count', verbose_name='Choice Count')
