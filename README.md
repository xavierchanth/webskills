# Web Skills

## What is this repo?

It is an abstraction over other skills I've found / want to try.
Rather than duplicating them and contributing to the slop, I've put together
a git submodules + symlink generator which allows me to maintain my own list of
skills.

These skills are not well audited yet, and this repo is experimental.
USE AT YOUR OWN RISK.

## Installation / Usage

The normal skills command is not symlink / module aware so you must pull it
locally:

### Clone it to a temporary directory

```sh
# Download to temp dir
git clone https://github.com/xavierchanth/webskills /tmp/webskills
# Install (doesn't touch anything outside of it's own temp dir)
(set -e; cd /tmp/webskills/; ./link_skills.py);
```

### Use skills cli to reference the local path

```sh
bunx skills add /tmp/webskills
```
