#!/usr/bin/env python3

import os
import re
import subprocess
import sys
import shutil
from pathlib import Path


def check_root(user_install):
    print('root? ', end='')
    if user_install:
        print('not needed')
        return True
    if os.geteuid() != 0:
        print('FAILED')
        print('re-run with `sudo` or use `--user` to install everything locally')
        print('if this is your machine use `sudo`; otherwise use `--user`')
        return False
    print('OK')
    return True


def check_tmux():
    print('tmux? ', end='')
    try:
        output = subprocess.check_output(['tmux', '-V']).decode().strip()
    except (OSError, subprocess.CalledProcessError):
        print('FAILED')
        return None
    # just get the major version number, it's all we need
    rv = int(re.match(r'tmux (\d+)', output).group(1))
    print(output.split(' ')[1])
    return rv


def check_zsh():
    print('zsh? ', end='')
    try:
        subprocess.check_output(['zsh', '--version']).decode().strip()
    except (OSError, subprocess.CalledProcessError):
        print('FAILED')
        return False
    print('OK')
    return True


def check_git():
    print('git? ', end='')
    try:
        subprocess.check_output(['git', '--version']).decode().strip()
    except (OSError, subprocess.CalledProcessError):
        print('FAILED')
        return False
    print('OK')
    return True


def install_tmux(base_dir, target_dir, user_install, tmux_version_major):
    print('- tmux')
    source_file = 'tmux.conf' if tmux_version_major >= 3 else 'tmux-legacy.conf'
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
        target_path,
        custom_config_path=custom_config_path,
        smartsplit=smartsplit_path,
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

    print('running some checks...')
    failures = False
    if not check_root(user_install):
        failures = True
    if not check_git():
        failures = True
    if not check_zsh():
        failures = True
    tmux_version_major = check_tmux()
    if tmux_version_major is None:
        failures = True

    if failures:
        print('some checks failed; fix the issues and try again')
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
    install_tmux(base_dir, target_dir, user_install, tmux_version_major)
    install_zsh(base_dir, target_dir, user_install)
    install_git(base_dir, target_dir, user_install)

    # TODO: offer to chsh
    # TODO: offer to set default editor to vim
    return 0


if __name__ == '__main__':
    sys.exit(main())
