import re
import logging

AWS_REGEX = re.compile(
    r"(AWS|aws)?_(SECRET|secret|Secret)?_?(ACCESS|access|Access)?_?(KEY|key|Key)(?P<secret>[A-Za-z0-9/\+=]{41})"
)


def replace(m):
    return "AWS_SECRET_ACCESS_KEY=" + len(m.group("secret")) * "*"


class AWSFilter(logging.Filter):
    def filter(self, record):
        record.msg = re.sub(AWS_REGEX, replace, record.msg)
        return True
