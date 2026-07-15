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

import click

from pyeomp.eomp.ets import EOMPETS
from pyeomp.eomp.kpi import EOMPKPI
from pyeomp import cli_options
from pyeomp.util import parse_eomp, urlopen_


@click.group()
def record():
    """EOMP record utilities"""
    pass


@click.group()
def ets():
    """EOMP ETS utilities"""
    pass


@click.group()
def kpi():
    """EOMP KPI utilities"""
    pass


@click.command('validate')
@click.pass_context
@click.argument('file_or_url')
@cli_options.OPTION_VERBOSITY
def ets_validate(ctx, file_or_url, verbosity):
    """validate EOMP record against the specification"""

    click.echo(f'Opening {file_or_url}')

    if file_or_url.startswith('http'):
        content = urlopen_(file_or_url).read()
    else:
        with open(file_or_url) as fh:
            content = fh.read()

    click.echo(f'Validating {file_or_url}')

    try:
        data = parse_eomp(content)
    except Exception as err:
        raise click.ClickException(err)
        ctx.exit(1)

    click.echo('Detected EOMP record')
    ts = EOMPETS(data)
    try:
        results = ts.run_tests()
    except Exception as err:
        raise click.ClickException(err)
        ctx.exit(1)

    click.echo(json.dumps(results, indent=4))
    ctx.exit(results['summary']['FAILED'])


@click.command('validate')
@click.pass_context
@click.argument('file_or_url')
@click.option('--summary', '-s', is_flag=True, default=False,
              help='Provide summary of KPI test results')
@click.option('--kpi', '-k', help='KPI to run, default is all')
@cli_options.OPTION_VERBOSITY
def kpi_validate(ctx, file_or_url, summary, kpi, verbosity):
    """validate EOMP record against key peformance indicators"""

    click.echo(f'Opening {file_or_url}')

    if file_or_url.startswith('http'):
        content = urlopen_(file_or_url).read()
    else:
        with open(file_or_url) as fh:
            content = fh.read()

    click.echo(f'Validating {file_or_url}')

    try:
        data = parse_eomp(content)
    except Exception as err:
        raise click.ClickException(err)
        ctx.exit(1)

    click.echo('Detected EOMP record')
    ts = EOMPETS(data)
    try:
        _ = ts.run_tests()
    except Exception as err:
        raise click.ClickException(err)
        ctx.exit(1)

    kpis = EOMPKPI(data)

    try:
        kpis_results = kpis.evaluate(kpi)
    except ValueError as err:
        raise click.UsageError(f'Invalid KPI {kpi}: {err}')
        ctx.exit(1)

    if not summary or kpi is not None:
        click.echo(json.dumps(kpis_results, indent=4))
    else:
        click.echo(json.dumps(kpis_results['summary'], indent=4))


ets.add_command(ets_validate)
kpi.add_command(kpi_validate)
record.add_command(ets)
record.add_command(kpi)
