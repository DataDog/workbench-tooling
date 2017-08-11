#!/bin/sh
# This is sourced before the host's profile.sh
# It can be used to add common envvars and aliases

export PATH=/opt/workbench/host/common/bin/:$PATH

if hash workbench 2>/dev/null; then
    eval "$(_WORKBENCH_COMPLETE=source workbench)"
    alias wb=workbench
    alias wbr='workbench recipe'
fi
