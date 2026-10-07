#!/usr/bin/env bash
set +e
neuroprivacy diff --vendor vendor-d --since 2025-01-01
exit $?
