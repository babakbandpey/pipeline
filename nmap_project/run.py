import datetime
import subprocess
from pipeline import PipelineUtils, ChatbotUtils


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
    # args.model = "llama3"
    args.path = "nmap_project/documentation.json"

    ip_addresses = [
        '172.28.128.3',
        '192.168.56.4'
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
        "Omit any other text in the response."
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
            reponse = chatbot.invoke(f"""
            Write the commands for namp scanning og all the open ports, services, version of the services but not OS on Ip Addresses : ({ip_address}).
            the response should resemble the following format:
            {{
                "commands": [
                    {{
                        "ip_address": "{ip_address}",
                        "command": "nmap [the necessary flags or scripts] {ip_address}"
                    }}
                ]
            }}

            enclose the json in ```json {{JSON_RESPONSE}} ```
            do not include any other text in the response.
            """)

            response_json = ChatbotUtils.parse_json(reponse)

            print(response_json)

            for command in response_json['commands']:
                print(command['command'])
                result = subprocess.run(command['command'], shell=True, check=True)
                print(result.stdout)
                print(result.stderr)

        exit(0)
        # Write the generated code to a file
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"nmap_project/nmap_script_{timestamp}.sh"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(commands)

        # Execute the generated script
        result = subprocess.run(['bash', filename], capture_output=True, text=True, check=True)

        # Print the output of the script
        print(result.stdout)
        print(result.stderr)

    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")


if __name__ == "__main__":
    main()
