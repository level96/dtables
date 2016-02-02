# coding: utf-8

from django.core.paginator import Paginator
# from django.views.generic import TemplateView

from dtables.columns import BaseColumn

EXCLUDE_ATTRS = {'meta': True, 'data': True}


class DTable(object):
    id = ''
    query_set = None
    initial = None
    prefix = None
    data = None
    flat = True
    sorting = ()
    page_num = 1
    per_page = 10

    _fields = ()
    _accessor_names = None
    _page = None
    _paginator = None

    def __init__(self, id, query_set, prefix=None, initial={}, page_num=1, flat=None, per_page=None, sorting=()):
        self.id = id

        if query_set is not None:
            self.query_set = query_set
        if initial is not None:
            self.initial = initial
        if page_num is not None:
            self.page_num = page_num
        if prefix is not None:
            self.prefix = prefix
        if per_page is not None:
            self.per_page = per_page
        if flat is not None:
            self.flat = flat
        if sorting is not None:
            self.sorting = sorting

        self._process_fields()
        self._process_sorting()
        self._process_pagination()

    def _process_fields(self):
        self._field_names = filter(
            lambda f: not EXCLUDE_ATTRS.get(f, False) and isinstance(getattr(self, f), BaseColumn),
            dir(self)
        )
        self._fields = [getattr(self, f) for f in self._field_names]
        self._accessor_names = ['id'] + [a.accessor for a in self._fields]

        # Set fields are flat
        for f in self._fields:
            f.set_flat(self.flat)

    def _process_sorting(self):
        diff = set([s.replace("-", "") for s in self.sorting]) - set(self._accessor_names)
        if len(diff) > 0:
            raise ValueError("Sort-Field must be one of ({}): given: {}".format(
                self._accessor_names,
                diff,
            ))

    def _process_pagination(self):
        if self.sorting:
            self.query_set = self.query_set.order_by(*self.sorting)
        if True or self.flat:
            self.query_set = self.query_set.values(*self._accessor_names)

        self._paginator = Paginator(self.query_set, per_page=self.per_page)
        self._page = self._paginator.page(self.page_num)

    @property
    def meta(self):
        return {
            'count': self.per_page,
            'total_count': self.query_set.count(),
            'page': self.page_num,
            'has_next': self._page.has_next(),
            'has_previous': self._page.has_previous(),
            'num_pages': self._paginator.num_pages,
            'offset': (self.page_num - 1) * self.per_page
        }

    @property
    def data(self):
        return self._page.object_list

    def render(self):
        pass
