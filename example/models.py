# coding: utf-8

from django.db import models


class Poll(models.Model):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name


class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name='choices')
    name = models.CharField(max_length=10)
    count = models.IntegerField()
    date_created = models.DateTimeField()

    def __unicode__(self):
        return u"Poll: {} ({}: {})".format(self.poll.name, self.name, self.count)
