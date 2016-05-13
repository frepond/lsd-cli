import logging
import re

from lsd_cli.print_utils import *
from xtermcolor import colorize

re_prefix = re.compile(r'^\s*(\w+):\s*(\<.*\>).$')


def __exec_leaplog(shell_ctx, filename):
    json_mode_enabled = shell_ctx['json_mode_enabled']
    lsd_api = shell_ctx['lsd_api']

    try:
        with open(filename, 'r') as file:
            content = file.read()
    except Exception as e:
        raise Exception("ERROR: could not read {0}".format(filename))

    result = lsd_api.leaplog(content)
    print_leaplog_result(result, json_mode_enabled)


def __exec_ruleset(shell_ctx, uri, filename):
    json_mode_enabled = shell_ctx['json_mode_enabled']
    lsd_api = shell_ctx['lsd_api']

    try:
        with open(filename, 'r') as file:
            ruleset = file.read()
    except Exception as e:
        raise Exception("ERROR: could not read {0}".format(filename))

    result = lsd_api.create_ruleset(uri, ruleset)
    click.echo(result)
    print_json_result(result, json_mode_enabled)


def __h(_):
    shell_help = []
    shell_help.append(underline(colorize('LSD-CLI\n', rgb=0x71d1df)))
    shell_help.append("""
The following are the list of built-in command and leaplog sentences
& directives supported. Directives  (@prefix or @include) or explicit rules
(head :- body) are added to the current shell session context without actually
getting to lsd. Shell context is used on selects (?), write assert (++) and
write detract (--).\n\n""")

    for k, v in __commands.items():
        shell_help.append(colorize(v['name'], rgb=0x71d1df))
        shell_help.append('\n')
        shell_help.append('  ')
        shell_help.append(v['help'])
        shell_help.append('\n\n')

    click.echo_via_pager(''.join(shell_help))


def __c(_):
    clear()


def __ll(shell_ctx, filename):
    __exec_leaplog(shell_ctx, filename)


def __rs(shell_ctx, uri, filename):
    __exec_ruleset(shell_ctx, uri, filename)


def __lr(shell_ctx):
    json_mode_enabled = shell_ctx['json_mode_enabled']
    lsd_api = shell_ctx['lsd_api']
    result = lsd_api.rulesets()
    print_json_result(result, json_mode_enabled)


def __lc(shell_ctx):
    print_json_result(shell_ctx['prefix'])


def __e(shell_ctx):
    # TODO: imlement
    click.echo(colorize("e(): Not implemented!", rgb=0xdd5a25))


def __prefix(shell_ctx, params):
    match = re_prefix.match(params)

    if not match:
        raise Exception(
            'Error: invalid prefix, syntax "@prefix prefix: <uri>."')

    prefix = match.group(1)
    uri = match.group(2)
    shell_ctx['prefix_mapping'][prefix] = uri
    logging.debug(shell_ctx['prefix_mapping'])


def __include(shell_ctx, params):
   shell_ctx['includes'].append('@include: {}'.format(params))
   logging.debug(shell_ctx['includes'])


def __import(shell_ctx, params):
    # TODO: imlement
    click.echo(colorize("import(): Not implemented!", rgb=0xdd5a25))


def __export(shell_ctx, params):
    # TODO: imlement
    click.echo(colorize("export(): Not implemented!", rgb=0xdd5a25))


def __select(shell_ctx, params):
    prefix_mapping = shell_ctx['prefix_mapping']
    # TODO build rulset from shell_ctx['includes'] and shell_ctx['rules']
    ruleset = None
    prog = '%(params)s' % locals()
    result = shell_ctx['lsd_api'].leaplog(
        prog, prefix_mapping=prefix_mapping, ruleset=ruleset)
    json_mode_enabled = shell_ctx['json_mode_enabled']

    print_leaplog_result(result, json_mode_enabled)


def __write(shell_ctx, params):
    prefix_dirs = __prefix_dirs(shell_ctx)
    prog = '%(prefix_dirs)s\n\n%(params)s' % locals()
    result = shell_ctx['lsd_api'].leaplog(prog)
    json_mode_enabled = shell_ctx['json_mode_enabled']

    print_json_result(result, json_mode_enabled)


def __write_assert(shell_ctx, params):
    __write(shell_ctx, params)


def __write_retract(shell_ctx, params):
    __write(shell_ctx, params)


def __rule(shell_ctx, params):
    # TODO: imlement
    click.echo(colorize("rule: Not implemented!", rgb=0xdd5a25))


def __noc(shell_ctx):
    click.echo(colorize("Not implemented!", rgb=0xdd5a25))


# shell commands dispatch table
__commands = {
    'h': {'cmd': __h, 'name': 'h()', 'help': 'Prints this help.'},
    'c': {'cmd': __c, 'name': 'c()', 'help': 'Clears the terminal.'},
    'e': {'cmd': __e, 'name': 'e()', 'help': 'Edits current shell contex.'},
    'll': {'cmd': __ll, 'name': 'll(filename)',
           'help': 'Loads an execute a leaplog program from filename.'},
    'rs': {'cmd': __rs, 'name': 'rs(uri, filename)',
           'help': 'Loads a ruleset from filename to LSD with the given uri name.'},
    'lr': {'cmd': __lr, 'name': 'lr()', 'help': "Lists LSD defined rulesets."},
    'select': {'cmd': __select, 'name': '?().',
               'help': 'Perform a select on lsd.'},
    'write_assert': {'cmd': __write_assert, 'name': '++().',
                     'help': 'Write an assert on lsd.'},
    'write_retract': {'cmd': __write_retract, 'name': '--().',
                      'help': 'Write an retract on lsd.'},
    'rule': {'cmd': __rule, 'name': '().',
             'help': 'Partial rule definition for the current shell session.'},
    'export': {'cmd': __export, 'name': '@export <filename>.',
               'help': "Export the current shell session to <filename>."},
    '@prefix': {'cmd': __prefix, 'name': '@prefix prefix: <uri>.',
                'help': "Define a new url prefix to use during the shell session."},
    '@include': {'cmd': __include, 'name': '@include <uri>.',
                 'help': "Use the given ruleset during the shell session."},
    'import': {'cmd': __import, 'name': '@import <filename>.',
               'help': "Import the given <filename> to the shell session."},
    'export': {'cmd': __export, 'name': '@export <filename>.',
               'help': "Export the current shell session to <filename>."},
    'lc': {'cmd': __lc, 'name': 'lc(filename)',
           'help': "List url prefix definitions in the current shell session."}
}


def exec_cmd(shell_ctx, cmd, args):
    logging.debug('%s: %s', cmd, args)
    __commands[cmd]['cmd'](shell_ctx, *args)
