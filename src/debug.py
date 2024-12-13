import json


class Logger:
    def log(self, level, message, data=None):
        message = {
            "level": level,
            "message": message,
        }

        if data:
            message["data"] = data

        print(json.dumps(message))

    def trace(self, message, data=None):
        return self.log(level="TRACE", message=message, data=data)

    def debug(self, message, data=None):
        return self.log(level="DEBUG", message=message, data=data)

    def info(self, message, data=None):
        return self.log(level="INFO", message=message, data=data)

    def warn(self, message, data=None):
        return self.log(level="WARN", message=message, data=data)

    def error(self, message, data=None):
        return self.log(level="ERROR", message=message, data=data)

    def fatal(self, message, data=None):
        return self.log(level="FATAL", message=message, data=data)


logger = Logger()
