# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-22 12:59

"""
封装一个日志类，想要实现的是文件和控制台都可以记录相关信息
write in 2021.11.22 12.59 @zpchcbd
"""

from core.setting import LOG_PATH
import logging
import os
import sys


class ColorizingStreamHandler(logging.StreamHandler):

    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    level_map = {
        logging.DEBUG: (None, 'blue', False),
        logging.INFO: (None, None, False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }
    csi = '\x1b['
    reset = '\x1b[0m'

    # def __init__(self, level_map=None, *args, **kwargs):
    #     if level_map is not None:
    #         self.level_map = level_map
    #     logging.StreamHandler.__init__(self, *args, **kwargs)

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    if os.name != 'nt':
        def output_colorized(self, message):
            self.stream.write(message)
    else:
        import re
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,    # black
            1: 0x04,    # red
            2: 0x02,    # green
            3: 0x06,    # yellow
            4: 0x01,    # blue
            5: 0x05,    # magenta
            6: 0x03,    # cyan
            7: 0x07,    # white
        }

        def output_colorized(self, message):
            import ctypes
            ctypes.windll.kernel32.SetConsoleTextAttribute.argtypes = [ctypes.c_ulong, ctypes.c_ushort]
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2): # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                    self.stream.flush()  # For win 10
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08 # foreground intensity on
                            elif p == 0: # reset to default color
                                color = 0x07
                            else:
                                pass # error condition ignored

                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params),
                                   'm', message, self.reset))
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message


class CUSTOM_LOGGER_LEVEL:
    MYSCAN_DEBUG = 50
    MYSCAN_INFO = 60
    MYSCAN_ERROR = 80
    MYSCAN_WARN = 70


class Logger:
    def __init__(self,
                 path=os.getcwd() + os.path.sep + LOG_PATH,
                 use_console=True,
                 string_fmt="[%(asctime)s] [%(levelname)s] %(message)s",
                 time_fmt="%Y-%m-%d %H:%M:%S"):

        logging.addLevelName(CUSTOM_LOGGER_LEVEL.MYSCAN_INFO, "+")
        logging.addLevelName(CUSTOM_LOGGER_LEVEL.MYSCAN_ERROR, "-")
        logging.addLevelName(CUSTOM_LOGGER_LEVEL.MYSCAN_WARN, "!")
        logging.addLevelName(CUSTOM_LOGGER_LEVEL.MYSCAN_DEBUG, "debug")

        # logger记录地址
        self.logger = logging.getLogger(path)

        # 设置logger阀值，日志等级小于level会被忽略
        self.logger.setLevel(CUSTOM_LOGGER_LEVEL.MYSCAN_INFO)

        # 设置日志记录格式
        self.formatter = logging.Formatter(string_fmt, time_fmt)

        # 文件日志输出记录
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

        # 控制台日志输出记录
        if use_console:
            try:
                console_handler = ColorizingStreamHandler(sys.stdout)
                console_handler.level_map[logging.getLevelName("+")] = (None, "green", False)
                console_handler.level_map[logging.getLevelName("-")] = (None, "red", False)
                console_handler.level_map[logging.getLevelName("!")] = (None, "yellow", False)
                console_handler.level_map[logging.getLevelName("DEBUG")] = (None, "cyan", False)
                self.console_handler = console_handler
            except Exception:
                self.console_handler = logging.StreamHandler(sys.stdout)
        else:
            self.console_handler = logging.StreamHandler(sys.stdout)

        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

    def set_level(self, level):
        self.logger.setLevel(level)

    def getLogger(self):
        return self.logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def myscan_debug(self, message, *args, **kwargs):
        self.logger.log(CUSTOM_LOGGER_LEVEL.MYSCAN_DEBUG, message, *args, **kwargs)

    def myscan_info(self, message, *args, **kwargs):
        self.logger.log(CUSTOM_LOGGER_LEVEL.MYSCAN_INFO, message, *args, **kwargs)

    def myscan_warn(self, message, *args, **kwargs):
        self.logger.log(CUSTOM_LOGGER_LEVEL.MYSCAN_WARN, message, *args, **kwargs)

    def myscan_error(self, message, *args, **kwargs):
        self.logger.log(CUSTOM_LOGGER_LEVEL.MYSCAN_ERROR, message, *args, **kwargs)

    def __str__(self):
        return 'this is my custom logger'


if __name__ == '__main__':
    mLogger = Logger(path='./logs.txt')
    mLogger.set_level(CUSTOM_LOGGER_LEVEL.MYSCAN_DEBUG)
    mLogger.myscan_debug('HengGe test...., debug')
    mLogger.myscan_info('HengGe test...., info')
    mLogger.myscan_warn('HengGe test...., warning')
    mLogger.myscan_error('HengGe test...., error')
