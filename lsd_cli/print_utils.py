import json
import logging

from pygments import formatters, highlight, lexers

import click
import tabulate
from xtermcolor import colorize
from datetime import datetime


def __format_json_value(shell_ctx, value):
    if not shell_ctx['pretty_print']:
        if value.get('@id', None):
            res = '<{0}>'.format(underline(value['@id']))
        elif value.get('@value', None) is not None:
            res = value['@value']
        else:
            res = value
    else:
        if value.get('@id', None):
            res = underline(colorize('<{0}>'.format(value['@id']), ansi=38))
        elif value.get('@value', None) is not None:
            ltype = value.get('@type', None)

            if not ltype:
                res = colorize(value['@value'], ansi=118)
            else:
                stype = ltype[32:]

                if stype == '#integer':
                    res = colorize(value['@value'], ansi=197)
                elif stype == '#float':
                    res = colorize(value['@value'], ansi=197)
                elif stype == '#dateTime':
                    res = colorize(value['@value'], ansi=208)
                elif stype == '#boolean':
                    res = colorize(value['@value'], ansi=197)
                else:
                    res = value['@value']
        else:
            res = value

    return res


def __prepare_dict(shell_ctx, variables, results):
    rows = []

    for item in results:
        row = []

        for k in variables:
            value = __format_json_value(shell_ctx, item[k])
            row.append(value)

        rows.append(row)

    return rows


def __format_lsd_value(value):
    if isinstance(value, str):
        if value.startswith('<') and value.endswith('>'):
            res = underline(colorize(value, ansi=38))
        else:
            res = colorize(value, ansi=118)
    else:
        if isinstance(value, int):
            res = colorize(value, ansi=197)
        elif isinstance(value, float):
            res = colorize(value, ansi=197)
        elif isinstance(value, datetime):
            res = colorize(value, ansi=208)
        elif isinstance(value, bool):
            res = colorize(value, ansi=197)
        else:
            res = value

    return res


def print_leaplog_result(shell_ctx, result):
    if not result:
        output = 'No results.'
    elif isinstance(result, dict):
        if shell_ctx['json_mode_enabled']:
            output = highlight(json.dumps(result, indent=4),
                               lexers.JsonLexer(), formatters.TerminalFormatter())
        else:
            # title_context = underline("context")
            # context = highlight(json.dumps(result['@context'], indent=4),
            # lexers.JsonLexer(), formatters.TerminalFormatter())
            rows = __prepare_dict(
                shell_ctx, result['variables'], result['results'])
            tab = tabulate.tabulate(rows, headers=result['variables'])
            output = "%(tab)s" % locals()
    else:
        if shell_ctx['json_mode_enabled']:
            raise Exception('Json mode not allowed using bert')
        else:
            if not shell_ctx['pretty_print']:
                tab = tabulate.tabulate(
                    [row.tuple for row in result.rows],
                    headers=result.vars)
            else:
                tab = tabulate.tabulate(
                    [[__format_lsd_value(value) for value in row]
                     for row in result],
                    headers=result.vars)

            output = "%(tab)s" % locals()

    click.echo_via_pager(output)


def __is_list(obj):
    return hasattr(obj, '__iter__') and not isinstance(obj, str) and not isinstance(obj, dict)


def print_json_result(shell_ctx, result):
    if not result:
        output = 'No results.'
    elif shell_ctx['json_mode_enabled']:
        output = highlight(json.dumps(result, indent=4),
                           lexers.JsonLexer(), formatters.TerminalFormatter())
    else:
        if not __is_list(result):
            result = [result]

        rows = [[item[k] for k in item] for item in result]
        output = tabulate.tabulate(rows, headers=result[0].keys())

    click.echo_via_pager(output)


def bold(s):
    return '\033[1m%s\033[0m' % s


def underline(s):
    return '\033[4m%s\033[0m' % s


def clear():
    click.echo("%c[2J\033[1;1H" % 27)
