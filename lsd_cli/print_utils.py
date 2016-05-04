import json
import pydoc

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
        output = highlight(unicode(json.dumps(result, indent=4), 'UTF-8'),
                           lexers.JsonLexer(), formatters.TerminalFormatter())
    else:
        title_context = underline("context")
        context = highlight(unicode(json.dumps(result['@context'], indent=4), 'UTF-8'),
                            lexers.JsonLexer(), formatters.TerminalFormatter())
        rows = __prepare_data(result['variables'], result['results'])
        tab = tabulate.tabulate(rows, headers=result['variables'])
        output = "%(title_context)s\n%(context)s%(tab)s" % locals()

    pydoc.pager(output)


def __is_list(obj):
    return hasattr(obj, '__iter__') and not isinstance(obj, str) and not isinstance(obj, dict)


def print_json_result(result, json_mode=True):
    if not result:
        output = 'No results.'
    elif json_mode:
        output = highlight(unicode(json.dumps(result, indent=4), 'UTF-8'),
                           lexers.JsonLexer(), formatters.TerminalFormatter())
    else:
        if not __is_list(result):
            result = [result]

        print(__is_list(result))
        print(result)

        rows = [[item[k] for k in item] for item in result]
        output = tabulate.tabulate(rows, headers=result[0].keys())

    pydoc.pager(output)


def bold(s):
    return '\033[1m%s\033[0m' % s


def underline(s):
    return '\033[4m%s\033[0m' % s


def clear():
    print(chr(27) + "[2J")
