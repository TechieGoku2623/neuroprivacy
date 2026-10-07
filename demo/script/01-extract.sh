#!/usr/bin/env bash
set +e
neuroprivacy extract --doc data/sample/vendor-a.html --summary
exit $?
