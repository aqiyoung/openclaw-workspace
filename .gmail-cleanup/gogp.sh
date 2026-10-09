#!/bin/bash
# Wrapper around gog that injects the proxy.
export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
exec gog "$@"
