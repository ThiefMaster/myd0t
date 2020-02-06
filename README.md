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

## Cheat Sheet

Well, about writing something more detailed.. still not going to happen. But
for those who never used tmux or zsh there's still some explaining needed,
and pointing to its docs is too lazy even for me, not to mention that the zsh
docs are huge and somewhat hard to navigate unless you spend a weekend on
familiarizing yourself with the shell (and even then you probably don't remember
much except what you use all the time).

### tmux

`tmux` is a (better) replacement for tabs and tab-like functionality in your GUI
terminal emulator. This is why myd0t actually removes the key bindings to create
new tabs in the terminal or switch tabs there.

The "prefix" key for tmux commands is CTRL+a (often also written as `^a` or
`C-a`), unless you are nesting sessions (usually a root shell running tmux
inside a non-root tmux window), in which case the prefix is `^b` instead.

So if a tmux command itself also requires the CTRL key, you do not need to
release it and press it again (modifier keys like CTRL, SHIFT and ALT are
not sent past the terminal at all, they only modify what gets sent when
pressing another key). For example, `^a` is the bining for `last-window`,
so to switch between the current window and the previous one, you can simply
press CTRL and then hit `a` twice.

On the other hand, if a command *does not* use the CTRL key, make sure to
release both `CTRL` and `a` before pressing the actual command's key.

The most important tmux key bindings are:

- `c` - create a new window
- `,` - rename the current window (useful for ones you keep for a long time)
- `"` - split the current window/pane vertically
- `%` - split the current window/pane horizontally
- `q` - show the pane indexes; you have 1 second to press the corresponding number
  if you want to switch to it
- `z` - zoom in the current pane; do it again if want to zoom out
- cursor keys - switch to the pane that's positioned next to the current one in
  the direction of the key you used
- CTRL + cursor keys - resize the current pane

### zsh

#### The shell is the lazy user's friend

There are some very useful aliases, which save you typing:

- `..` will go up one level (shortcut for `cd ..`)
- `...` will go up two levels instead of one
- `cd` will go to your home directory
- `^l` clears your windows (no need to write `clear`)
- `^d` closes your shell (or aborts an input prompt); you'll never need to write
  `exit` in your shell

You **do not** need to `cd` to other directories to view/edit a file or list their
contents. Just like in any other shell, `ll ../foo` etc. work justfine and allow you
to stay in the directory you are in. If you do change directories because you need
to do more, then `cd -` will bring you back to the previous directory. You can also
tab-complete right after entering `cd -` to select one of the other directories you
have been in before.

If you want to run a command you used before, `^r` will enter reverse history search.
Pressing `^r` again after entering a search term will go back through all matching
entries; if you went too far you can also go forward again using `^s`. Wildcards can
be used, so if you want to search for a command using such chars you need to escape
them with a backslash.

zsh has very powerful tab completion. To kill a single process by name, you can write
`kill whatever` and then tab-complete; this will show you a process list from which
you can then select the PID to kill.

It can also complete partial paths. Let's say you want to do to `~/dev/myapp/src`.
Instead of typing `cd ~/dev/myapp/src` (or recalling it from history), you can
simply write `cd ~/d/m/s` and tab-complete. If there's only one match, it'll be
replaced with the full path. But this example probably wasn't the best one, because
changing to your main project's directory is something you probably DO want to recall
from history!

#### Key Bindings

The shell has lots of key bindings, but some are much more common than others.

- `CTRL+left/right` - jump one word left/right
- `ALT+left/right` - jump one arg left/right (honors quotes/backslashes)
- `ALT+del/backspace` - delete one arg to the right/left (doesn't work in all terminals)
- `^w` - delete the word on the left of the cursor
- `^f` - delete until the previous slash (great for paths)
- `^-` - undo
- `ALT+q` - stash away whatever command you just entered for one round. That lets you run
  one command, and then the old one reappears. This is great if you entered a command
  and then realize that you needed to do something else first. You can use this shortcut
  as often as you want, but maybe at some point you really do want to execute that original
  command?

#### autovenv

If you do Python development, you really want to use the auto-venv functionality
which automatically loads a virtualenv based on the directory you are in. It is
configured by creating a file `~/.autovenv` with content like this:

```
DEFAULT                 ~/.myenv
/tmp                    IGNORE
~/dev/myproject         env
~/dev/otherproject      .venv
```

This autovenv config will result in the following behavior:

- by default, the virtualenv `~/.myenv` is loaded (you need to create it if you plan
  to use the config above)
- if you are inside `~/dev/myproject` (or any subdirectory of it), `~/dev/myproject/env`
  will be loaded
- if you are somewhere inside `~/dev/otherproject`, then the venv from `.venv` will be
  loaded
- if you are inside `/tmp`, then the functionality is completely disabled, this means
  that whatever virtualenv was active remains active, and if you manually activate some
  other virtualenv, changing directories won't deactivate/activate any other virtualenv.

### vim

You hopefully know some basic vimming, but if not: ESC switches from insert/replace
mode to command mode, and then you can use `:x` to save+exit, or `:q!` to just exit
without saving. `/foo` will search for `foo`, and `:%s/old/new/g` will replace all
occurrences or `old` with `new` in the whole file.

You should also *really* use vim when writing git commit messages, as it highlights
overly long first lines or a non-empty second lines in a very notable way. Again,
myd0t configures vim as your default editor so git will use it as well.

## Customization

Of course you can always fork this repo - that lets you track your
customizations in Git and easily share them between machines.

But if you just want to add some extra configuration on a single machine,
simply use the user config files which are provided for tmux and zsh. The
paths are displayed during installation, and these files are preserved even
when re-running the myd0t installer.


[releases]: https://github.com/ThiefMaster/myd0t/releases
[zsh-config]: https://github.com/ThiefMaster/zsh-config
