"""
Read and write properties in a string in the format of a 'wp-config.php' file.
"""

import re

from logging import getLogger


class WpConfigString():
    """
    Read and write properties in a string in the format of a 'wp-config.php'
    file.

    Args:
        content (str): The string content of a 'wp-config.php' file
    """

    def __init__(self, content):
        self._content = content
        self._log = getLogger(__name__)

    @property
    def content(self):
        """ Gets the loaded content. """

        return self._content

    def _get_match(self, key):
        """
        Gets a MatchObject for the given key.

        Args:
            key (str): Key of the property to look-up.

        Return:
            MatchObject: The discovered match.
        """

        return self._get_string_match(key=key) or \
            self._get_non_string_match(key=key)

    def _get_non_string_match(self, key):
        """
        Gets a MatchObject for the given key, assuming a non-string value.

        Args:
            key (str): Key of the property to look-up.

        Return:
            MatchObject: The discovered match.
        """

        expression = r'(?:\s*)'.join([
            '^',
            'define',
            r'\(',
            '\'{}\''.format(key),
            ',',
            r'(.*)',
            r'\)',
            ';'
        ])

        pattern = re.compile(expression, re.MULTILINE)
        return pattern.search(self._content)

    def _get_string_match(self, key):
        """
        Gets a MatchObject for the given key, assuming a string value.

        Args:
            key (str): Key of the property to look-up.

        Return:
            MatchObject: The discovered match.
        """

        expression = r'(?:\s*)'.join([
            '^',
            'define',
            r'\(',
            '\'{}\''.format(key),
            ',',
            r'\'(.*)\'',
            r'\)',
            ';'
        ])

        pattern = re.compile(expression, re.MULTILINE)
        return pattern.search(self._content)

    def _get_value_from_match(self, key, match):
        """
        Gets the value of the property in the given MatchObject.

        Args:
            key (str):           Key of the property looked-up.
            match (MatchObject): The matched property.

        Return:
            The discovered value, as a string or boolean.
        """

        value = match.groups(1)[0]
        clean_value = str(value).lstrip().rstrip()

        if clean_value == 'true':
            self._log.info('Got value of "%s" as boolean true.', key)
            return True

        if clean_value == 'false':
            self._log.info('Got value of "%s" as boolean false.', key)
            return False

        try:
            float_value = float(clean_value)
            self._log.info('Got value of "%s" as float "%f".',
                           key,
                           float_value)
            return float_value
        except ValueError:
            self._log.info('Got value of "%s" as string "%s".',
                           key,
                           clean_value)
            return clean_value

    def get(self, key):
        """
        Gets the value of the property of the given key.

        Args:
            key (str): Key of the property to look-up.
        """

        match = self._get_match(key=key)

        if not match:
            return None

        return self._get_value_from_match(key=key, match=match)

    def set(self, key, value):
        """
        Updates the value of the given key in the loaded content.

        Args:
            key (str): Key of the property to update.
            value (str): New value of the property.

        Return:
            bool: Indicates whether or not a change was made.
        """

        match = self._get_match(key=key)

        if not match:
            self._log.info('"%s" does not exist, so it will be added.', key)

            if isinstance(value, str):
                self._log.info('"%s" will be added as a PHP string value.',
                               key)
                value_str = '\'{}\''.format(value)
            else:
                self._log.info('"%s" will be added as a PHP object value.',
                               key)
                value_str = str(value).lower()

            new = 'define(\'{key}\', {value});'.format(
                key=key,
                value=value_str)

            self._log.info('"%s" will be added as: %s', key, new)

            replace_this = '<?php\n'
            replace_with = '<?php\n' + new + '\n'
            self._content = self._content.replace(replace_this, replace_with)
            self._log.info('Content string has been updated.')
            return True

        if self._get_value_from_match(key=key, match=match) == value:
            self._log.info('"%s" is already up-to-date.', key)
            return False

        self._log.info('"%s" exists and will be updated.', key)

        start_index = match.start(1)
        end_index = match.end(1)

        if isinstance(value, bool):
            value = str(value).lower()
            self._log.info('"%s" will be updated with boolean value: %s',
                           key,
                           value)
        else:
            self._log.info('"%s" will be updated with string value: %s',
                           key,
                           value)

        start = self._content[:start_index]
        end = self._content[end_index:]

        self._content = start + value + end
        return True
