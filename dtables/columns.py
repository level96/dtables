# coding: utf-8

from django.db.models import Q


class BaseColumn(object):
    field = ''
    accessor = ''
    verbose_name = ''
    flat = True
    ascending = ''
    descending = ''

    def __init__(self, field=None, accessor=None, verbose_name=None, flat=True):
        if field:
            self.field = field
        if accessor:
            self.accessor = accessor
        if verbose_name:
            self.verbose_name = verbose_name
        if flat is not None:
            self.flat = flat

        self.set_flat(self.flat)

    def set_flat(self, type):
        if type is True:
            self.accessor = self.accessor.replace(".", '__')
        else:
            self.accessor = self.accessor.replace("__", '.')

        self.ascending = self.accessor
        self.descending = "-{}".format(self.accessor)

    def get_q_function(self, value):
        return Q(**{self.accessor: value})


class StringColumn(BaseColumn):
    def get_q_function(self, value):
        return Q(**{'{}__icontains'.format(self.accessor): value})