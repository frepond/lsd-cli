import json
import pydoc

import tabulate
from pygments import formatters, highlight, lexers


def __format_value(v):
    if (v.get('@id', None)):
        return '<{0}>'.format(v['@id'])
    elif (v.get('@value', None) is not None):
        return v
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


def print_leaplog_json(leaplog_json, json_mode=True):
    if json_mode:
        formatted_result = highlight(unicode(json.dumps(leaplog_json, indent=4), 'UTF-8'),
                                     lexers.JsonLexer(), formatters.TerminalFormatter())

        pydoc.pager(formatted_result)
    else:
        title_context = underline("context")
        context = highlight(unicode(json.dumps(leaplog_json['@context'], indent=4), 'UTF-8'),
                            lexers.JsonLexer(), formatters.TerminalFormatter())
        rows = __prepare_data(leaplog_json['variables'], leaplog_json['results'])
        tab = tabulate.tabulate(rows, headers=leaplog_json['variables'])
        result = "%(title_context)s\n%(context)s%(tab)s" % locals()
        pydoc.pager(result)


def print_json(json_list, json_mode=True):
    try:
        if json_mode:
            formatted_result = highlight(unicode(json.dumps(json_list, indent=4), 'UTF-8'),
                                         lexers.JsonLexer(), formatters.TerminalFormatter())

            pydoc.pager(formatted_result)
        else:
            if json_list:
                    rows = [[item[k] for k in item] for item in json_list]
                    tab = tabulate.tabulate(rows, headers=json_list[0].keys())
            else:
                tab = []

            pydoc.pager(tab)
    except Exception as e:
                print(e)

def bold(s):
    return '\033[1m%s\033[0m' % s


def underline(s):
    return '\033[4m%s\033[0m' % s


def clear():
    print(chr(27) + "[2J")
