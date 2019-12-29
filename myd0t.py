#!/usr/bin/env python3

import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from colorama_ansi import Fore, clear_line

DISTROS = {
    'gentoo': {
        'install': ['emerge', '-avn'],
        'packages': {
            'git': 'dev-vcs/git',
            'zsh': 'app-shells/zsh',
            'tmux': 'app-misc/tmux',
        },
    },
    'arch': {
        'install': ['pacman', '-S'],
        'packages': {'git': 'git', 'zsh': 'zsh', 'tmux': 'tmux',},
    },
    'fedora': {
        'install': ['dnf', 'install'],
        'packages': {'git': 'git', 'zsh': 'zsh', 'tmux': 'tmux',},
    },
    'centos': {
        'install': ['yum', 'install'],
        'packages': {'git': 'git', 'zsh': 'zsh', 'tmux': 'tmux',},
    },
    'ubuntu': {
        'install': ['apt', 'install'],
        'packages': {'git': 'git', 'zsh': 'zsh', 'tmux': 'tmux',},
    },
    'debian': {
        'install': ['apt', 'install'],
        'packages': {'git': 'git', 'zsh': 'zsh', 'tmux': 'tmux',},
    },
}


def guess_distro():
    if os.path.exists('/etc/os-release'):
        return subprocess.check_output(
            ['sh', '-c', '. /etc/os-release; echo -n $ID']
        ).decode()
    elif os.path.exists('/etc/arch-release'):
        # at least the docker image doesn't have /etc/os-release
        return 'arch'


def check_programs(distro, programs):
    missing = {p for p in programs if not shutil.which(p)}
    colors = {p: Fore.LIGHTRED if p in missing else Fore.LIGHTGREEN for p in programs}
    result = {f'{colors[p]}{p}{Fore.RESET}' for p in programs}
    print(f'required packages: {", ".join(sorted(result))}')
    if not missing:
        return True
    try:
        install_packages(distro, missing)
    except KeyboardInterrupt:
        clear_line()
        print(f'\r{Fore.LIGHTRED}package installation aborted{Fore.RESET}')
        return False
    else:
        return check_programs(distro, programs)


def install_packages(distro, packages):
    try:
        distro_data = DISTROS[distro]
    except KeyError:
        print('please install the following packages:\n')
        for p in packages:
            print(f' - {p}')
        print()
        input('press ENTER once you are done\n')
        return
    distro_packages = [distro_data['packages'][x] for x in packages]
    args = [*distro_data['install'], *distro_packages]
    cmdline = ' '.join(map(shlex.quote, args))
    if os.geteuid() != 0:
        print('run the following command as root to install missing packages:\n')
        print(f'    {Fore.LIGHTWHITE}{cmdline}{Fore.RESET}')
        print()
        input('press ENTER once you are done\n')
    else:
        print(
            f'i will run {Fore.LIGHTWHITE}{cmdline}{Fore.RESET} to install missing packages'
        )
        input('press ENTER to continue\n')
        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            print('non-zero exit code; installation likely failed')


def check_root(user_install):
    print('root? ', end='')
    if user_install:
        print(f'{Fore.YELLOW}not needed{Fore.RESET}')
        return True
    if os.geteuid() != 0:
        print(f'{Fore.LIGHTRED}FAILED{Fore.RESET}')
        print('re-run with `sudo` or use `--user` to install everything locally')
        print('if this is your machine use `sudo`; otherwise use `--user`')
        return False
    print(f'{Fore.LIGHTGREEN}OK{Fore.RESET}')
    return True


def is_tmux_2():
    try:
        output = subprocess.check_output(['tmux', '-V']).decode().strip()
    except (OSError, subprocess.CalledProcessError):
        print('FAILED')
        return None
    return re.match(r'tmux (\d+)', output).group(1) == '2'


def install_tmux(base_dir, target_dir, user_install):
    print('- tmux')
    source_file = 'tmux.conf' if not is_tmux_2() else 'tmux-legacy.conf'
    target_path = target_dir / 'tmux.conf'
    tmux_config_path = Path(
        '~/.tmux.conf' if user_install else '/etc/tmux.conf'
    ).expanduser()
    # copy to myd0t config dir
    shutil.copy(base_dir / 'tmux' / source_file, target_path)
    # delete existing config (hopefully not something the user still needed)
    if tmux_config_path.exists() or tmux_config_path.is_symlink():
        tmux_config_path.unlink()
    # link to the config file inside the myd0t config dir
    tmux_config_path.symlink_to(target_path)
    # create an override file in case the user wants to add more stuff
    custom_config_path = target_dir / 'tmux.user.conf'
    if not custom_config_path.exists():
        custom_config_path.touch()
    smartsplit_path = target_dir / 'bin' / 'tmux-smartsplit'
    replace_placeholders(
        target_path, custom_config_path=custom_config_path, smartsplit=smartsplit_path,
    )


def install_zsh(base_dir, target_dir, user_install):
    print('- zsh')
    target_path = target_dir / 'zsh'
    tm_config_path = target_path / 'config-tm'
    if user_install:
        zshrc_path = Path('~/.zshrc').expanduser()
        zshenv_path = None
        try:
            if zshrc_path.exists() and not zshrc_path.is_symlink():
                input(
                    '~/.zshrc will be overwritten. Press ENTER to confirm, CTRL+C to abort\n'
                )
        except KeyboardInterrupt:
            print('\rzsh setup aborted')
            return
    elif Path('/etc/zsh').exists():
        zshrc_path = Path('/etc/zsh/zshrc')
        zshenv_path = Path('/etc/zsh/zshenv')
    else:
        zshrc_path = Path('/etc/zshrc')
        zshenv_path = Path('/etc/zshenv')
    # delete previously-copied config since copytree fails if target dirs exist
    if tm_config_path.exists():
        shutil.rmtree(tm_config_path)
    # delete old config (hopefully not something the user still needed)
    if zshrc_path.exists() or zshrc_path.is_symlink():
        zshrc_path.unlink()
    if zshenv_path and (zshenv_path.exists() or zshenv_path.is_symlink()):
        zshenv_path.unlink()
    # copy to myd0t config dir
    shutil.copytree(
        base_dir / 'zsh' / 'config-tm',
        tm_config_path,
        ignore=lambda p, n: {'.git', '.gitignore', '.gitmodules', 'README.md'},
    )
    # link to our config files
    zshrc_path.symlink_to(target_path / 'zshrc')
    if zshenv_path:
        zshenv_path.symlink_to(target_path / 'zshenv')
    # create override files in case the user wants to add more stuff
    custom_zshrc_path = target_path / 'zshrc.user'
    if not custom_zshrc_path.exists():
        custom_zshrc_path.touch()
    if zshenv_path:
        custom_zshenv_path = target_path / 'zshenv.user'
        if not custom_zshenv_path.exists():
            custom_zshenv_path.touch()
    # copy the configs our symlinks point to
    replace_placeholders(
        target_path / 'zshrc',
        base_dir / 'zsh' / 'zshrc',
        zshrc=tm_config_path / '.zshrc',
        custom_zshrc=custom_zshrc_path,
    )
    if zshenv_path:
        replace_placeholders(
            target_path / 'zshenv',
            base_dir / 'zsh' / 'zshenv',
            zshenv=tm_config_path / '.zshenv',
            custom_zshenv=custom_zshenv_path,
        )


def install_git(base_dir, target_dir, user_install):
    print('- git')
    target_file_path = target_dir / 'gitconfig'
    git_config_arg = '--global' if user_install else '--system'
    smartless_path = target_dir / 'bin' / 'smartless'
    replace_placeholders(
        target_file_path, base_dir / 'gitconfig', smartless=smartless_path
    )
    subprocess.check_call(
        [
            'git',
            'config',
            git_config_arg,
            '--replace-all',
            'include.path',
            str(target_file_path),
            f'^{re.escape(str(target_file_path))}$',
        ]
    )


def replace_placeholders(file: Path, infile: Path = None, **placeholders):
    data = (infile or file).read_text()
    for name, value in placeholders.items():
        data = data.replace(f'@@{name}@@', str(value))
    file.write_text(data)


def main():
    args = sys.argv[1:]
    user_install = '--user' in args
    base_dir = Path(__file__).absolute().parent

    distro = guess_distro()
    if distro not in DISTROS:
        print(f'unknown distro: {distro}; cannot auto-install packages')

    print('running some checks...')
    if not check_root(user_install):
        return 1
    if not check_programs(distro, ['git', 'zsh', 'tmux']):
        return 1

    print()
    if user_install:
        target_dir = Path('~/.config/myd0t').expanduser()
    else:
        # make sure files we create/copy are world-readable
        os.umask(0o022)
        target_dir = Path('/etc/myd0t')
    print(f'installing to {target_dir}')
    target_dir.mkdir(parents=True, exist_ok=True)

    # bin is not tied to any specific application (even though it could be),
    # so we just copy the whole thing beforehand
    target_bin_path = target_dir / 'bin'
    if target_bin_path.exists():
        shutil.rmtree(target_bin_path)
    shutil.copytree(base_dir / 'bin', target_dir / 'bin')

    print('installing configs...')
    install_tmux(base_dir, target_dir, user_install)
    install_zsh(base_dir, target_dir, user_install)
    install_git(base_dir, target_dir, user_install)

    # TODO: offer to chsh
    # TODO: offer to set default editor to vim
    return 0


if __name__ == '__main__':
    sys.exit(main())
