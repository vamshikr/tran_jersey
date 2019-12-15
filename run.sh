#!/bin/bash
set -o nounset
set -o errexit
set -o pipefail


gunicorn tran_jersey.app:init_app -k eventlet --workers 1 --bind "0.0.0.0:8080" --worker-class "aiohttp.GunicornUVLoopWebWorker"
