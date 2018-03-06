#!/usr/bin/sh
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory

mkdir -p $PREFIX/lib/a-prime
cp $SRC_DIR/run_aprime.bash $PREFIX/lib/a-prime/run_aprime.bash
mkdir -p $PREFIX/bin
cp $SRC_DIR/python/get_aprime_template $PREFIX/bin/get_aprime_template

for subdir in bash_scripts images python
do
    dest_path=$PREFIX/lib/a-prime/${subdir}
    mkdir -p $dest_path
    cp $SRC_DIR/${subdir}/* $dest_path
done
