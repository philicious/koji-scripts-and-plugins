## Koji Plugins and Scripts ##

This is a compilation of scripts and plugins for automation with Koji
For more info, see head comment in code files.

### sigul_sign ###

Koji-Plugin to auto-sign built packages with sigul.

### mash_and_spacewalk_sync ###

Koji-Plugin + Script that mashes your packages after being tagged to testing. Then calls Spacewalk to sync the repo.

(This spawns mash / spacewalk to background detached)

Can be combined with sigul_sign

### mash_and_spacewalk_sync_task_handler ###

Koji-Builder-Plugin (Kojid). Same as aboth but as real Koji tasks with result/log feedback

You should take this one.

### koji-github-webhook ###

Enables auto-building in Koji after committing updates to spec/Makefile to Github with certain flags in commit message.
