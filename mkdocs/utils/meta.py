"""
Copyright (c) 2015, Waylan Limberg
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or other
materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may
be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

MultiMarkdown Meta-Data

Extracts, parses and transforms MultiMarkdown style data from documents.

"""


import re

import yaml

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader

#####################################################################
# Data Parser                                                       #
#####################################################################

YAML_RE = re.compile(r'^-{3}[ \t]*\n(.*?\n)(?:\.{3}|-{3})[ \t]*\n', re.UNICODE | re.DOTALL)
META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
META_MORE_RE = re.compile(r'^([ ]{4}|\t)(\s*)(?P<value>.*)')


def get_data(doc):
    """
    Extract meta-data from a text document.

    Returns a tuple of document and a data dict.
    """
    data = {}

    # First try YAML
    m = YAML_RE.match(doc)
    if m:
        try:
            data = yaml.load(m.group(1), SafeLoader)
            if isinstance(data, dict):
                doc = doc[m.end() :].lstrip('\n')
            else:
                data = {}
        except Exception:
            pass
        return doc, data

    # No YAML delimiters. Try MultiMarkdown style
    lines = doc.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    key = None
    while lines:
        line = lines.pop(0)

        if line.strip() == '':
            break  # blank line - done
        m1 = META_RE.match(line)
        if m1:
            key = m1.group('key').lower().strip()
            value = m1.group('value').strip()
            if key in data:
                data[key] += f' {value}'
            else:
                data[key] = value
        else:
            m2 = META_MORE_RE.match(line)
            if m2 and key:
                # Add another line to existing key
                data[key] += ' {}'.format(m2.group('value').strip())
            else:
                lines.insert(0, line)
                break  # no meta data - done
    return '\n'.join(lines).lstrip('\n'), data
