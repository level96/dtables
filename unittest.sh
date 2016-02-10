#!/usr/bin/env bash

coverage run --source='.' manage.py test --testrunner example.test_runner.FixturesTestRunner example
coverage html