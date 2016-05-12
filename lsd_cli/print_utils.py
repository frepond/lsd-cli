import json

import click
import tabulate
from pygments import formatters, highlight, lexers


def __format_value(v):
    if (v.get('@id', None)):
        return '<{0}>'.format(v['@id'])
    elif (v.get('@value', None) is not None):
        return v['@value']
    else:
        return v


def __prepare_data(variables, results):
    rows = []

    for item in results:
        row = []

        for k in variables:
            value = __format_value(item[k])
            row.append(value)

        rows.append(row)

    return rows


def print_leaplog_result(result, json_mode=True):
    if not result:
        output = 'No results.'
    elif json_mode:
        output = highlight(json.dumps(result, indent=4),
                           lexers.JsonLexer(), formatters.TerminalFormatter())
    else:
        # title_context = underline("context")
        # context = highlight(json.dumps(result['@context'], indent=4),
        # lexers.JsonLexer(), formatters.TerminalFormatter())
        rows = __prepare_data(result['variables'], result['results'])
        tab = tabulate.tabulate(rows, headers=result['variables'])
        output = "%(tab)s" % locals()

    click.echo_via_pager(output)


def __is_list(obj):
    return hasattr(obj, '__iter__') and not isinstance(obj, str) and not isinstance(obj, dict)


def print_json_result(result, json_mode=True):
    if not result:
        output = 'No results.'
    elif json_mode:
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
