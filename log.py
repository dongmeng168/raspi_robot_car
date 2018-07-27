import logging
class MyCarLog(object):
    """docstring for MyCarLog"""
    def __init__(self):
        pass
        # 创建Logger
        self.logger = logging.getLogger("MyCar.main")
        self.logger.setLevel(logging.DEBUG)

        # 创建Handler

        # 终端Handler
        self.consoleHandler = logging.StreamHandler()
        self.consoleHandler.setLevel(logging.DEBUG)

        # 文件Handler
        self.fileHandler = logging.FileHandler('log.log', mode='w', encoding='UTF-8')
        self.fileHandler.setLevel(logging.NOTSET)

        # Formatter
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.consoleHandler.setFormatter(self.formatter)
        self.fileHandler.setFormatter(self.formatter)

        # 添加到Logger中
        self.logger.addHandler(self.consoleHandler)
        self.logger.addHandler(self.fileHandler)
    def debug(self,msg):
        return self.logger.debug(msg)
    def info(self,msg):
        return self.logger.info(msg)
    def warning(self,msg):
        return self.logger.warning(msg)
    def error(self,msg):
        return self.logger.error(msg)
    def critical(self,msg):
        return self.logger.critical(msg)

if __name__ == '__main__':
    # 打印日志
    macatlog1 = MyCarLog()
    macatlog1.debug('debug 信息')
    macatlog1.info('info 信息')
    macatlog1.warning('warn 信息')
    macatlog1.error('error 信息')
    macatlog1.critical('critical 信息')
    macatlog1.debug('%s 是自定义信息' % '这些东西')
