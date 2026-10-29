"""Run the imported F83 numerical-analysis corpus on the real ZX-UX rvm."""
import csv
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
PROJ = SRC.parent
CORPUS = SRC / 'assets/forth-src/numerical-analysis'
REF_ROOT = Path(os.environ.get('ZXUX_REFERENCE_ROOT',
                               str(PROJ / 'reference/ZX-UX')))
REF_SDK = REF_ROOT / 'src/zx-ux-sdk'
TAPE = REF_ROOT / 'build/out/ZX-UX.tzx'
os.environ.setdefault('ZXUX_SDK', str(REF_SDK))
sys.path.insert(0, str(SRC / 'zx-ux-sdk'))
from rfc import driver                 # noqa: E402

needs_tape = pytest.mark.skipif(not TAPE.exists(),
                                reason='ZX-UX system tape not built')


def _expected_lines():
    path = CORPUS / 'original/F83_Z80_SUITE/reference/EXPECTED.csv'
    result = {}
    with path.open(newline='', encoding='ascii') as stream:
        for row in csv.DictReader(stream):
            result.setdefault(row['program'], []).append(row['text'].strip())
    return result


@needs_tape
def test_twenty_numerical_analysis_demos_on_rvm(tmp_path):
    sources = sorted(CORPUS.glob('*.fth'))
    expected = _expected_lines()
    assert len(sources) == 20
    assert set(path.stem.upper() for path in sources) == set(expected)

    for source in sources:
        output = tmp_path / (source.stem + '.ssx')
        assert driver.main([str(source), '-o', str(output)]) == 0
        run = subprocess.run(
            [sys.executable, str(REF_SDK / 'rvm.py'), '--headless', '--no-cache',
             '--text', '--frames', '12000', '--system', str(TAPE), str(output)],
            capture_output=True, text=True, timeout=180)
        text = run.stdout + '\n' + run.stderr
        assert run.returncode == 0, text
        status = re.search(r'^rvm: .*: (exit 0 \(exit\))', text, re.MULTILINE)
        assert status, text
        normalized = ' '.join(text.split())
        for line in expected[source.stem.upper()]:
            assert ' '.join(line.split()) in normalized, (source.name, line, text)
