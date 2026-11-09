#!/bin/sh
set -eu
root=$(git rev-parse --show-toplevel)
cd "$root"
git config --local core.hooksPath .githooks
printf '%s\n' 'Installed local checker hooks. Set ZXUX_CHECKER_ZIP to your private ZIP outside Git.'
