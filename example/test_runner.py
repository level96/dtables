# coding: utf-8

import logging

from django.test.runner import DiscoverRunner
from example.fixtures import BasicFixtures


class FixturesTestRunner(DiscoverRunner):

    def setup_databases(self, *args, **kwargs):
        result = super(FixturesTestRunner, self).setup_databases(*args, **kwargs)
        BasicFixtures()
        return result
