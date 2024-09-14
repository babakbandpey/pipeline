"""
This module contains the NmapScanner class, which represents an Nmap scanner.

The NmapScanner class provides methods to run an Nmap scan on a target IP address or hostname,
parse the scan output, and extract relevant information.

Example usage:
    target = "192.168.56.4"
    scanner = NmapScanner(target)
    scanner.run_nmap() or scanner.run_command("nmap -sV -p 22,80 -O 10.0.10.10")
    scanner.parse_output()
"""

import subprocess
import re
from pipeline import logger
from pprint import pprint

class NmapScanner:
    """
    A class that represents an Nmap scanner.

    Attributes:
        target (str): The target IP address or hostname to scan.
        nmap_output (str): The output of the Nmap scan.
        parsed_data (dict): Parsed data from the Nmap scan.

    Methods:
        run_nmap(): Runs the Nmap scan.
        run_command(command: str): Runs a command in the shell.
        parse_output(): Parses the Nmap scan output.
        get_parsed_data(): Returns the parsed data from the Nmap scan.
    """
    def __init__(self, **kwargs):
        """
        kwargs:
            target (str): The target IP address or hostname to scan.
            flags (str): Additional flags to pass to Nmap.
            ports (str): The ports to scan.
            firewall (bool): Whether to bypass the firewall.
            script (str): The Nmap script to run.
            command (str): The full Nmap command to run.
        """
        if 'target' not in kwargs:
            logger.error("Target IP address or hostname is required. kwargs: %s", kwargs)
            raise ValueError("Target IP address or hostname is required.")

        self._kwargs = kwargs
        self.nmap_output = ''
        self.parsed_data = {}


    def __getattr__(self, name):
        """
        Returns the value of the specified attribute.
        """
        attributes = {
            "target": lambda: self._kwargs.get("target"),
            "flags": lambda: self._kwargs.get("flags", ""),
            "ports": lambda: f" -p {self._kwargs['ports']}" if self._kwargs.get("ports") else "",
            "firewall": lambda: " -Pn " if self._kwargs.get("firewall") else "",
            "script": lambda: f" --script {self._kwargs['script']}" if self._kwargs.get("script") else ""
        }

        if name in attributes:
            return attributes[name]()

        raise AttributeError(f"The 'NmapScanner' object has no attribute '{name}'")


    def run_nmap(self):
        """
        Runs an Nmap scan on the target.

        Returns:
            str: The output of the Nmap scan.
        """
        command = f"nmap {self.flags} {self.ports} {self.script} {self.firewall} {self.target}"
        return self.run_command(command)


    def run_command(self, command):
        """
        Runs a command in the shell.
        param command: The command to run.
        """

        logger.info("Running Nmap command: %s", command)

        try:
            with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                output, error = process.communicate()
                if process.returncode != 0:
                    logger.error("Error running nmap: %s", error)
                    return None

            self.nmap_output = output
            return self
        except Exception as e:
            logger.error("Error running nmap: %s", str(e))


    def parse_output(self):
        """
        Parses the Nmap scan output and extracts relevant information.
        """
        host_regex = re.compile(r'Nmap scan report for ([\d\.]+)')
        port_regex = re.compile(r'(\d+/\w+)\s+(\w+)\s+(\w+)\s+(.+)')
        mac_regex = re.compile(r'MAC Address: ([0-9A-F:]+) \((.+)\)')
        service_info_regex = re.compile(r'Service Info: OSs: (.+); CPE: (.+)')

        host_match = host_regex.search(self.nmap_output)
        host_ip = host_match.group(1) if host_match else None

        ports = []
        for port_match in port_regex.finditer(self.nmap_output):
            port_info = {
                'port': port_match.group(1),
                'state': port_match.group(2),
                'service': port_match.group(3),
                'version': port_match.group(4)
            }
            ports.append(port_info)

        mac_match = mac_regex.search(self.nmap_output)
        mac_address = mac_match.group(1) if mac_match else None
        mac_vendor = mac_match.group(2) if mac_match else None

        service_info_match = service_info_regex.search(self.nmap_output)
        os_info = service_info_match.group(1) if service_info_match else None
        cpe_info = service_info_match.group(2) if service_info_match else None

        self.parsed_data = {
            'host_ip': host_ip,
            'ports': ports,
            'mac_address': mac_address,
            'mac_vendor': mac_vendor,
            'os_info': os_info,
            'cpe_info': cpe_info
        }

        return self


    def get_output(self):
        """
        Returns the output of the Nmap scan.
        """
        return self.nmap_output


    def get_parsed_data(self):
        """
        Returns the parsed data from the Nmap scan.
        """
        return self.parsed_data
