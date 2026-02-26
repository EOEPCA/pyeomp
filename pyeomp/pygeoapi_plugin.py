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

#
# pyeomp as a service
# -------------------
#
# This file is intended to be used as a pygeoapi process plugin which will
# provide pyeomp functionality via OGC API - Processes.
#
# To integrate this plugin in pygeoapi:
#
# 1. ensure pyeomp is installed into the pygeoapi deployment environment
#
# 2. add the processes to the pygeoapi configuration as follows:
#
# pyeomp-record-validate:
#     type: process
#     processor:
#         name: pyeomp.pygeoapi_plugin.EOMPETSProcessor
#
# 3. (re)start pygeoapi
#
# The resulting processes will be available at the following endpoints:
#
# /processes/pyeomp-record-validate
#
# Note that pygeoapi's OpenAPI/Swagger interface (at /openapi) will also
# provide a developer-friendly interface to test and run requests
#

import json
import logging

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError

from pyeomp.eomp.ets import EOMPTestSuite
from pyeomp.util import get_package_version, THISDIR, urlopen_

LOGGER = logging.getLogger(__name__)

with (THISDIR / 'resources' / 'ets-report.json').open() as fh:
    ETS_REPORT_SCHEMA = json.load(fh)

with (THISDIR / 'resources' / 'worldcereal_inference2.json').open() as fh:
    EXAMPLE_EOMP = json.load(fh)


PROCESS_EOMP_ETS = {
    'version': get_package_version(),
    'id': 'pyeomp-record-validate',
    'title': {
        'en': 'EOMP record validator'
    },
    'description': {
        'en': 'Validate a EOMP record against the ETS'
    },
    'keywords': ['eoepca', 'eomp', 'ets', 'test suite', 'metadata'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://github.com/EOEPCA/eomp',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'record': {
            'title': 'EOMP record',
            'description': 'EOMP record (can be inline or remote link)',
            'schema': {
                'type': ['object', 'string']
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['eomp']
        }
    },
    'outputs': {
        'result': {
            'title': 'Report of ETS results',
            'description': 'Report of ETS results',
            'schema': {
                'contentMediaType': 'application/json',
                **ETS_REPORT_SCHEMA
            }
        }
    },
    'example': {
        'inputs': {
            'record': EXAMPLE_EOMP
        }
    }
}


class EOMPETSProcessor(BaseProcessor):
    """EOMP ETS"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pyeomp.pygeoapi_plugin.EOMPETSProcessor
        """

        super().__init__(processor_def, PROCESS_EOMP_ETS)

    def execute(self, data, outputs=None):

        response = None
        mimetype = 'application/json'
        record = data.get('record')

        if record is None:
            msg = 'Missing record'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        if isinstance(record, str) and record.startswith('http'):
            LOGGER.debug('Record is a link')
            record = json.loads(urlopen_(record).read())
        else:
            LOGGER.debug('Record is inline')

        LOGGER.debug('Running ETS against record')
        response = EOMPTestSuite(record).run_tests()

        return mimetype, response

    def __repr__(self):
        return '<EOMPETSProcessor>'
