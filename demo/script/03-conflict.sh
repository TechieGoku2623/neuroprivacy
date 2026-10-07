#!/usr/bin/env bash
set +e
neuroprivacy audit --vendor vendor-c --show-conflicts --summary
exit $?
