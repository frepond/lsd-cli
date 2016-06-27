"""CLI print utils."""

import logging

from pygments import formatters, highlight, lexers

import click
import tabulate
import ujson as json
from xtermcolor import colorize


def __format_value(value):
    if isinstance(value, list):
        result = '[{0} elems...]'.format(len(value))
    elif value.get('@id', None):
        result = underline(colorize('<{0}>'.format(value['@id']), ansi=38))
    elif value.get('@value', None) is not None:
        ltype = value.get('@type', None)

        if not ltype:
            result = colorize(value['@value'], ansi=118)
        else:
            stype = ltype[32:]

            if stype == '#integer':
                result = colorize(value['@value'], ansi=197)
            elif stype == '#float':
                result = colorize(value['@value'], ansi=197)
            elif stype == '#dateTime':
                result = colorize(value['@value'], ansi=208)
            elif stype == '#boolean':
                result = colorize(value['@value'], ansi=197)
            else:
                result = value['@value']
    else:
        result = value

    return result


def __prepare_data(_, variables, results):
    rows = []

    for item in results:
        row = []

        for k in variables:
            value = __format_value(item[k])
            row.append(value)

        rows.append(row)

    return rows


def print_leaplog_result(shell_ctx, result):
    """Leaplog result (json-ld) formatter and stdout printer.
    :param shell_ctx: the shell context configuration.
    :param result: the json-ld to format and print.
    """
    if not result:
        output = 'No results.'
    elif shell_ctx['json_mode_enabled']:
        output = highlight(json.dumps(result, indent=4),
                           lexers.JsonLexer(), formatters.TerminalFormatter())
    else:
        # title_context = underline("context")
        # context = highlight(json.dumps(result['@context'], indent=4),
        # lexers.JsonLexer(), formatters.TerminalFormatter())
        logging.debug(result)
        rows = __prepare_data(
            shell_ctx, result['variables'], result['results'])
        tab = tabulate.tabulate(rows, headers=result['variables'])
        output = '%(tab)s' % locals()

    click.echo_via_pager(output)


def __is_list(obj):
    return hasattr(obj, '__iter__') and not isinstance(obj, str) and not isinstance(obj, dict)


def print_json_result(_, result):
    """Json result formatter and stdout printer.
    :param shell_ctx: the shell context configuration.
    :param result: the json to format and print.
    """
    if not result:
        output = 'No results.'
    else:
        output = highlight(json.dumps(result, indent=4),
                           lexers.JsonLexer(), formatters.TerminalFormatter())

    click.echo_via_pager(output)


def bold(string):
    """Adds ansi bold format to a string.
    :param s: the string to format.
    :return: the formated string.
    """
    return '\033[1m%s\033[0m' % string


def underline(string):
    """Adds ansi underline format to a string.
    :param s: the string to format.
    :return: the formated string.
    """
    return '\033[4m%s\033[0m' % string


def clear():
    """Clears the stdout."""
    click.echo("%c[2J\033[1;1H" % 27)
