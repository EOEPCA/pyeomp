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

import logging
from pathlib import Path
import shutil
import tempfile

import click

from pyeomp import cli_options
from pyeomp.util import get_userdir, urlopen_

LOGGER = logging.getLogger(__name__)

USERDIR = get_userdir()

TEMPDIR = tempfile.TemporaryDirectory()
TEMPDIR2 = Path(tempfile.TemporaryDirectory().name)

EOMP_FILES = get_userdir() / 'eomp'
EOMP_FILES_TEMP = TEMPDIR2 / 'eomp'


@click.group()
def bundle():
    """Configuration bundle management"""
    pass


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
def sync(ctx, verbosity):
    """Sync configuration bundle"""

    LOGGER.debug('Caching schema')
    LOGGER.debug(f'Downloading EOMP schema to {EOMP_FILES_TEMP}')
    EOMP_FILES_TEMP.mkdir(parents=True, exist_ok=True)
    EOMP_SCHEMA = 'https://raw.githubusercontent.com/EOEPCA/eomp/refs/heads/master/schemas/eomp-bundled.json'  # noqa

    json_schema = EOMP_FILES_TEMP / 'eomp-bundled.json'
    with json_schema.open('wb') as fh:
        fh.write(urlopen_(f'{EOMP_SCHEMA}').read())

    LOGGER.debug(f'Removing {USERDIR}')
    if USERDIR.exists():
        shutil.rmtree(USERDIR)

    LOGGER.debug(f'Moving files from {TEMPDIR2} to {USERDIR}')
    shutil.move(TEMPDIR2, USERDIR)

    LOGGER.debug(f'Cleaning up {TEMPDIR}')
    TEMPDIR.cleanup()


bundle.add_command(sync)
