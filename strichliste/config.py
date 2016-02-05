from configparser import ConfigParser

from utils.Borg import Borg


class Config(Borg):
    _shared_state = {}

    def __init__(self, config_path=None):
        Borg.__init__(self)
        if config_path is not None:
            config = ConfigParser()
            config.read(config_path)
            self.upper_account_boundary = config.getint('limits', 'account_upper', fallback=100) * 100
            self.lower_account_boundary = config.getint('limits', 'account_lower', fallback=-10) * 100
            self.upper_transaction_boundary = config.getint('limits', 'transaction_upper', fallback=9999) * 100
            self.lower_transaction_boundary = config.getint('limits', 'transaction_lower', fallback=-9999) * 100
            self.db_path = config.get('base', 'db_path', fallback='/tmp/strichliste.db')
            if ':///' not in self.db_path:
                self.db_path = 'sqlite:///' + self.db_path
            self.log_path = config.get('logging', 'path', fallback='/tmp/strichliste.log')