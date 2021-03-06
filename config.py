import ConfigParser
import watchdog
from watchdog.observers import Observer

global options

class Options(watchdog.events.FileSystemEventHandler):
    CONFIG_FILE = 'config.ini'
    REQUIRED_SECTIONS = (
        'credentials',
        'general',
        'target'
    )

    def __init__(self, *args, **kwargs):

        self._config = ConfigParser.RawConfigParser()
        self.reload_config()
        self._config_valid = False
        self.observer = Observer()
        self.observer.schedule(self, path='.', recursive=False)
        self.observer.start()

    def __del__(self):
        self.observer.stop()
        self.observer.join()

    def on_any_event(self, event):
        if self.CONFIG_FILE in event.src_path:
            self.reload_config()

    def reload_config(self):
        print 'config reloaded'
        self._config.read(self.CONFIG_FILE)
        self.check_config()

    def check_config(self):
        self._config_valid = False

        try:
            for section in self.REQUIRED_SECTIONS:
                self._config.items(section)
            self._config_valid = True
        except ConfigParser.NoSectionError:
            self._config_valid = False

    def updateValue(self,section,key,value):
        from ConfigParser import SafeConfigParser
        parser = SafeConfigParser()
        parser.read(self.CONFIG_FILE)
        parser.set(section, key, value)
        with open(self.CONFIG_FILE, 'wb') as configfile:
            parser.write(configfile)

    def __getitem__(self, section):

        return dict(self._config.items(section))


    @property
    def valid(self):
        return self._is_config_valid


options = Options()
