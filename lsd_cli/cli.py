from __future__ import unicode_literals

import re
import traceback
from os.path import expanduser

import pkg_resources  # part of setuptools
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
from xtermcolor import colorize

from lsd_cli import lsd
from lsd_cli.lsd import Lsd
from lsd_cli.print_utils import *
from lsd_cli.shell_cmd import exec_cmd

version = pkg_resources.require("lsd-cli")[0].version
vi_mode_enabled = False
json_mode_enabled = False
click.disable_unicode_literals_warning = True
home = expanduser("~")
history = FileHistory(home + '/.lsd-cli_history')
auto_suggest = AutoSuggestFromHistory()
debug = False


def get_bottom_toolbar_tokens(cli):
    text = 'Vi' if vi_mode_enabled else 'Emacs'
    output = "Json" if json_mode_enabled else 'Tabular'

    return [(Token.Toolbar, ' lsd-cli v{0}. '.format(version)),
            (Token.Toolbar, ' h() Help '),
            (Token.Toolbar, ' [F4] %s ' % text),
            (Token.Toolbar, ' [F5] %s ' % output),
            (Token.Toolbar, ' (%0.3f ms, %d tuples) ' % (lsd.timer, lsd.tuples))]


def get_title():
    return 'lsd-cli v{0}'.format(version)


style = style_from_dict({
    Token.Prompt: '#ffc853',
    Token.Toolbar: '#ffffff bg:#298594'
})


def __process_cmd(shell_ctx, cmd):
    prog = re.compile(r'(\w+)\((.*)\)')
    match = prog.match(cmd)

    if not match:  # no matching command then interpreted as query or fact
        prefixes = ''

        for prefix, uri in shell_ctx['prefix'].items():
            prefixes = prefixes + '@prefix {}: {}.\n'.format(prefix, uri)

        result = shell_ctx['lsd_api'].leaplog(prefixes + '\n' + cmd)
        print_leaplog_result(result, json_mode_enabled)
    else:
        cmd = match.group(1)
        params = match.group(2)

        try:
            exec_cmd(shell_ctx, cmd, params)
        except Exception as e:
            click.echo(colorize(e, rgb=0xdd5a25))
            if debug:
                traceback.print_exc()


@click.command()
@click.option('--host', '-h', default='localhost', help='LSD host.')
@click.option('--port', '-p', default=10018, type=int, help='LSD port.')
@click.argument('tenant', default='leapsight', required=False)
def main(tenant, host, port):
    """Leapsight Semantic Dataspace Command Line Tool"""
    # Create a set of key bindings that have Vi mode enabled if the
    # ``vi_mode_enabled`` is True.
    try:
        lsd_api = Lsd(tenant, host, port)
    except Exception:
        click.echo('ERROR: connection refused {0}:{1}({2})'.format(
            host, port, tenant))
        exit(1)

    manager = KeyBindingManager.for_prompt(
        enable_vi_mode=Condition(lambda cli: vi_mode_enabled))

    # Add an additional key binding for toggling this flag.
    @manager.registry.add_binding(Keys.F4)
    def _f4(_event):
        """ Toggle between Emacs and Vi mode. """
        global vi_mode_enabled
        vi_mode_enabled = not vi_mode_enabled

    # Add an additional key binding for toggling this flag.
    @manager.registry.add_binding(Keys.F5)
    def _f5(_event):
        """ Toggle between Json and Tabular mode. """
        global json_mode_enabled
        json_mode_enabled = not json_mode_enabled

    click.clear()
    click.echo(colorize("""
Welcome to    _/         _/_/_/_/    _/_/_/
             _/         _/          _/    _/
            _/         _/_/_/_/    _/    _/
           _/               _/    _/    _/
          _/_/_/_/   _/_/_/_/    _/_/_/      command line interface!
"""
                        , rgb=0x2cb9d0))

    shell_ctx = {
            'lsd_api': lsd_api,
            'json_mode_enabled': json_mode_enabled,
            'prefix': {}
        }

    while True:
        cmd = prompt('lsd> ', history=history, auto_suggest=auto_suggest,
                     get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                     style=style, vi_mode=vi_mode_enabled,
                     key_bindings_registry=manager.registry,
                     get_title=get_title)
        try:
            if cmd:
                __process_cmd(shell_ctx, cmd)
        except Exception as e:
            click.echo(e)
