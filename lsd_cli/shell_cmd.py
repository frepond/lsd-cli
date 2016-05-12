from xtermcolor import colorize

from lsd_cli.print_utils import *


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
    shell_help.append("""The following are the list of built-in command. If no command is entered then the
input is interpreted as a datalog sentence.\n\n""")

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


def __cx(shell_ctx, prefix, uri):
    shell_ctx['prefix'][prefix] = uri


def __lc(shell_ctx):
    print_json_result(shell_ctx['prefix'])


def __noc(shell_ctx):
    click.echo(colorize("Not implemented!", rgb=0xdd5a25))


# shell commands dispatch table
__commands = {
    'h': {'cmd': __h, 'name': 'h()', 'help': 'Prints this help.'},
    'c': {'cmd': __c, 'name': 'c()', 'help': 'Clears the terminal.'},
    'll': {'cmd': __ll, 'name': 'll(filename)',
           'help': 'Loads an execute a leaplog program from filename.'},
    'rs': {'cmd': __rs, 'name': 'rs(uri, filename)',
           'help': 'Loads a ruleset from filename to LSD with the given uri name.'},
    'lr': {'cmd': __lr, 'name': 'lr()', 'help': "Lists LSD defined rulesets."},
    'cx': {'cmd': __cx, 'name': 'cx(prefix, uri)',
           'help': "Define a new url prefix to use during the shell session."},
    'lc': {'cmd': __lc, 'name': 'lc(filename)',
           'help': "List url prefix definitions in the current shell session."}
}


def exec_cmd(shell_ctx, cmd, param_str):
    if param_str:
        args = [x.strip() for x in param_str.split(',')]
    else:
        args = []

    __commands[cmd]['cmd'](shell_ctx, *args)
