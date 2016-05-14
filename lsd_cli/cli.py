from __future__ import unicode_literals

import logging
import re
import traceback
from os.path import expanduser

import pkg_resources  # part of setuptools

from lsd_cli import lsd
from lsd_cli.lsd import Lsd
from lsd_cli.print_utils import *
from lsd_cli.shell_cmd import process_input, _load_context
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
from xtermcolor import colorize

version = pkg_resources.require("lsd-cli")[0].version
vi_mode_enabled = False
json_mode_enabled = False
click.disable_unicode_literals_warning = True
home = expanduser("~")
history = FileHistory(home + '/.lsd-cli_history')
cli_rc = home + '/.lsdclirc'
auto_suggest = AutoSuggestFromHistory()


def get_bottom_toolbar_tokens(cli):
    text = 'Vi' if vi_mode_enabled else 'Emacs'
    output = "Json" if json_mode_enabled else 'Tabular'

    return [(Token.Toolbar, ' lsd-cli v{0}. '.format(version)),
            (Token.Toolbar, ' h() Help '),
            (Token.Toolbar, ' [F4] %s ' % text),
            (Token.Toolbar, ' [F5] %s ' % output),
            (Token.Toolbar, ' (%0.2f ms/%0.2f ms, %d rows) '
             % (lsd.cli_time, lsd.lsd_time, lsd.tuples))]


def get_title():
    return 'lsd-cli v{0}'.format(version)


style = style_from_dict({
    Token.Prompt: '#ffc853',
    Token.Toolbar: '#ffffff bg:#298594'
})


@click.command()
@click.option('--host', '-h', default='localhost', help='LSD host.', show_default=True)
@click.option('--port', '-p', default=10018, type=int, help='LSD port.', show_default=True)
@click.option('--verbose', '-v', is_flag=True)
@click.argument('tenant', default='leapsight', required=False)
def main(tenant, host, port, verbose):
    """Leapsight Semantic Dataspace Command Line Tool"""
    # Create a set of key bindings that have Vi mode enabled if the
    # ``vi_mode_enabled`` is True.
    if verbose:
        format = '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=format)

    # try to connect to lsd
    try:
        lsd_api = Lsd(tenant, host, port)
    except Exception as e:
        click.echo('ERROR: connection refused {0}:{1}({2})'.format(
            host, port, tenant))
        logging.debug(e)

        exit(1)

    manager = KeyBindingManager.for_prompt(
        enable_vi_mode=Condition(lambda cli: vi_mode_enabled))

    # add an additional key binding for toggling this flag.
    @manager.registry.add_binding(Keys.F4)
    def _f4(_event):
        """ Toggle between Emacs and Vi mode. """
        global vi_mode_enabled
        vi_mode_enabled = not vi_mode_enabled

    # add an additional key binding for toggling this flag.
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

    ll_completer = WordCompleter(
        ['@prefix prefix: <uri>.', '@include <uri>.', '++().', '--().', '+().', '-().',
         '?().', 'import(filename)', 'export(filename)', 'h()', 'e()'])
    shell_ctx = {
        'lsd_api': lsd_api,
        'json_mode_enabled': json_mode_enabled,
        'prefix_mapping': {},
        'rules': [],
        'includes': []
    }

    # load init file ~/lsd-cli.rc
    try:
        _load_context(shell_ctx, cli_rc)
    except:
        pass

    while True:
        input = prompt('lsd> ', history=history, auto_suggest=auto_suggest,
                       get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                       style=style, vi_mode=vi_mode_enabled,
                       key_bindings_registry=manager.registry,
                       get_title=get_title, completer=ll_completer)
        try:
            if input:
                process_input(shell_ctx, input.strip())
        except Exception as e:
            click.echo(colorize(e, rgb=0xdd5a25))
            logging.debug(traceback.print_exc())
