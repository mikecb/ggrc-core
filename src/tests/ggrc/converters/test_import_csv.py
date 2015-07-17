# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: miha@reciprocitylabs.com

import random
import os
from os.path import abspath
from os.path import dirname
from os.path import join
from flask import json

from ggrc.models import Policy
from ggrc.models import Relationship
from ggrc.converters import errors
from tests.ggrc import TestCase
from tests.ggrc.generator import ObjectGenerator

THIS_ABS_PATH = abspath(dirname(__file__))
CSV_DIR = join(THIS_ABS_PATH, 'test_csvs/')


if os.environ.get("TRAVIS", False):
  random.seed(1)  # so we can reproduce the tests if needed


class TestBasicCsvImport(TestCase):

  def setUp(self):
    TestCase.setUp(self)
    self.generator = ObjectGenerator()
    self.client.get("/login")

  def tearDown(self):
    pass

  def generate_people(self, people):
    for person in people:
      self.generator.generate_person({
          "name": person,
          "email": "{}@reciprocitylabs.com".format(person),
      }, "gGRC Admin")

  def import_file(self, filename, dry_run=False):
    data = {"file": (open(join(CSV_DIR, filename)), filename)}
    headers = {
        "X-test-only": "true" if dry_run else "false",
        "X-requested-by": "gGRC",
    }
    response = self.client.post("/_service/import_csv",
                                data=data, headers=headers)
    self.assertEqual(response.status_code, 200)
    return json.loads(response.data)

  def test_policy_basic_import(self):
    filename = "policy_basic_import.csv"
    self.import_file(filename)
    self.assertEqual(Policy.query.count(), 3)

  def test_policy_import_working_with_warnings_dry_run(self):
    filename = "policy_import_working_with_warnings.csv"

    response_json = self.import_file(filename, dry_run=True)

    expected_warnings = set([
        errors.UNKNOWN_USER_WARNING.format(line=3, email="miha@policy.com"),
        errors.UNKNOWN_OBJECT.format(
            line=3, object_type="Program", slug="P753"),
        errors.OWNER_MISSING.format(line=4),
        errors.UNKNOWN_USER_WARNING.format(line=6, email="not@a.user"),
        errors.OWNER_MISSING.format(line=6),
        errors.WRONG_REQUIRED_VALUE.format(line=5, value="",
                                           column_name="State"),
        errors.WRONG_REQUIRED_VALUE.format(line=6, value="",
                                           column_name="State"),
    ])
    response_warnings = response_json[0]["row_warnings"]
    self.assertEqual(expected_warnings, set(response_warnings))
    response_errors = response_json[0]["row_errors"]
    self.assertEqual(set(), set(response_errors))
    self.assertEqual(4, response_json[0]["created"])
    policies = Policy.query.all()
    self.assertEqual(len(policies), 0)

  def test_policy_import_working_with_warnings(self):
    def test_owners(policy):
      self.assertNotEqual([], policy.owners)
      self.assertEqual("user@example.com", policy.owners[0].email)
    filename = "policy_import_working_with_warnings.csv"
    self.import_file(filename)

    policies = Policy.query.all()
    self.assertEqual(len(policies), 4)
    for policy in policies:
      test_owners(policy)

  def test_policy_same_titles(self):
    def test_owners(policy):
      self.assertNotEqual([], policy.owners)
      self.assertEqual("user@example.com", policy.owners[0].email)

    filename = "policy_same_titles.csv"
    response_json = self.import_file(filename)

    self.assertEqual(3, response_json[0]["created"])
    self.assertEqual(6, response_json[0]["ignored"])
    self.assertEqual(0, response_json[0]["updated"])
    self.assertEqual(9, response_json[0]["rows"])

    expected_errors = set([
        errors.DUPLICATE_VALUE_IN_CSV.format(
            line_list="3, 4, 6, 10, 11", column_name="Title",
            value="A title", s="s", ignore_lines="4, 6, 10, 11"),
        errors.DUPLICATE_VALUE_IN_CSV.format(
            line_list="5, 7", column_name="Title", value="A different title",
            s="", ignore_lines="7"),
        errors.DUPLICATE_VALUE_IN_CSV.format(
            line_list="8, 9, 10, 11", column_name="Code", value="code",
            s="s", ignore_lines="9, 10, 11"),
    ])
    response_errors = response_json[0]["row_errors"]
    self.assertEqual(expected_errors, set(response_errors))

    policies = Policy.query.all()
    self.assertEqual(len(policies), 3)
    for policy in policies:
      test_owners(policy)

  def test_facilities_intermappings_dry_run(self):
    self.generate_people(["miha", "predrag", "vladan", "ivan"])

    filename = "facilities_intermappings.csv"
    response_json = self.import_file(filename, dry_run=True)

    self.assertEqual(4, response_json[0]["created"])

    response_warnings = response_json[0]["row_warnings"]
    self.assertEqual(set(), set(response_warnings))
    self.assertEqual(0, Relationship.query.count())

  def test_facilities_intermappings(self):
    self.generate_people(["miha", "predrag", "vladan", "ivan"])

    filename = "facilities_intermappings.csv"
    response_json = self.import_file(filename)

    self.assertEqual(4, response_json[0]["created"])

    response_warnings = response_json[0]["row_warnings"]
    self.assertEqual(set(), set(response_warnings))
    self.assertEqual(4, Relationship.query.count())