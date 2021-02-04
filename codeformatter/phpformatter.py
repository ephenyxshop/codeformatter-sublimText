# @author          Avtandil Kikabidze
# @copyright       Copyright (c) 2008-2015, Avtandil Kikabidze aka LONGMAN (akalongman@gmail.com)
# @link            http://longman.me
# @license         The MIT License (MIT)

import os
import re
import tempfile

import json

import sublime
import subprocess
import os.path
from os.path import dirname, realpath


class PhpFormatter:

    def __init__(self, formatter):
        self.formatter = formatter
        self.opts = formatter.settings.get('codeformatter_php_options')

    def format(self, text):
        # Create temp file
        if self.formatter.platform == 'windows':
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
        else:
            tmp_file = tempfile.NamedTemporaryFile()
        tmp_file.write(text)
        tmp_file.seek(0)

        php_path = 'php'
        if ('php_path' in self.opts and self.opts['php_path']):
            php_path = self.opts['php_path']

        php55_compat = False
        if ('php55_compat' in self.opts and self.opts['php55_compat']):
            php55_compat = self.opts['php55_compat']

        enable_auto_align = False
        if (
            'enable_auto_align' in self.opts and
            self.opts['enable_auto_align']
        ):
            enable_auto_align = self.opts['enable_auto_align']

        indent_with_space = False
        if (
            'indent_with_space' in self.opts and
            self.opts['indent_with_space']
        ):
            indent_with_space = self.opts['indent_with_space']

        psr1 = False
        if ('psr1' in self.opts and self.opts['psr1']):
            psr1 = self.opts['psr1']

        psr1_naming = False
        if ('psr1_naming' in self.opts and self.opts['psr1_naming']):
            psr1_naming = self.opts['psr1_naming']

        psr2 = False
        if ('psr2' in self.opts and self.opts['psr2']):
            psr2 = self.opts['psr2']

        smart_linebreak_after_curly = False
        if ('smart_linebreak_after_curly' in self.opts and self.opts['smart_linebreak_after_curly']):
            smart_linebreak_after_curly = self.opts['smart_linebreak_after_curly']

        visibility_order = False
        if ('visibility_order' in self.opts and self.opts['visibility_order']):
            visibility_order = self.opts['visibility_order']

        passes = []
        if ('passes' in self.opts and self.opts['passes']):
            passes = self.opts['passes']

        passes_option = []
        if ('passes_option' in self.opts and self.opts['passes_option']):
            passes_option = self.opts['passes_option']

        excludes = []
        if ('excludes' in self.opts and self.opts['excludes']):
            excludes = self.opts['excludes']

        cmd = []
        cmd.append(str(php_path))
        cmd.append('-ddisplay_errors=stderr')
        cmd.append('-dshort_open_tag=On')

        formatter_path = os.path.join(
            dirname(realpath(sublime.packages_path())),
            'Packages',
            'CodeFormatter',
            'codeformatter',
            'lib',
            'phpbeautifier',
            'php-cs-fixer.phar' if len(passes_option) > 0 else ('fmt-php55.phar' if php55_compat else 'phpf.phar')
        )

        cmd.append(formatter_path)

        if len(passes_option) > 0:
            cmd.append('fix')
            cmd.append('--quiet')
            cmd.append('--no-interaction')
            cmd.append('--show-progress=none')
            cmd.append('--using-cache=no')
            cmd.append('--rules=' + json.dumps(passes_option))
            cmd.append(tmp_file.name)
        elif len(passes) > 0:

            if psr1:
                cmd.append('--psr1')

            if psr1_naming:
                cmd.append('--psr1-naming')

            if psr2:
                cmd.append('--psr2')

            if indent_with_space is True:
                cmd.append('--indent_with_space')
            elif indent_with_space > 0:
                cmd.append('--indent_with_space=' + str(indent_with_space))

            if enable_auto_align:
                cmd.append('--enable_auto_align')

            if visibility_order:
                cmd.append('--visibility_order')

            if smart_linebreak_after_curly:
                cmd.append('--smart_linebreak_after_curly')

            cmd.append('--passes=' + ','.join(passes))

            if len(excludes) > 0:
                cmd.append('--exclude=' + ','.join(excludes))

            cmd.append('-')

        try:
            if self.formatter.platform == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                p = subprocess.Popen(
                    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, startupinfo=startupinfo,
                    shell=False, creationflags=subprocess.SW_HIDE)
            else:
                p = subprocess.Popen(
                    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            stdout, stderr = p.communicate() if len(passes_option) > 0 else p.communicate(text)
            if len(passes_option) > 0:
                formatted_str = tmp_file.read()
                if self.formatter.platform == 'windows':
                    tmp_file.close()
                    os.unlink(tmp_file.name)
                stdout = formatted_str
        except Exception as e:
            stdout = ''
            stderr = str(e)

        # Close temp file
        tmp_file.close()

        return stdout, stderr

    def format_on_save_enabled(self, file_name):
        format_on_save = False

        if 'format_on_save' in self.opts and self.opts['format_on_save']:
            format_on_save = self.opts['format_on_save']

        if isinstance(format_on_save, str):
            format_on_save = re.search(format_on_save, file_name) is not None

        return format_on_save

