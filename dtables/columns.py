# coding: utf-8


class BaseColumn(object):
    field = ''
    accessor = ''
    verbose_name = ''
    flat = True

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

    def render(self):
        return


class StringColumn(BaseColumn):
    pass