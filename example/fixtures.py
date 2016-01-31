# coding: utf-8

from model_mommy import mommy
from example.models import Poll
from example.models import Choice


class BasicFixtures(object):

    def create_choices(self, poll, num):
        for e in range(num):
            mommy.make(Choice, poll=poll)

    def create_poll(self, num):
        for x in range(num):
            p = mommy.make(Poll)
            self.create_choices(p, 50)

    def __init__(self):
        print "Creating Fixtures: Poll, Choices"
        self.create_poll(1)