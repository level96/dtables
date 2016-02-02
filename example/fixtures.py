# coding: utf-8

import random

from model_mommy import mommy
from example.models import Poll
from example.models import Choice


class BasicFixtures(object):

    def create_choices(self, poll, num):
        for e in range(1, num + 1):
            mommy.make(Choice, poll=poll, name="Choice-{:03}".format(e), count=random.randint(0, 50))

    def create_poll(self, num):
        for x in range(1, num + 1):
            p = mommy.make(Poll, name="Poll-{:03}".format(x))
            self.create_choices(p, 59)

    def __init__(self):
        print "Creating Fixtures: Poll, Choices"
        self.create_poll(1)