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
        self.table = MyTable('PollChoiceTable', Choice.objects.all())
        self.assertTrue(isinstance(self.table, DTable))

    def test_process_fields_is_correct(self):
        self.assertEqual(['choice_count', 'choice_name', 'date_created', 'poll'], self.table._field_names)

    @genty_dataset(
        # field, accessor, verbose_name
        ('poll', 'poll__name', 'Poll Name'),
        ('choice_name', 'name', 'Choice'),
        ('choice_count', 'count', 'Choice Count'),
    )
    def test_init_table_with_string_columns(self, field, accessor, verbose_name):
        self.assertTrue(hasattr(self.table, field))
        self.assertTrue(isinstance(getattr(self.table, field), StringColumn))
        self.assertEqual(getattr(self.table, field).accessor, accessor)
        self.assertEqual(getattr(self.table, field).verbose_name, verbose_name)

    def test_table_data_and_fields(self):
        for e in self.table.data:
            self.assertIn('count', e)
            self.assertIn('poll__name', e)
            self.assertIn('name', e)
            self.assertIn('id', e)
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

        self.table = MyTable('PollChoiceTable', Choice.objects.all(), page_num=page)

        meta = self.table.meta
        for k, v in base_dict.items():
            self.assertIn(k, meta)
            self.assertEqual(v, meta.get(k, None))

    @genty_dataset(-1, 0, 999)
    def test_table_raise_empty_result_when_page_num_is_out_of_range(self, page_num):
        self.assertRaises(
            EmptyPage,
            MyTable,
            'PollChoiceTable',
            Choice.objects.all(),
            page_num=page_num
        )


@genty
class DTableInitWithInitialTest(unittest.TestCase):

    @genty_dataset(
        # sorting, first_elem, last_elem
        ((MyTable.choice_name.ascending,), 'Choice-001', 'Choice-010'),
        ((MyTable.choice_name.descending,), 'Choice-059', 'Choice-050'),
        ((MyTable.poll.ascending, MyTable.choice_name.descending), 'Choice-059', 'Choice-050'),
        ((MyTable.poll.ascending, MyTable.choice_name.ascending), 'Choice-001', 'Choice-010'),
    )
    def test_table_sorting_with_correct_fields(self, sorting, first_elem, last_elem):
        table = MyTable('PollChoiceTable', Choice.objects.all(), sorting=sorting)

        data = [e for e in table.data]

        self.assertEqual(data[0]['name'], first_elem)
        self.assertEqual(data[-1]['name'], last_elem)

    @genty_dataset(
        (('aaaa',),),
        ((MyTable.poll.accessor, 'xxx'),),
    )
    def test_table_sorting_with_incorrect_fields(self, fields):
        self.assertRaises(ValueError, MyTable, 'PollChoiceTable', Choice.objects.all(), sorting=fields)


@genty
class DTableInitWithFiltersTest(unittest.TestCase):
    @genty_dataset(
        ({MyTable.choice_name: 'Choice-003'}, ['Choice-003']),
        (
                {MyTable.choice_name: 'Choice-00'},
                [u'Choice-001', u'Choice-002', u'Choice-003', u'Choice-004',
                 u'Choice-005', u'Choice-006', u'Choice-007', u'Choice-008', u'Choice-009']
         ),
    )
    def test_table_filtering(self, filters, result):
        table = MyTable('PollChoiceTable', Choice.objects.all(), filters=filters)
        table_data = [e.get('name') for e in table.data]
        self.assertEqual(table_data, result)
