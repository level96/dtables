# coding: utf-8

# import pytest
import unittest
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
        self.assertEqual(['choice_count', 'choice_name', 'poll'], self.table._field_names)

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

        for e in self.table.data:
            logger.debug(e)

    @genty_dataset(
        # field, value,
        ({'count': 10, 'has_next': True, 'has_previous': False, 'total_count': 50, 'offset': 0, 'num_pages': 5, 'page': 1}, 1),
        ({'count': 10, 'has_next': True, 'has_previous': True, 'total_count': 50, 'offset': 10, 'num_pages': 5, 'page': 2}, 2),
        ({'count': 10, 'has_next': False, 'has_previous': True, 'total_count': 50, 'offset': 40, 'num_pages': 5, 'page': 5}, 5),
    )
    def test_table_pagination_ranges(self, fields, page):
        self.table = MyTable('PollChoiceTable', Choice.objects.all(), page_num=page)

        meta = self.table.meta
        for k, v in fields.items():
            self.assertIn(k, meta)
            self.assertEqual(v, meta.get(k, None))


class DTableInitWithInitialTest(unittest.TestCase):
    pass