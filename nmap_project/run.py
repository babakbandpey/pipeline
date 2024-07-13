import datetime
import subprocess
import secrets
from pprint import pprint
from pipeline import PipelineUtils, ChatbotUtils, logger, NmapScanner


def main():
    """
    The main function.
    """
    # write the date and the time of the conversation
    print("\n\nWelcome to the chatbot!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), "\n\n")

    next_prompt = None

    args = PipelineUtils.get_args()
    args.type = "json"
    args.model = "lmstudio"
    args.path = "nmap_project/documentation.json"

    ip_addresses = [
        '172.28.128.3',
        # '192.168.56.4'
    ]

    args.system_prompt_template = " ".join((
        "You are a network administrator who has to use the nmap to scan the network.",
        "You need to write the namp shell commands that scans the ports of the provided IP addresses."
        "Format your response as a JSON object that contains a list of commands for scanning IP addresses using nmap."
        "The JSON object should have a key commands which maps to a list of objects."
        "Each object should contain two keys: ip_address with the IP address as its value, and command with the corresponding nmap command as its value."
        "each command must start with nmap followed by the IP address and the necessary flags to scan the ports of the IP address."
        "Format your resposne as JSON object.",
        "The json object must only have two keys: commands and command.",
        "Each command must start with nmap followed by the IP address and the necessary flags to scan the ports of the IP address.",
        "Omit any other text in the response.",
    ))

    args.output_type = "json"

    chatbot = PipelineUtils.create_chatbot(args)

    try:
        # while True:
        #     next_prompt = PipelineUtils.handle_command(
        #         input("\n** Enter your message: ") if next_prompt is None else next_prompt,
        #         chatbot
        #     )
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
                    pprint(port)
                    info = f"[Port: {port['port']}, Service: {port['service']}, Version: {port['version']}, OS: {result['os_info']}]"
                    args.collection_name = secrets.token_hex(16)
                    _chatbot = PipelineUtils.create_chatbot(args)
                    response = _chatbot.invoke(f"""
                    Suggest a pentesting method for {info}. respond in pure JSON format.
                    The reponse should resemble the following format:
                    {{
                        "suggestion": {{
                            "method": "The suggested pentesting method"
                            "description": "The description of the suggested pentesting method",
                            "tools": ["Tool 1", "Tool 2", "Tool 3"]
                            "examples": ["list of real life examples of using the tool on Port: '{port['port']}', Service: '{port['service']}', Version: '{port['version']}', OS: '{result['os_info']}'", ...]
                        }}
                    }}
                    each example must be a dict with the key "command": "The command used to run the tool"
                    """)
                    pprint(ChatbotUtils.parse_json(response))

                    _chatbot.delete_collection()

    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")


if __name__ == "__main__":
    main()
