# coding: utf-8

# import pytest
import unittest

from django.core.paginator import EmptyPage
from genty import genty, genty_dataset
from dtables.tables import DTable
from dtables.columns import StringColumn

from example.tables import MyTable
from example.models import Choice

import logging
logger = logging.getLogger(__name__)


@genty
class DTableInitTest(unittest.TestCase):
    def setUp(self):
        self.table = MyTable(Choice.objects.all())
        self.assertTrue(isinstance(self.table, DTable))

    @genty_dataset(
        # prefix, identifier
        ('', '', 'MyTable'),
        ('id', '', 'id-MyTable'),
        ('', 'MyPollTable', 'MyPollTable'),
        ('id', 'MyPollTable', 'id-MyPollTable'),
    )
    def test_table_prefix_identifier(self, prefix, identifier, result):
        table = MyTable(Choice.objects.all(), prefix=prefix, identifier=identifier)
        self.assertEqual(result, table.identifier)

    def test_process_fields_is_correct(self):
        ref_fields = ['id', 'poll__name', 'name', 'count', 'date_created']
        field_names = [f.accessor for f in self.table.header]
        self.assertEqual(ref_fields, field_names)

    @genty_dataset(
        # field, accessor, verbose_name
        ('id', 'id', 'Id'),
        ('poll', 'poll__name', 'Poll Name'),
        ('choice_name', 'name', 'Choice'),
        ('choice_count', 'count', 'Choice Count'),
    )
    def test_init_table_with_string_columns(self, field, accessor, verbose_name):
        self.assertTrue(field in self.table.fields)
        field_instance = self.table.fields.get(field)
        self.assertTrue(isinstance(field_instance, StringColumn))
        self.assertEqual(field_instance.accessor, accessor)
        self.assertEqual(field_instance.verbose_name, verbose_name)

    def test_table_data_and_fields(self):
        for e in self.table.data:
            self.assertEqual(1, e[0])  # id
            self.assertEqual('Poll-001', e[1])  # poll_name
            self.assertEqual('Choice-001', e[2])  # name
            break

        # for e in self.table.data:
        #     print e

    @genty_dataset(
        # fields, value,
        ({'has_next': True, 'has_previous': False, 'offset': 0, 'page': 1}, 1),
        ({'has_next': True, 'has_previous': True, 'offset': 10, 'page': 2}, 2),
        ({'has_next': True, 'has_previous': True, 'offset': 40, 'page': 5}, 5),
        ({'has_next': False, 'has_previous': True, 'offset': 50, 'page': 6}, 6),
    )
    def test_table_pagination_ranges(self, fields, page):
        base_dict = {'count': 10, 'total_count': 59, 'num_pages': 6}
        base_dict.update(fields)

        self.table = MyTable(Choice.objects.all(), page_num=page)

        meta = self.table.meta
        for k, v in base_dict.items():
            self.assertIn(k, meta)
            self.assertEqual(v, meta.get(k, None))

    @genty_dataset(-1, 0, 999)
    def test_table_raise_empty_result_when_page_num_is_out_of_range(self, page_num):
        self.assertRaises(
            EmptyPage,
            MyTable,
            Choice.objects.all(),
            page_num=page_num
        )


@genty
class DTableInitWithInitialTest(unittest.TestCase):

    @genty_dataset(
        # sorting, first_elem, last_elem
        (('name',), 'Choice-001', 'Choice-010'),
        (('-name',), 'Choice-059', 'Choice-050'),
        (('poll__name', '-name'), 'Choice-059', 'Choice-050'),
        (('poll__name', 'name'), 'Choice-001', 'Choice-010'),
    )
    def test_table_sorting_with_correct_fields(self, sorting, first_elem, last_elem):
        table = MyTable(Choice.objects.all(), sorting=sorting)

        data = [e for e in table.data]
        self.assertEqual(data[0][2], first_elem)
        self.assertEqual(data[-1][2], last_elem)

    @genty_dataset(
        (('aaaa',),),
        (('poll__name', 'xxx'),),
    )
    def test_table_sorting_with_incorrect_fields(self, fields):
        self.assertRaises(ValueError, MyTable, Choice.objects.all(), sorting=fields)


# @genty
# class DTableInitWithFiltersTest(unittest.TestCase):
#     @genty_dataset(
#         ({'name': 'Choice-003'}, ['Choice-003']),
#         (
#             {'name': 'Choice-00'},
#             [u'Choice-001', u'Choice-002', u'Choice-003', u'Choice-004',
#              u'Choice-005', u'Choice-006', u'Choice-007', u'Choice-008', u'Choice-009']
#          ),
#     )
#     def test_table_filtering(self, filters, result):
#         table = MyTable(Choice.objects.all(), filters=filters)
#         table_data = [e[2] for e in table.data]
#         self.assertEqual(table_data, result)
