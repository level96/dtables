# coding: utf-8

from django.core.paginator import Paginator

from dtables.columns import BaseColumn

import logging
logger = logging.getLogger(__name__)

EXLCUDE_ATTRS = ('meta', 'data')


class DTable(object):
    id = ''
    query_set = None
    initial = None
    prefix = None
    data = None
    flat = True
    page_num = 1
    per_page = 10

    _fields = ()
    _accessor_names = None
    _page = None
    _paginator = None

    def __init__(self, id, query_set, prefix='', initial={}, page_num=1, flat=None, per_page=None,):
        self.id = id

        if query_set:
            self.query_set = query_set
        if initial:
            self.initial = initial
        if page_num:
            self.page_num = page_num
        if prefix:
            self.prefix = prefix
        if per_page:
            self.per_page = per_page
        if flat is not None:
            self.flat = flat

        self._process_fields()
        self._process_pagination()

    def _process_fields(self):
        self._field_names = filter(
            lambda x: x not in EXLCUDE_ATTRS and isinstance(getattr(self, x), BaseColumn),
            dir(self)
        )
        self._fields = [getattr(self, f) for f in self._field_names]
        self._accessor_names = ['id'] + [a.accessor for a in self._fields]
        for f in self._fields:
            f.set_flat(self.flat)

    def _process_pagination(self):
        self._paginator = Paginator(
            self.query_set.values(*self._accessor_names),
            per_page=self.per_page
        )
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
            'offset': (self.page_num-1) * self.per_page
        }

    @property
    def data(self):
        for column in self._page.object_list:
            yield column

    def render(self):

        return ''
