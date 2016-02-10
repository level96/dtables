# coding: utf-8

from django.db.models import Q


class BaseColumn(object):
    accessor = ''
    verbose_name = ''
    flat = True
    ascending = ''
    descending = ''
    creation_counter = 0

    def __init__(self, accessor=None, verbose_name=None, flat=True):
        if accessor:
            self.accessor = accessor
        if verbose_name:
            self.verbose_name = verbose_name
        if flat is not None:
            self.flat = flat

        # Ensure correct field ordering : field definition
        self.creation_counter = BaseColumn.creation_counter
        BaseColumn.creation_counter += 1

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