"""
This is the main file that runs the Nmap Port Scanner Project.
"""

import datetime
import json
import secrets
import sys
from pprint import pprint
from pipeline import PipelineUtils, ChatbotUtils, logger, NmapScanner


def main():
    """
    The main function.
    """
    # write the date and the time of the conversation
    print("\n\nWelcome to the Nmap Port Scanner Project!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), " GMT.\n\n")

    args = PipelineUtils.get_args()
    args.type = "json"
    args.model = "lmstudio"
    args.path = "nmap_project/documentation.json"

    ip_addresses = [
        '172.28.128.3',
        # '192.168.56.4'
    ]

    args.system_prompt_template = (
        "You are a professional peneteration testing expert."
        "You must scan host of provided IP addresses for vulnerabilies."
        "You must find ways to exploit these vulnerabilities."
        "If methods fails, you must suggest alternative methods."
        "You must write shell commands that perform these tasks."
        "Format your response as a JSON object containing a list of commands."
        "The JSON object should have a key 'commands' which maps to a list of objects."
        "Exclude any additional text or information from your response."
    )

    args.output_type = "json"
    args.collection_name = secrets.token_hex(16)
    chatbot = PipelineUtils.create_chatbot(args)

    try:
        for ip_address in ip_addresses:
            response = chatbot.invoke(f"""
            Write the one command for namp scanning of all the ports -p-, services, version of the services and the OS type and version on Ip Addresses : ({ip_address}).
            the response should resemble the following format:
            {{
                "commands": [
                    {{
                        "command": "nmap [the necessary flags or scripts] {ip_address}"
                        "ports": "[if needed: string of ports seperated by comma or hyphen|None]",
                        "flags": "[string of flags]",
                        "target": "{ip_address}",
                        "firewall": "[if needed: true|false]",
                        "script": "[if needed: {{script_name: script_path, ...}}|None]"
                    }}
                ]
            }}
            """)

            response_json = ChatbotUtils.parse_json(response)

            pprint(response_json)

            # Zero out the path so that the chatbot doesn't try to read from it
            args.path = None
            # changing to simple chatbot
            args.type = "chat"

            for command in response_json['commands']:
                logger.info(command['command'])
                # command['firewall'] = True
                command['flags'] += " -T5 "
                nmap_scanner = NmapScanner(**command)
                nmap_scanner.run_command(command['command'])
                # nmap_scanner.run_nmap()
                logger.info(nmap_scanner.parse_output())
                logger.info("Nmap scan output:")
                result = nmap_scanner.get_parsed_data()
                pprint(nmap_scanner.get_output())
                pprint(result)



                for port in result['ports']:
                    options = {
                        "IP Address": ip_address,
                        "Port Number": port['port'],
                        "Service Name": port['service'],
                        "Version": port['version'],
                        "OS": result['os_info']
                    }
                    logger.info(options)
                    info = json.dumps(options, indent=4)

                    args.collection_name = secrets.token_hex(16)
                    _chatbot = PipelineUtils.create_chatbot(args)
                    response = _chatbot.invoke(f"""
                    What will be the best way to exploit the vulnerability on the target?
                    Information about the target: {info}.
                    Sugget necessary tools and commands to exploit the vulnerability.
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
                    pprint(ChatbotUtils.parse_json(response))
                    _chatbot.clear_chat_history()
                    sys.exit()
                    continue



                    args.collection_name = secrets.token_hex(16)
                    _chatbot = PipelineUtils.create_chatbot(args)
                    response = _chatbot.invoke(f"""
                    You must suggest vulnerability proof of concept method.
                    Information about the target: {info}.
                    The installed tools at the moment are:
                    - nmap
                    - sqlmap
                    - whatweb
                    - dirb
                    - gobuster
                    - hydra
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
                    pprint(ChatbotUtils.parse_json(response))
                    _chatbot.clear_chat_history()

    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")


if __name__ == "__main__":
    main()
