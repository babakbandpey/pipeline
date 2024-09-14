"""
SearchSploit Interaction Class

This Python script provides a comprehensive class to interact with the `searchsploit` tool on a Linux system.
The `searchsploit` tool is used to search the Exploit Database, and this class encapsulates its functionalities
for easy integration and usage in Python projects.

Class: SearchSploit

Methods:
1. __init__():
    - Initializes the base command for `searchsploit`.
    - Initializes a logger object from the `pipeline` module to log information and errors.

2. _run_command(cmd: List[str], timeout: int = None) -> str:
    - Runs the given command using `subprocess`.
    - Captures and returns the output.
    - Logs the command execution and errors.
    - Accepts an optional timeout parameter to terminate the process if it exceeds the given duration.

3. search(terms: List[str], case_sensitive: bool = False, exact_match: bool = False,
          strict_search: bool = False, title_only: bool = False, exclude: str = None,
          cve: str = None, json_format: bool = False) -> Union[str, dict]:
    - Constructs and runs the `searchsploit` search command with various options:
        * case_sensitive: Perform a case-sensitive search.
        * exact_match: Perform an exact and order match on exploit titles.
        * strict_search: Perform a strict search, disabling fuzzy version range matches.
        * title_only: Search only the exploit title.
        * exclude: Exclude specific terms from results.
        * cve: Search for specific CVE values.
        * json_format: Output results in JSON format.
    - Returns the search results as a string or JSON dictionary.

4. show_path(edb_id: int) -> str:
    - Shows the full path to an exploit by its EDB-ID.
    - Copies the path to the clipboard if possible.

5. mirror_exploit(edb_id: int) -> str:
    - Mirrors (copies) an exploit to the current working directory by its EDB-ID.

6. examine_exploit(edb_id: int) -> str:
    - Examines (opens) an exploit using the default pager by its EDB-ID.

7. update_database(timeout: int = 60) -> str:
    - Checks for and installs any updates to the exploit database.
    - Terminates the process if it exceeds the given timeout (default is 60 seconds).

8. help() -> str:
    - Displays the help screen with all available options and usage examples.

Example Usage:
    ss = SearchSploit()

    # Perform a simple search
    print(ss.search(["afd", "windows", "local"]))

    # Perform a search with exact match and JSON output
    print(ss.search(["oracle", "windows"], exact_match=True, json_format=True))

    # Show the path of an exploit by EDB-ID
    print(ss.show_path(39446))

    # Mirror an exploit by EDB-ID
    print(ss.mirror_exploit(39446))

    # Examine an exploit by EDB-ID
    print(ss.examine_exploit(39446))

    # Update the exploit database
    print(ss.update_database())

    # Display help
    print(ss.help())
"""

import subprocess
import json
from typing import List, Union
from pipeline import logger

class SearchSploit:
    """
    A class to interact with the `searchsploit` tool on a Linux system.
    """

    def __init__(self):
        """
        Initializes the base command for `searchsploit` and sets up the logger.
        """
        self.base_cmd = ["searchsploit"]
        self.logger = logger

    def _run_command(self, cmd: List[str], timeout: int = None) -> str:
        """
        Runs the given command using `subprocess`.

        Parameters:
        cmd (List[str]): The command to run as a list of strings.
        timeout (int, optional): The time in seconds after which the process will be terminated if it exceeds this duration.

        Returns:
        str: The output of the command or an error message.
        """

        self.logger.info("Running command: %s", ' '.join(cmd))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
            self.logger.info("Command executed successfully: %s", ' '.join(cmd))
            return result.stdout
        except subprocess.TimeoutExpired:
            self.logger.error("Command timed out after %s seconds: %s", timeout, ' '.join(cmd))
            return f"Command '{cmd}' timed out after {timeout} seconds"
        except subprocess.CalledProcessError as e:
            self.logger.error("Error executing command: %s", e.stderr)
            return f"Error executing command '{cmd}' : {e.stderr}"
        except json.JSONDecodeError as e:
            self.logger.error("JSON decode error: %s", str(e))
            return f"JSON decode error for command '{cmd}': {str(e)}"
        except Exception as e:
            self.logger.error("Unexpected error command %s : %s", cmd, str(e))
            return f"Unexpected error: {str(e)}"

    def search(self, terms: List[str], case_sensitive: bool = False, exact_match: bool = False,
               strict_search: bool = False, title_only: bool = False, exclude: str = None,
               cve: str = None, json_format: bool = True) -> Union[str, dict]:
        """
        Constructs and runs the `searchsploit` search command with various options.

        Parameters:
        terms (List[str]): The search terms.
        case_sensitive (bool, optional): Perform a case-sensitive search.
        exact_match (bool, optional): Perform an exact and order match on exploit titles.
        strict_search (bool, optional): Perform a strict search, disabling fuzzy version range matches.
        title_only (bool, optional): Search only the exploit title.
        exclude (str, optional): Exclude specific terms from results.
        cve (str, optional): Search for specific CVE values.
        json_format (bool, optional): Output results in JSON format.

        Returns:
        Union[str, dict]: The search results as a string or JSON dictionary.
        """
        cmd = self.base_cmd + terms

        if case_sensitive:
            cmd.append("--case")
        if exact_match:
            cmd.append("--exact")
        if strict_search:
            cmd.append("--strict")
        if title_only:
            cmd.append("--title")
        if exclude:
            cmd.append(f"--exclude={exclude}")
        if cve:
            cmd.append(f"--cve={cve}")
        if json_format:
            cmd.append("--json")

        output = self._run_command(cmd)
        if json_format:
            try:
                return json.loads(output)
            except json.JSONDecodeError as e:
                self.logger.error("JSON decode error: %s", str(e))
                return f"JSON decode error: {str(e)}"
        return output

    def show_path(self, edb_id: int) -> str:
        """
        Shows the full path to an exploit by its EDB-ID.

        Parameters:
        edb_id (int): The EDB-ID of the exploit.

        Returns:
        str: The full path to the exploit or an error message.
        """
        cmd = self.base_cmd + ["--path", str(edb_id)]
        return self._run_command(cmd)

    def mirror_exploit(self, edb_id: int) -> str:
        """
        Mirrors (copies) an exploit to the current working directory by its EDB-ID.

        Parameters:
        edb_id (int): The EDB-ID of the exploit.

        Returns:
        str: The result of the mirror command or an error message.
        """
        cmd = self.base_cmd + ["--mirror", str(edb_id)]
        return self._run_command(cmd)

    def examine_exploit(self, edb_id: int) -> str:
        """
        Examines (opens) an exploit using the default pager by its EDB-ID.

        Parameters:
        edb_id (int): The EDB-ID of the exploit.

        Returns:
        str: The result of the examine command or an error message.
        """
        cmd = self.base_cmd + ["--examine", str(edb_id)]
        return self._run_command(cmd)

    def update_database(self, timeout: int = 60) -> str:
        """
        Checks for and installs any updates to the exploit database.

        Parameters:
        timeout (int, optional): The time in seconds after which the process will be terminated if it exceeds this duration (default is 60 seconds).

        Returns:
        str: The result of the update command or an error message.
        """
        cmd = self.base_cmd + ["--update"]
        return self._run_command(cmd, timeout=timeout)

    def help(self) -> str:
        """
        Displays the help screen with all available options and usage examples.

        Returns:
        str: The help screen output.
        """
        cmd = self.base_cmd + ["--help"]
        return self._run_command(cmd)
