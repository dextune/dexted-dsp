#!/usr/bin/env python3
"""Check installed CMake exports and real C ABI consumption in a fresh build tree.

Uses the host compiler/toolchain already configured by the caller. Does not
publish anything or access the network. Runtime DLL lookup is explicit.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def run(*args: str, env=None) -> None:
    subprocess.run(list(args),check=True,env=env)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',type=Path,default=ROOT/'build')
    args=parser.parse_args()
    # Windows MSBuild/vctip can briefly retain handles after a successful CTest.
    # Best-effort temporary cleanup is safe on disposable CI runners; test errors
    # still propagate via subprocess.check=True.
    with tempfile.TemporaryDirectory(prefix='dexted-consumer-',
                                     ignore_cleanup_errors=(os.name == 'nt')) as temporary:
        folder=Path(temporary).resolve()
        prefix=folder/'install'
        build=folder/'consumer-build'
        run('cmake','--install',str(args.build_dir.resolve()),'--config','Release','--prefix',str(prefix))
        options=['cmake','-S',str(ROOT/'examples/native_consumer'),'-B',str(build),
                 '-DCMAKE_PREFIX_PATH='+str(prefix),'-DCMAKE_BUILD_TYPE=Release']
        vcpkg=os.environ.get('VCPKG_INSTALLATION_ROOT')
        if sys.platform=='win32' and vcpkg:
            options.extend(['-A','x64',
                            '-DCMAKE_TOOLCHAIN_FILE='+str(Path(vcpkg)/'scripts/buildsystems/vcpkg.cmake'),
                            '-DVCPKG_TARGET_TRIPLET=x64-windows'])
        run(*options)
        run('cmake','--build',str(build),'--config','Release')
        env=os.environ.copy()
        env['PATH']=str(prefix/'bin')+os.pathsep+env.get('PATH','')
        # Also pass macOS/Linux shared-library lookups for bare CTest executables.
        env['LD_LIBRARY_PATH']=str(prefix/'lib')+os.pathsep+env.get('LD_LIBRARY_PATH','')
        env['DYLD_LIBRARY_PATH']=str(prefix/'lib')+os.pathsep+env.get('DYLD_LIBRARY_PATH','')
        run('ctest','--test-dir',str(build),'-C','Release','--output-on-failure',env=env)
    print('installed CMake consumer: PASS')


if __name__=='__main__':
    main()
