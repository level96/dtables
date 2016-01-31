#!/usr/bin/env bash

coverage run --source='.' manage.py test -v2 --testrunner example.test_runner.FixturesTestRunner example
coverage html