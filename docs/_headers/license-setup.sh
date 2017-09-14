#!/usr/bin/env bash
# Copyright (c) 2015,2016, UT-BATTELLE, LLC
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

SOURCE_DIR="../.."

CURRENT="Copyright (c)"

ALWAYS_IGNORE=(-not -path "*.git*" -not -path "*docs/*" -not -iname "setup_*" -not -path "*python/MPAS-Analysis/*" \
               -not -iname "MANIFEST.in")

FILE_IGNORE=(-not -iname "*.md" -not -iname "*.json" -not -iname "*.txt" \
             -not -iname "*.png" -not -iname "*.jpg" -not -iname "*.svg" \
             -not -iname "config.*" -not -iname "README" -not -iname "*.nc"\
             -not -iname "streams.*" -not -iname "*.ocean" -not -iname "*.pyc" \
             -not -iname "*.sl" -not -iname "*.ps1" -not -iname "*.yml"    )

PYTHON_IGNORE=(-not -iname "__init__.py" -not -iname "colormaps.py"  \
               -not -path "*dist/*" -not -path "*.egg-info/*") 

CSS_IGNORE=(-not -iname "jquery-ui.min.css")
