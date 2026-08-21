#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2022-2026 RoadrunnerWMC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Iterator


KAMEK_EXE_NAME = 'Kamek.exe' if sys.platform == 'win32' else 'Kamek'
KAMEK_H_NAME = 'kamek.h'
MWCCEPPC_EXE_NAME = 'mwcceppc.exe'
MWASMEPPC_EXE_NAME = 'mwasmeppc.exe'
CW_WRAPPER_SCRIPT_NAME = 'cw_wrapper.py'

DEFAULT_BUILD_DIR_NAME = '_build'
DEFAULT_OUTPUT_DIR_NAME = 'bin'
DEFAULT_OUTPUT_MAPS_DIR_NAME = '_maps'

DYNAMIC_GAME_VERSION_NAME = 'DYNAMIC'
GAME_VERSION_PREPROC_FLAG_DYNAMIC = 'IS_GAME_VERSION_DYNAMIC'
GAME_VERSION_PREPROC_FLAG = 'IS_GAME_VERSION_{version}_COMPATIBLE'


def ninja_escape(thing: Any) -> str:
    """
    Call str() on `thing` (probably a str or Path), and apply
    Ninja-style space escaping
    """
    return str(thing).replace('$', '$$').replace(':', '$:').replace(' ', '$ ')


class Config:
    """
    Contains configuration options provided by the user
    """
    kamek_dir: Path
    k_stdlib_dir: Path | None
    cw_dir: Path
    project_dir: Path
    build_dir: Path
    output_dir: Path
    output_maps_dir: Path | None
    select_versions: list[str] | None
    extra_cflags: list[str]

    @staticmethod
    def create_arg_parser(*args, **kwargs) -> None:
        """
        Create an ArgumentParser
        """
        parser = argparse.ArgumentParser(*args,
            epilog='Any additional arguments will be passed directly to CodeWarrior.',
            allow_abbrev=False,
            **kwargs)

        if sys.platform == 'win32':
            kamek_binary_desc = KAMEK_EXE_NAME
        else:
            kamek_binary_desc = 'the Kamek binary ("Kamek")'

        deps_group = parser.add_argument_group('Dependency locations')
        deps_group.add_argument('--kamek', type=Path,
            help=f'Kamek folder, containing {kamek_binary_desc} and the k_stdlib directory (default: {KAMEK_EXE_NAME} is searched for on PATH)')
        deps_group.add_argument('--kstdlib', type=Path,
            help="Kamek's k_stdlib directory (default: <kamek dir>/k_stdlib)")
        deps_group.add_argument('--cw', type=Path, metavar='CODEWARRIOR',
            help=f'CodeWarrior folder, containing {MWCCEPPC_EXE_NAME}, {MWASMEPPC_EXE_NAME}, and license.dat, at minimum (default: {MWCCEPPC_EXE_NAME} is searched for on PATH)')

        proj_group = parser.add_argument_group('Project location')
        proj_group.add_argument('--project-dir', type=Path, metavar='PROJECT',
            help='project directory (with src/, include/, etc.) (default: current directory)')

        out_group = parser.add_argument_group('Output options')
        out_group.add_argument('--select-version', metavar='VERSION', action='append',
            help='build only for the indicated game version, instead of all of them (can be specified multiple times)')
        out_group.add_argument('--build-dir', type=Path, metavar='BUILD',
            help=f'directory to put object files and Ninja\'s bookkeeping files ("$builddir")'
                 f' (default: <project dir>/{DEFAULT_BUILD_DIR_NAME})')
        out_group.add_argument('--output-dir', type=Path, metavar='OUT',
            help=f'output directory to put Kamekfiles in'
                 f' (default: <project dir>/{DEFAULT_OUTPUT_DIR_NAME})')
        out_group.add_argument('--output-maps-dir', type=Path, metavar='MAPS',
            help=f'directory to put text files with symbol names and offsets (Kamek\'s "-output-map" argument)'
                 f' (to disable generating maps, set this to the empty string)'
                 f' (default: <project dir>/{DEFAULT_OUTPUT_MAPS_DIR_NAME})')

        return parser

    @staticmethod
    def find_on_path(exe_name: str, arg_name: str) -> Path:
        """
        Search PATH for an executable. If not found, raise ValueError,
        with an error message suggesting that the user can also use the
        arg_name argument to specify a relevant path manually
        """
        result = shutil.which(exe_name)

        if result is None:
            raise ValueError(f'Unable to find {exe_name} (no {arg_name} argument provided, and not found on PATH)')
        else:
            return Path(result)

    @classmethod
    def from_args(cls, args: argparse.Namespace, extra_args: list[str]) -> None:
        """
        Construct a Config instance from the CLI arguments
        """
        project_dir = args.project_dir or Path.cwd()

        self = cls()

        if args.kamek is not None:
            self.kamek_dir = args.kamek.resolve()
        else:
            self.kamek_dir = cls.find_on_path(KAMEK_EXE_NAME, '--kamek').parent

        if args.kstdlib is not None:
            self.k_stdlib_dir = args.kstdlib.resolve()
        else:
            self.k_stdlib_dir = self.kamek_dir / 'k_stdlib'

        if args.cw is not None:
            self.cw_dir = args.cw.resolve()
        else:
            self.cw_dir = cls.find_on_path(MWCCEPPC_EXE_NAME, '--cw').parent

        if not (self.kamek_dir / KAMEK_EXE_NAME).is_file():
            raise ValueError(f'Kamek directory seems incorrect (no {KAMEK_EXE_NAME} found)')
        if not (self.k_stdlib_dir / KAMEK_H_NAME).is_file():
            raise ValueError(f'Kamek k_stdlib directory seems incorrect (no {KAMEK_H_NAME} found)')
        if not (self.cw_dir / MWCCEPPC_EXE_NAME).is_file():
            raise ValueError(f'CodeWarrior directory seems incorrect (no {MWCCEPPC_EXE_NAME} found)')

        self.project_dir = project_dir.resolve()
        self.select_versions = args.select_version or None
        self.build_dir = (args.build_dir or project_dir / DEFAULT_BUILD_DIR_NAME).resolve()
        self.output_dir = (args.output_dir or project_dir / DEFAULT_OUTPUT_DIR_NAME).resolve()
        self.extra_cflags = extra_args

        if args.output_maps_dir is None:
            self.output_maps_dir = (project_dir / DEFAULT_OUTPUT_MAPS_DIR_NAME).resolve()
        elif args.output_maps_dir:
            self.output_maps_dir = args.output_maps_dir.resolve()
        else:
            self.output_maps_dir = None

        if self.select_versions is not None:
            # Quick sanity check
            for v in self.select_versions:
                if v not in self.get_version_names_list():
                    raise ValueError(f'Unknown --select-version version: "{v}"')

        return self

    @property
    def kamek_exe(self) -> Path:
        return self.kamek_dir / KAMEK_EXE_NAME

    @property
    def mwcceppc_exe(self) -> Path:
        return self.cw_dir / MWCCEPPC_EXE_NAME

    @property
    def mwasmeppc_exe(self) -> Path:
        return self.cw_dir / MWASMEPPC_EXE_NAME

    @property
    def src_dir(self) -> Path:
        return self.project_dir / 'src'

    @property
    def include_dir(self) -> Path:
        return self.project_dir / 'include'

    @property
    def address_map_txt(self) -> Path:
        fp1 = self.project_dir / 'address-map.txt'
        fp2 = self.project_dir / 'versions.txt'
        if fp2.is_file() and not fp1.is_file():
            return fp2
        else:
            return fp1

    def have_address_map_txt(self) -> bool:
        return self.address_map_txt.is_file()

    @property
    def externals_txt(self) -> Path:
        return self.project_dir / 'externals.txt'

    def have_externals_txt(self) -> bool:
        return self.externals_txt.is_file()

    @property
    def ninja_file(self) -> Path:
        return self.project_dir / 'build.ninja'

    _version_names_list = None
    def get_version_names_list(self) -> list[str]:
        if self._version_names_list is None:
            if self.have_address_map_txt():
                self._version_names_list = \
                    get_version_names_list_from_address_map(
                        self.address_map_txt)
            else:
                self._version_names_list = []
        return list(self._version_names_list)

    def have_output_maps_dir(self) -> bool:
        return self.output_maps_dir is not None


def get_version_names_list_from_address_map(path: Path) -> list[str]:
    """
    Read an address map file and extract the names of all game versions
    it defines, in order.
    """
    address_map_version_header_line = re.compile(
        r'^'          # start of string
        r'\s*'        # optional whitespace
        r'\[(\w+)\]'  # '[', one or more word chars (captured), ']'
        r'.*'         # additional stuff (e.g. comments); we don't care
                      # much anymore at this point
        r'$'          # end of string
    )

    versions = []
    for line in path.read_text(encoding='utf-8').splitlines():
        match = address_map_version_header_line.fullmatch(line)
        if match:
            versions.append(match[1])

    return versions


class TranslationUnit:
    """
    Represents one translation unit (.cpp or .s file)
    """
    source_file: Path

    use_static_version_builds: bool
    # {"compile_for_this_version": {"for", "these", "build", "versions"}, ...}
    static_version_builds: dict[str, set[str]]

    def __init__(self, src_root_dir: Path, source_file: Path, game_versions: list[str]) -> 'TranslationUnit':
        """
        Create a TranslationUnit from a .cpp file path, including
        checking for the existence of a corresponding .json file
        """
        super().__init__()
        self.source_file = source_file
        self.use_static_version_builds = False
        self.static_version_builds = {}

        inspect_path = source_file
        while True:
            json_path = inspect_path.with_suffix('.json')
            if json_path.is_file():
                self.read_config(json_path, game_versions)
                return

            if inspect_path == src_root_dir or inspect_path == inspect_path.parent:
                break
            else:
                inspect_path = inspect_path.parent

    def is_cpp(self) -> bool:
        return self.source_file.suffix.lower() == '.cpp'

    def read_config(self, path: Path, game_versions: list[str]) -> None:
        """
        Read additional config data from an optional .json file
        """
        if not path.is_file():
            return
        with path.open(encoding='utf-8') as f:
            j = json.load(f)

        if 'json_version' not in j:
            raise ValueError(f'{path.name}: json_version not found')
        elif j['json_version'] != 1:
            raise ValueError(f'{path.name}: unsupported json_version ({j["json_version"]})')

        builds_list = j.get('builds')
        if builds_list:
            self.use_static_version_builds = True
            self.static_version_builds = {k: set(v) for k, v in builds_list.items()}

            # Sanity checks
            already_seen = set()
            for leader, group in self.static_version_builds.items():
                if leader not in game_versions:
                    raise ValueError(f'{path.name}: unknown game version "{leader}" (expected one of {game_versions})')
                if leader not in group:
                    raise ValueError(f"{path.name} says to compile for version {leader} when building versions {group}, but {leader} isn't even in that group!")
                for member in group:
                    if member not in game_versions:
                        raise ValueError(f'{path.name}: unknown game version "{member}" (expected one of {game_versions})')
                    if member in already_seen:
                        raise ValueError(f'{path.name}: "{member}" is present in multiple build groups')
                already_seen |= group

    def iter_builds(self, config: Config) -> Iterator[tuple[str, Path]]:
        """
        Iterator over the .o files that need to be built for this TU.
        Yields (preprocessor flag, .o filepath) pairs.
        """
        if self.use_static_version_builds:
            versions_to_build_for = set()

            if config.select_versions is None:
                # Build all leaders
                versions_to_build_for = set(self.static_version_builds)

            else:
                # Build all leaders which have at least one group member
                # that we need to output for
                for leader, group in self.static_version_builds.items():
                    for member in group:
                        if member in config.select_versions:
                            versions_to_build_for.add(leader)

            for version in versions_to_build_for:
                yield GAME_VERSION_PREPROC_FLAG.format(version=version), self.o_file_for_version(version, config)

        else:
            yield GAME_VERSION_PREPROC_FLAG_DYNAMIC, self.o_file_for_version(DYNAMIC_GAME_VERSION_NAME, config)

    def o_file_for_version(self, version: str, config: Config) -> str | None:
        """
        Return the .o file path that should be used for the specified
        game version, or None if it shouldn't be built at all for this
        version.
        """
        if self.use_static_version_builds:
            for leader, group in self.static_version_builds.items():
                if version in group:
                    suffix = f'.{leader}.o'
                    break
            else:
                return None
        else:
            # We can use just ".o" instead of ".dynamic.o"
            suffix = '.o'

        return config.build_dir / self.source_file.relative_to(config.src_dir).with_suffix(suffix)


def make_ninja_file(config: Config) -> str:
    """
    Make the overall Ninja file
    """

    # Find all TUs, and read any configs
    tus = []
    for glob in ['**/*.cpp', '**/*.s']:
        for fp in sorted(config.src_dir.glob(glob, case_sensitive=False)):
            tus.append(TranslationUnit(config.src_dir, fp, config.get_version_names_list()))

    use_addrmap = config.have_address_map_txt()
    use_externals = config.have_externals_txt()
    use_output_maps = config.have_output_maps_dir()

    quote = '"' if sys.platform == 'win32' else "'"

    if sys.platform == 'win32':
        mkdir_command = 'cmd /c mkdir $out'
    else:
        mkdir_command = 'mkdir -p $out'

    lines = []
    lines.append(f'# NOTE: "builddir" has special significance to Ninja (see the manual)')
    lines.append(f'builddir = {ninja_escape(config.build_dir)}')
    lines.append(f'outdir = {ninja_escape(config.output_dir)}')
    lines.append(f'')
    lines.append(f'mwcceppc = {ninja_escape(config.mwcceppc_exe)}')
    lines.append(f'mwasmeppc = {ninja_escape(config.mwasmeppc_exe)}')
    cw_wrapper = Path(__file__).parent / CW_WRAPPER_SCRIPT_NAME
    lines.append(f'cc = {ninja_escape(sys.executable)} {quote}{ninja_escape(cw_wrapper)}{quote} {quote}$mwcceppc{quote}')
    lines.append(f'as = {ninja_escape(sys.executable)} {quote}{ninja_escape(cw_wrapper)}{quote} {quote}$mwasmeppc{quote}')
    lines.append(f'kamek = {ninja_escape(config.kamek_exe)}')
    lines.append(f'kstdlib = {ninja_escape(config.k_stdlib_dir)}')
    if use_addrmap:
        lines.append(f'addrmap = {ninja_escape(config.address_map_txt)}')
    if use_externals:
        lines.append(f'externals = {ninja_escape(config.externals_txt)}')
    if use_output_maps:
        lines.append(f'outmapsdir = {ninja_escape(config.output_maps_dir)}')
    lines.append(f'includedir = {ninja_escape(config.include_dir)}')
    lines.append(f'')

    dumb_constant = ' $\n  '  # backslashes aren't allowed in f-strings
    lines.append(f"""
shared_flags = $
  -I- $
  -i {quote}$kstdlib{quote} $
  -i {quote}$includedir{quote} $
  -maxerrors 1

cflags = $
  $shared_flags $
  -Cpp_exceptions off $
  -enum int $
  -O4,s $
  -use_lmw_stmw on $
  -fp hard $
  -rostr $
  -sdata 0 $
  -sdata2 0 $
  -RTTI off{(dumb_constant + ' '.join(config.extra_cflags)) if config.extra_cflags else ''}

asflags = $shared_flags

rule mkdir
  command = {mkdir_command}
  description = mkdir -p $out

rule mwcc
  command = $cc $cflags -c -o $out -MDfile $out.d $in
  depfile = $out.d
  description = {config.mwcceppc_exe.name} -o $out_filename $in_filename

rule mwasm
  command = $as $asflags -c -o $out -MDfile $out.d $in
  depfile = $out.d
  description = {config.mwasmeppc_exe.name} -o $out_filename $in_filename
""".strip('\n'))

    # Add "mwcc" and "mwasm" edges for all (.cpp or .s) -> .o files
    lines.append('')
    for tu in tus:
        for preproc_flag, o_file in tu.iter_builds(config):
            if tu.is_cpp():
                lines.append(f'build {ninja_escape(o_file)}: mwcc {ninja_escape(tu.source_file)}')
                lines.append(f'  cflags = $cflags -D{preproc_flag}')
            else:
                lines.append(f'build {ninja_escape(o_file)}: mwasm {ninja_escape(tu.source_file)}')
                lines.append(f'  asflags = $asflags -D{preproc_flag}')
            lines.append(f'  out_filename = {ninja_escape(o_file.relative_to(config.build_dir))}')
            lines.append(f'  in_filename = {ninja_escape(tu.source_file.relative_to(config.src_dir))}')
            lines.append('')

    rule_command = f'{quote}$kamek{quote} $in -quiet -dynamic'
    if use_addrmap:
        rule_command += f' {quote}-versions=$addrmap{quote}'
    if use_externals:
        rule_command += f' {quote}-externals=$externals{quote}'
    if use_output_maps:
        rule_command += f' {quote}-output-map=$outmapsdir/$$KV$$.txt{quote}'
    rule_command += ' -output-kamek=$out -select-version=$selectversion'

    lines.append(f"""
build $outmapsdir: mkdir

rule kmdynamic
  command = {rule_command}
  description = {ninja_escape(config.kamek_exe.name)} -> $out_filename
""")

    # Add "km" edges for all .o -> .bin files
    # TODO: how do you handle the case where a version ends up with zero
    # .o files? *do* I even need to handle that?
    output_versions = config.select_versions or config.get_version_names_list()
    for version in output_versions:
        lines.append(f'build $outdir/{version}.bin: kmdynamic')

        for tu in tus:
            o_file = tu.o_file_for_version(version, config)
            if o_file:
                lines[-1] += f' {ninja_escape(o_file)}'

        implicit_deps = []
        if use_addrmap:
            implicit_deps.append('$addrmap')
        if use_externals:
            implicit_deps.append('$externals')
        if use_output_maps:
            implicit_deps.append('$outmapsdir')
        if implicit_deps:
            lines[-1] += f' | {" ".join(implicit_deps)}'

        lines.append(f'  selectversion = {version}')
        lines.append(f'  out_filename = {version}.bin')
        lines.append('')

    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> None:
    """
    Main function
    """
    parser = Config.create_arg_parser(
        description='Creates a Ninja file matching the configuration options you specify.')

    # Use parse_known_args() so that we can collect unrecognized
    # arguments and pass them to CodeWarrior
    args, extra_args = parser.parse_known_args(argv)
    config = Config.from_args(args, extra_args)

    txt = make_ninja_file(config)
    ninja_fp = config.ninja_file
    ninja_fp.write_text(txt, encoding='utf-8')


if __name__ == '__main__':
    main()
