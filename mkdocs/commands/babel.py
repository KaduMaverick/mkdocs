from distutils.errors import DistutilsOptionError
from os import path

from babel.messages import frontend as babel
from pkg_resources import EntryPoint

DEFAULT_MAPPING_FILE = path.normpath(
    path.join(path.abspath(path.dirname(__file__)), '../themes/babel.cfg')
)


class ThemeMixin:
    def get_theme_dir(self):
        """Validate theme option and return path to theme's root obtained from entry point."""
        entry_points = EntryPoint.parse_map(self.distribution.entry_points, self.distribution)
        if 'mkdocs.themes' not in entry_points:
            raise DistutilsOptionError("no mkdocs.themes are defined in entry_points")
        if self.theme is None and len(entry_points['mkdocs.themes']) == 1:
            # Default to the only theme defined in entry_points as none specified.
            self.theme = tuple(entry_points['mkdocs.themes'].keys())[0]
        if self.theme not in entry_points['mkdocs.themes']:
            raise DistutilsOptionError("you must specify a valid theme name to work on")
        theme = entry_points['mkdocs.themes'][self.theme]
        return path.dirname(theme.resolve().__file__)


class compile_catalog(babel.compile_catalog, ThemeMixin):
    user_options = babel.compile_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None

    def finalize_options(self):
        if not self.directory:
            theme_dir = self.get_theme_dir()
            self.directory = f"{theme_dir}/locales"
        super().finalize_options()


class extract_messages(babel.extract_messages, ThemeMixin):
    user_options = babel.extract_messages.user_options + [
        ("domain=", "d", "domains of the POT output file"),
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.domain = "messages"
        self.theme = None

    def finalize_options(self):
        if not self.version:
            version = self.distribution.get_version()
            self.version = ".".join([i for i in version.split(".") if "dev" not in i])
        if not self.mapping_file:
            self.mapping_file = DEFAULT_MAPPING_FILE
        if not self.input_paths or not self.output_file:
            theme_dir = self.get_theme_dir()
            if not self.input_paths:
                self.input_paths = theme_dir
            if not self.output_file:
                self.output_file = f"{theme_dir}/{self.domain}.pot"
        super().finalize_options()


class init_catalog(babel.init_catalog, ThemeMixin):
    user_options = babel.init_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None

    def finalize_options(self):
        if not self.input_file or not self.output_dir:
            theme_dir = self.get_theme_dir()
            if not self.input_file:
                self.input_file = f"{theme_dir}/{self.domain}.pot"
            if not self.output_dir:
                self.output_dir = f"{theme_dir}/locales"
        super().finalize_options()


class update_catalog(babel.update_catalog, ThemeMixin):
    user_options = babel.update_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None

    def finalize_options(self):
        if not self.input_file or not self.output_dir:
            theme_dir = self.get_theme_dir()
            if not self.input_file:
                self.input_file = f"{theme_dir}/{self.domain}.pot"
            if not self.output_dir:
                self.output_dir = f"{theme_dir}/locales"
        super().finalize_options()
