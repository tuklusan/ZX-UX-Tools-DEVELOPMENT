"""Build integration, cassette payload and transplanted-SDK smoke tests."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

SRC = Path(__file__).resolve().parents[1]
ROOT = SRC.parent
REF_ROOT = Path(os.environ.get('ZXUX_REFERENCE_ROOT',
                               str(ROOT / 'reference/ZX-UX')))
SDK = REF_ROOT / 'src/zx-ux-sdk'
TAPE = REF_ROOT / 'build/out/ZX-UX.tzx'
TOOL = SRC / 'zx-ux-sdk/tools/forthbuild.py'
spec = importlib.util.spec_from_file_location('forthbuild', TOOL)
forthbuild = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forthbuild)


def test_build_and_run_transplanted_sdk(tmp_path):
    staged = tmp_path / 'sdk'
    shutil.copytree(SDK, staged, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(SRC / 'zx-ux-sdk', staged, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__'))
    programs = tmp_path / 'programs'
    programs.mkdir()
    shutil.copy2(SRC / 'assets/forth-src/examples/hello.fth', programs)
    dest = tmp_path / 'built'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    # Exercise sibling-SDK discovery from a working directory unrelated to it.
    env.pop('ZXUX_SDK', None)
    result = subprocess.run([sys.executable, '-B', str(staged / 'tools/forthbuild.py'),
                             '--stack', '768', str(programs), str(dest)],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    sys.path.insert(0, str(SDK))
    import rld
    import rtap
    ssx = dest / 'ssx/hello.ssx'
    data = ssx.read_bytes()
    assert rld.parse_ssx(data)['stack'] == 768
    _, blocks = rtap.tzx_blocks((dest / 'tzx/hello.tzx').read_bytes())
    assert blocks[1][1][1:-1] == data
    assert 'program  /dev/cassette/hello' in '\n'.join(rtap.list_blocks([b for _, b in blocks]))
    if not TAPE.exists():
        pytest.fail('The existing ZX-UX boot tape is required for end-to-end verification')
    run = subprocess.run([sys.executable, '-B', str(staged / 'rvm.py'), '--headless',
                          '--no-cache', '--text', '--frames', '12000', '--system', str(TAPE), str(ssx)],
                         cwd=tmp_path, env=env, capture_output=True, text=True, timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr
    assert 'HELLO ZX-UX' in run.stdout


@pytest.mark.parametrize('names,match', [
    (['a/hello.fth', 'b/hello.fth'], 'Duplicate'),
    (['toolongname.fth'], 'cassette program name'),
    ([], 'No .fth sources'),
])
def test_reject_source_selection_before_output(tmp_path, names, match):
    programs = tmp_path / 'sources'
    programs.mkdir()
    for name in names:
        source = programs / name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('1 .', encoding='utf-8')
    dest = tmp_path / 'out'
    with pytest.raises(ValueError, match=match):
        forthbuild.build(SDK, programs, dest)
    assert not dest.exists()


def test_compile_error_reports_source(tmp_path):
    programs = tmp_path / 'sources'
    programs.mkdir()
    (programs / 'bad.fth').write_text('nosuchword', encoding='utf-8')
    with pytest.raises(ValueError, match='bad.fth.*nosuchword'):
        forthbuild.build(SDK, programs, tmp_path / 'out')
