"""
This is the main file that runs the Nmap Port Scanner Project.
"""

import datetime
import secrets
from pprint import pprint
from pipeline import PipelineUtils, ChatbotUtils, NmapScanner, SearchSploit


class NmapPortScannerProject:
    """
    The Nmap Port Scanner Project class that orchestrates the project.
    """

    def __init__(self, nmap_options, command=None):
        self.nmap_options = nmap_options
        self.command = command
        self.args = self.prepare_args()
        self.ip_addresses = [nmap_options['target']]
        self.chatbot = None

    def display_welcome_message(self):
        """
        Displays the welcome message with the current date and time.

        Parameters:
        None

        Returns:
        None
        """
        print("\n\nWelcome to the Nmap Port Scanner Project!\n\n")
        print("Today's date and time: ", datetime.datetime.now(), " GMT.\n\n")

    def prepare_args(self):
        """
        Prepares and returns the command line arguments for the pipeline.

        Parameters:
        None

        Returns:
        args: Namespace object containing the command line arguments.
        """
        args = PipelineUtils.get_args()
        args.type = "json"
        args.model = "lmstudio"
        args.path = "nmap_project/documentation.json"
        args.system_prompt_template = (
            "You are a professional penetration testing expert."
            "You must scan host of provided IP addresses for vulnerabilities."
            "You must find ways to exploit these vulnerabilities."
            "If methods fail, you must suggest alternative methods."
            "You must write shell commands that perform these tasks."
            "Format your response as a JSON object containing a list of commands."
            "The JSON object should have a key 'commands' which maps to a list of objects."
            "Exclude any additional text or information from your response."
        )
        args.output_type = "json"
        args.collection_name = secrets.token_hex(16)
        return args

    def scan_ip_address(self):
        """
        Scans a provided IP address and returns the results.

        Parameters:
        None

        Returns:
        result (dict): The result of the Nmap scan.
        """
        nmap_scanner = NmapScanner(**self.nmap_options)
        if self.command:
            nmap_scanner.run_command(self.command)
        else:
            nmap_scanner.run_nmap()
        nmap_scanner.parse_output()
        result = nmap_scanner.get_parsed_data()
        pprint(nmap_scanner.get_output())
        pprint(result)
        return result

    def process_ports(self, result):
        """
        Processes the scanned ports and searches for exploits.

        Parameters:
        result (dict): The result of the Nmap scan.

        Returns:
        list: A list of options dictionaries containing port details.
        """
        options_list = []
        for port in result['ports']:
            options = {
                "IP Address": self.nmap_options['target'],
                "Port Number": port['port'],
                "Service Name": port['service'],
                "Version": port['version'],
                "OS": result['os_info']
            }
            options_list.append(options)
        return options_list

    def search_exploits(self, version):
        """
        Searches for exploits based on the service version.

        Parameters:
        version (str): The version of the service being scanned.

        Returns:
        search_results (list): A list of search results from SearchSploit.
        """
        ss = SearchSploit()
        search_results = ss.search([version])
        pprint(search_results)
        return search_results

    def handle_chatbot(self, info, version):
        """
        Handles the chatbot interaction for vulnerability exploitation.

        Parameters:
        info (str): JSON formatted string with information about the target.
        version (str): The version of the service being scanned.

        Returns:
        response (dict): The response from the chatbot.
        """
        self.args.collection_name = secrets.token_hex(16)
        self.chatbot = PipelineUtils.create_chatbot(self.args)
        response = self.chatbot.invoke(f"""
        Information about the target: {info}.
        What will be the best way to exploit vulnerability on target?
        You must select right tool or tools from list to identify vulnerabilities of Version: '{version}' service.:
        1: nmap
        2: sqlmap
        3: whatweb
        4: dirb
        5: gobuster
        6: hydra
        7: nikto
        8: wpscan
        If non of the tools are relevant, you may suggest other tools.
        Respond in pure JSON format.
        The response should follow this format:
        {{
            "commands": [
                {{
                    "method": ....,
                    "description": ....,
                    "tool": ....,
                    "command": ...
                }},
                {{
                    "method": ....,
                    "description": ....,
                    "tool": ....,
                    "command": ...
                }},
                etc...
            ]
        }}
        """)
        parsed_response = ChatbotUtils.parse_json(response)
        pprint(parsed_response)
        self.chatbot.clear_chat_history()
        return parsed_response

    def handle_chatbot_vulnerability(self, info):
        """
        Handles the chatbot interaction for suggesting vulnerability proof of concept methods.

        Parameters:
        info (str): JSON formatted string with information about the target.

        Returns:
        response (dict): The response from the chatbot.
        """
        self.args.collection_name = secrets.token_hex(16)
        self.chatbot = PipelineUtils.create_chatbot(self.args)
        response = self.chatbot.invoke(f"""
        You must suggest vulnerability proof of concept method.
        Information about the target: {info}.
        The installed tools at the moment are:
        - nmap
        - sqlmap
        - whatweb
        - dirb
        - gobuster
        - hydra
        - nikto
        - wpscan
        - ncat
        - hashcat
        - john
        - searchsploit
        You must choose the tools which are relevant to target.
        You may suggest tools that are not in the list but still relevant to target.
        Respond in pure JSON format.
        The JSON object should have a key 'commands' which maps to a list of objects.
        Each object should have the following keys:
        - 'method': The suggested pentesting method
        - 'description': A description of the suggested pentesting method
        - 'tool': The tool used to perform the pentesting method
        - 'command': The tool command including the parameters and target and any other necessary information
        The response should follow this format:
        {{
            "commands": [
                {{
                    "method": ....,
                    "description": ....,
                    "tool": ....,
                    "command": ...
                }},
                {{
                    "method": ....,
                    "description": ....,
                    "tool": ....,
                    "command": ...
                }},
                etc...
            ]
        }}
        """)
        parsed_response = ChatbotUtils.parse_json(response)
        pprint(parsed_response)
        self.chatbot.clear_chat_history()
        return parsed_response

    def run(self):
        """
        The main function that orchestrates the Nmap Port Scanner Project.

        Parameters:
        None

        Returns:
        None
        """
        self.display_welcome_message()
        scan_result = self.scan_ip_address()
        options_list = self.process_ports(scan_result)
        for options in options_list:
            # info = json.dumps(options, indent=4)
            self.search_exploits(options["Version"])
            # self.handle_chatbot(info, options["Version"])
            # self.handle_chatbot_vulnerability(info)


def main():
    """

    """
    nmap_options = {
        'target': '172.28.128.3',
        'firewall': False,
        'flags': '-sV -O -T5',
        'ports': None,
        'script': None
    }
    command = None  # or provide a specific nmap command here if needed
    project = NmapPortScannerProject(nmap_options, command)
    project.run()


if __name__ == "__main__":
    main()
