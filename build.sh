#!/bin/bash
set -euxo pipefail

if [ -d "build" ]; then
    rm -rf "build"
fi

mkdir build
mkdir build/plots
sh download_data.sh
python main.py
cp static/* build/
