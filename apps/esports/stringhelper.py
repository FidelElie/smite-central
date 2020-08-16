import re

class StringHelper(object):
    regexps = {}
    webcodes = [
        "&amp;"
    ]

    def add_regexp(self, regexp_name, regular_expression, check_cases = False):
        """ Add Regular Expression To Be Precompiled And Stored.

        Parameters
        ----------
        regexp_name: str
            Desired name for the regular expression to be stored with.
        regular_expression: str
            The regular expression to be compiled
        check_cases: bool (default: False)
            If you want the compiled regular expression to be case sensitive
        """
        if not isinstance(check_cases, bool):
            raise TypeError("'check_cases' parameter supports type bool")

        parameters = {"pattern": regular_expression}

        if not check_cases:
            parameters["flags"] = re.IGNORECASE

        self.regexps[regexp_name] = re.compile(**parameters)

    def regexp(self, regexp_name):
        """ Call A Stored Regular Expression To Be Used.

        Parameters
        ----------
        regexp_name: str
            The name for the stored regular expression.

        Returns
        -------
        desired_regexp: Pattern
            The desired explored regular expression
        """
        if regexp_name in self.regexps:
            desired_regexp = self.regexps[regexp_name]
        else:
            raise KeyError(f"Desired regexp '{regexp_name}' was not found.")
        return desired_regexp

    @staticmethod
    def filter_string(string, filters):
        """ Check String Content Against Specific Filters.

        Parameters
        ----------
        string: str
            The String To Check Against.
        filters: dict
            A dictionary containing an 'include' and an 'exclude' key. The 'include' will cause function to only return a match if the string value one of the 'include' values. The 'exclude' key will cause the function to return a match if the string value does not contain an 'exclude' values. Each of the keys should have the value of a list of strings.

        Returns
        -------
        found_match: bool
            Returns True if all filter checks were passed or False otherwise.

        """
        if isinstance(filters, dict):
            if len(filters.keys()) != 2:
                raise ValueError("Invalid Number Of Filter Keys Provided.")
        else:
            raise TypeError("Dictionary Type Expected For Filters.")

        def execute_filter(string, filters, desired_boolean):
            if not filters:
                found_match = True
            else:
                for _filter in filters:
                    if _filter.lower() in string.lower():
                        found_match = desired_boolean
                        break
                else:
                    found_match = not desired_boolean

            return found_match

        match_flags = []
        for flags in filters:
            flag_data = filters[flags]
            if flags == "include":
                match_flags.append(execute_filter(string, flag_data, True))
            elif flags == "exclude":
                match_flags.append(execute_filter(string, flag_data, False))
            else:
                raise KeyError("'include' and 'exclude' flags are supported")

        # if any check returns False then overall check is False
        found_match = False if False in match_flags else True

        return found_match

    @staticmethod
    def compound_filter(filters):
        """ Flatten include and exclude filters

        Parameters
        ----------
        filters: dict
            The dictionary of filters to flatten.

        Returns
        -------
        flattened_filters: dict
            The flattened filters with one include and exclude flag
        """
        include_lists = [filters[_filter]["include"] for _filter in filters]
        exclude_lists = [filters[_filter]["exclude"] for _filter in filters]
        flatten_list = lambda x: [item for sublist in x for item in sublist]

        includes = flatten_list(include_lists)
        excludes = flatten_list(exclude_lists)

        flattened_filters = {
            "include": includes,
            "exclude": excludes
        }

        return flattened_filters

    @staticmethod
    def remove_extra_spaces(string):
        """ Remove Double Space From String Usually Caused By Human Error

        Parameters
        ----------
        string: str
            String for the removal to be executed on.

        Returns
        -------
        no_double_spaces_string: str
            String with the double spaces removed.
        """
        string_to_list = string.split(" ")
        no_whitespace = [word.strip() for word in string_to_list]
        no_double_spaces_list = list(filter(lambda a: a != "", no_whitespace))
        no_double_spaces = " ".join(no_double_spaces_list)

        return no_double_spaces

    @staticmethod
    def regexp_word_sequence(words):
        """ Create an or (|) Sequnce of word quickly for regular expressions

        Parameters
        ----------
        words: list
            List containing the words that should be added to the regular expression string.

        Returns
        -------
        regex_string: str
            String containing the sequence of word that can be now used in regular expressions.
        """
        regexpable_strings = list(map(lambda x: x.replace(" ", "\s*"), words))
        regex_string = r"({})".format("|".join(regexpable_strings))
        return regex_string




