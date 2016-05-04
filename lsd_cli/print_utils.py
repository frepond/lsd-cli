import json
import pydoc

import tabulate
from pygments import formatters, highlight, lexers


def __format_value(v):
    if (v.get('@id', None)):
        return '<{0}>'.format(v['@id'])
    else:
        return v


def __prepare_data(leaplog_results):
    rows = []

    for item in leaplog_results:
        row = []

        for (k, v) in item.items():
            value = __format_value(v)
            row.append(value)

        rows.append(row)

    return rows


def print_leaplog_json(leaplog_json, json_mode=True):
    if json_mode:
        formatted_result = highlight(unicode(json.dumps(leaplog_json, indent=4), 'UTF-8'),
                                     lexers.JsonLexer(), formatters.TerminalFormatter())

        pydoc.pager(formatted_result)
    else:
        title_context = underline("context")
        context = highlight(unicode(json.dumps(leaplog_json['@context'], indent=4), 'UTF-8'),
                            lexers.JsonLexer(), formatters.TerminalFormatter())
        rows = __prepare_data(leaplog_json['results'])
        tab = tabulate.tabulate(rows, headers=leaplog_json['variables'])
        result = "%(title_context)s\n%(context)s%(tab)s" % locals()
        pydoc.pager(result)


def bold(s):
    return '\033[1m%s\033[0m' % s


def underline(s):
    return '\033[4m%s\033[0m' % s


def clear():
    print(chr(27) + "[2J")
