
"""
Read and write properties in a 'wp-config.php' file.
"""

from logging import getLogger

from wpconfigr import WpConfigString

class WpConfigFile(WpConfigString):
    """
    Read and write properties in a 'wp-config.php' file.

    Args:
        filename (str): Filename of the 'wp-config.php' file.
    """

    def __init__(self, filename):
        self._filename = filename
        self._log = getLogger(__name__)

        self._log.info('Loading configuration from "%s"...', filename)
        with open(self._filename, 'r') as stream:
            content = stream.read()

        self._log.info('Loaded configuration from "%s".', filename)
        super().__init__(content=content)

    def set(self, key, value):
        """
        Updates the value of the given key in the file.

        Args:
            key (str): Key of the property to update.
            value (str): New value of the property.

        Return:
            bool: Indicates whether or not a change was made.
        """

        changed = super().set(key=key, value=value)

        if not changed:
            return False

        self._log.info('Saving configuration to "%s"...', self._filename)

        with open(self._filename, 'w') as stream:
            stream.write(self.content)
            self._log.info('Saved configuration to "%s".', self._filename)

        return True
