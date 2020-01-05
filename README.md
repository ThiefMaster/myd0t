# myd0t

This is an installer for my core dotfiles.

## Usage

The easiest way to install myd0t is to use the self-extracting installer
from the [releases][releases] page. It will automatically install any
dependencies that are missing.

You can also clone this repo (with `--recursive` since it's using git
submodules) and run `myd0t.py` yourself.

## Supported distributions

- Gentoo
- Ubuntu
- Debian
- CentOS
- Fedora
- Arch Linux

Use the latest (stable) version, I do not care about ancient systems.

Other distributions should work fine, but some automatisms won't:

- missing packages need to be installed manually
- the global default editor cannot be set automatically
- you need to update the global vimrc manually

Since adding another distribution is easy, feel free to open an issue or
even send a PR if your favorite distribution is not listed.

## Features

At some point I'll hopefully write something more detailed here... for now
this list is all you'll get:

- tmux config
- zsh config (see [its repo][zsh-config] for details)
- git config with useful aliases
- vim config, and setting vim as the default editor
- gnome terminal config (if you use a GUI on your system)

And if you are a new colleague of me who I conviced to use this, I'll just
show you in person why using my dotfiles is a good idea, especially if you
don't already have your own fancy configs!

## Customization

Of course you can always fork this repo - that lets you track your
customizations in Git and easily share them between machines.

But if you just want to add some extra configuration on a single machine,
simply use the user config files which are provided for tmux and zsh. The
paths are displayed during installation, and these files are preserved even
when re-running the myd0t installer.


[releases]: https://github.com/ThiefMaster/myd0t/releases
[zsh-config]: https://github.com/ThiefMaster/zsh-config
