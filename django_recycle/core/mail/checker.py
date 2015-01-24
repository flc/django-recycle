import os
import logging


logger = logging.getLogger(__name__)


class EmailChecker(object):

    def __init__(self, paths):
        self.paths = paths

        domains = set()
        for path in self.paths:
            if os.path.isfile(path):
                domains = domains.union(self._process_file(path))
            elif os.path.isdir(path):
                for filename in os.listdir(path):
                    p = os.path.join(path, filename)
                    domains = domains.union(self._process_file(p))
        self.domains = domains

    def _process_file(self, path):
        logger.debug("opening file %s", path)
        try:
            f = open(path)
        except Exception:
            logger.exception("Failed to open %s", path)
            return set()
        else:
            return set(line.strip().lower() for line in f)

    def __len__(self):
        return len(self.domains)

    def __contains__(self, other):
        return other in self.domains

    def is_allowed(self, email):
        domain = email.split("@")[1].lower()
        return domain not in self.domains
