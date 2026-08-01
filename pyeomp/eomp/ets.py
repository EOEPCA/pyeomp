##############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import json
import logging
import requests
import uuid

from jsonschema import FormatChecker
from jsonschema.validators import Draft202012Validator

from pyeomp.bundle import EOMP_FILES
from pyeomp.errors import TestSuiteError
from pyeomp.util import get_current_datetime_rfc3339, get_package_version

LOGGER = logging.getLogger(__name__)


def gen_test_id(test_id: str) -> str:
    """
    Convenience function to print test identifier as URI

    :param test_id: test suite identifier

    :returns: test identifier as URI
    """

    return f'http://eoepca.org/spec/eomp/1/conf/core/{test_id}'


class EOMPETS:
    def __init__(self, record):
        """
        initializer

        :param data: dict of EOMP JSON

        :returns: `pyeomp.eomp.ets.EOMPETS`
        """

        self.version = get_package_version()
        self.errors = []
        self.record = record

    def run_tests(self):

        results = []
        tests = []

        ets_report = {
            'id': str(uuid.uuid4()),
            'report_type': 'ets',
            'summary': {
                'PASSED': 0,
                'FAILED': 0,
                'SKIPPED': 0,
                'WARNINGS': 0
            },
            'generated_by': f'pyeomp {self.version} (https://github.com/EOEPCA/pyeomp)'  # noqa
        }

        for f in dir(EOMPETS):
            if all([callable(getattr(EOMPETS, f)),
                    f.startswith('test_requirement'),
                    not f.endswith('validation')]):
                tests.append(f)

        LOGGER.debug('Running schema validation')
        result = self.test_requirement_validation()
        results.append(result)
        if result['code'] == 'FAILED':
            self.errors.append(result)

        for t in tests:
            result = getattr(self, t)()
            results.append(result)
            if result['code'] == 'FAILED':
                self.errors.append(result)

        for code in ['PASSED', 'FAILED', 'SKIPPED', 'WARNINGS']:
            r = len([t for t in results if t['code'] == code])
            ets_report['summary'][code] = r

        ets_report['tests'] = results
        ets_report['datetime'] = get_current_datetime_rfc3339()
        ets_report['metadata_id'] = self.record['id']

        return ets_report

    def test_requirement_stac_extensions(self):
        """
        Validate that an EOMP record's STAC extensions is valid
        to the authoritative schema.
        """

        status = {
            'id': gen_test_id('stac_extensions'),
            'code': 'PASSED'
        }

        for stac_extension in self.record['stac_extensions']:
            LOGGER.debug(f'Validating against STAC Extension {stac_extension}')
            stac_extension_schema = requests.get(stac_extension)
            stac_extension_schema.raise_for_status()

            validation_errors = validate_json(
                stac_extension_schema.json(), self.record)

            if validation_errors:
                status['code'] = 'FAILED'
                status['message'] = f'{len(validation_errors)} error(s)'
                status['errors'] = validation_errors

        return status

    def test_requirement_validation(self):
        """
        Validate that an EOMP record is valid to the authoritative schema.
        """

        validation_errors = []

        status = {
            'id': gen_test_id('validation'),
            'code': 'PASSED'
        }

        schema = EOMP_FILES / 'eomp-bundled.json'

        if not schema.exists():
            msg = "EOMP schema missing. Run 'pyeomp bundle sync' to cache"
            LOGGER.error(msg)
            raise RuntimeError(msg)

        with schema.open() as fh:
            LOGGER.debug(f'Validating {self.record} against {schema}')
            validation_errors = validate_json(json.load(fh), self.record)

            if validation_errors:
                status['code'] = 'FAILED'
                status['message'] = f'{len(validation_errors)} error(s)'
                status['errors'] = validation_errors

        return status

    def raise_for_status(self):
        """
        Raise error if one or more failures were found during validation.

        :returns: `pyeomp.errors.TestSuiteError` or `None`
        """

        if len(self.errors) > 0:
            raise TestSuiteError('Invalid EOMP record', self.errors)


def validate_json(schema: dict, instance: dict) -> list:
    """
    Helper function to validate JSON against a JSON Schema

    :param schema: `dict` of JSON Schema
    :paran instance: `dict` of request instance

    :returns: `list` of validation errors
    """

    format_checkers = ['date-time', 'email', 'regex',
                       'uri', 'uri-reference']

    validation_errors = []
    LOGGER.debug('Validating input against schema')
    LOGGER.debug(f'Input: {instance}')
    LOGGER.debug(f'Schema: {schema}')
    validator = Draft202012Validator(
        schema, format_checker=FormatChecker(formats=format_checkers))

    for error in validator.iter_errors(instance):
        msg = f'{error.json_path}: {error.message}'
        LOGGER.debug(msg)
        validation_errors.append(msg)

    return validation_errors
