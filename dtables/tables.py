# coding: utf-8

import copy
from collections import OrderedDict

from django.core.paginator import Paginator
from django.forms.widgets import MediaDefiningClass
from django.utils import six

# from django.views.generic import TemplateView

from dtables.columns import BaseColumn

EXCLUDE_ATTRS = {'meta': True, 'data': True}


class DeclarativeFieldsMetaclass(MediaDefiningClass):
    """
    Metaclass that collects Fields declared on the base classes.
    """
    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, BaseColumn):
                current_fields.append((key, value))
                attrs.pop(key)
        current_fields.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_fields'] = OrderedDict(current_fields)

        new_class = (super(DeclarativeFieldsMetaclass, mcs).__new__(mcs, name, bases, attrs))

        # Walk through the MRO.
        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class BaseDTable(object):
    identifier = ''
    query_set = None
    initial = None
    prefix = None
    data = None
    flat = True
    filters = None
    sorting = ()
    page_num = 1
    per_page = 10
    field_order = None
    fields = {}
    request = None

    _accessor_names = None
    _page = None
    _paginator = None

    def __init__(self, query_set, identifier=None, prefix=None, initial={}, filters={},
                 page_num=1, flat=None, per_page=None, sorting=(), field_order=None,
                 request=None):

        if query_set is not None:
            self.query_set = query_set
        if identifier is not None:
            self.identifier = identifier
        if initial is not None:
            self.initial = initial
        if prefix is not None:
            self.prefix = prefix
        if page_num is not None:
            self.page_num = page_num
        if per_page is not None:
            self.per_page = per_page
        if flat is not None:
            self.flat = flat
        if filters is not None:
            self.filters = filters
        if sorting is not None:
            self.sorting = sorting

        self.request = request

        # Handling field definition ordering
        self.fields = copy.deepcopy(self.base_fields)
        self._bound_fields_cache = {}
        self._order_fields(self.field_order if field_order is None else field_order)

        # Processing
        self._process_identifier()
        self._process_request()
        self._process_fields()
        self._process_q_functions()
        self._process_sorting()
        self._process_pagination()

    def _order_fields(self, field_order):
        """
        Rearranges the fields according to field_order.
        field_order is a list of field names specifying the order. Fields not
        included in the list are appended in the default order for backward
        compatibility with subclasses not overriding field_order. If field_order
        is None, all fields are kept in the order defined in the class.
        Unknown fields in field_order are ignored to allow disabling fields in
        form subclasses without redefining ordering.
        """
        if field_order is None:
            return
        fields = OrderedDict()
        for key in field_order:
            try:
                fields[key] = self.fields.pop(key)
            except KeyError:  # ignore unknown fields
                pass
        fields.update(self.fields)  # add remaining fields in original order
        self.fields = fields

    def _process_identifier(self):
        identifier = self.identifier if self.identifier else self.__class__.__name__
        prefix = '{}-'.format(self.prefix) if self.prefix else ''
        self.identifier = '{}{}'.format(prefix, identifier) if self.prefix else identifier

    def _process_request(self):
        """
        Extract request params to ordering, pagination, filtering
        :return:
        """

        if not self.request:
            return

        self.sorting = self.request.GET.getlist('sorting', self.sorting)
        self.per_page = self.request.GET.get('per_page', self.per_page)
        self.page_num = self.request.GET.get('page', self.page_num)

    def _process_fields(self):
        self._accessor_names = [a.accessor for a in self.fields.values()]

        # Set fields are flat
        # for f in self._fields.values():
        #     f.set_flat(self.flat)

    def _process_q_functions(self):
        for field, search in self.filters.items():
            self.query_set = self.query_set.filter(field.get_q_function(search))

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
            self.query_set = self.query_set.values_list(*self._accessor_names)

        self._paginator = Paginator(self.query_set, per_page=self.per_page)
        self._page = self._paginator.page(self.page_num)

    @property
    def meta(self):
        total_count = self.query_set.count()
        count = total_count if total_count < self.per_page else self.per_page
        return {
            'count': count,
            'total_count': total_count,
            'page': self.page_num,
            'has_next': self._page.has_next(),
            'has_previous': self._page.has_previous(),
            'num_pages': self._paginator.num_pages,
            'offset': (self.page_num - 1) * self.per_page
        }

    @property
    def header(self):
        return [f for f in self.fields.values()]

    @property
    def data(self):
        return self._page.object_list

    def __iter__(self):
        for name in self.fields:
            yield self[name]

    def __getitem__(self, name):
        """Returns a BoundField with the given name."""

        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError(
                "Key %r not found in '%s'" % (name, self.__class__.__name__))
        if name not in self._bound_fields_cache:
            self._bound_fields_cache[name] = field.get_bound_field(self, name)
        return self._bound_fields_cache[name]




class DTable(six.with_metaclass(DeclarativeFieldsMetaclass, BaseDTable)):
    "Table"