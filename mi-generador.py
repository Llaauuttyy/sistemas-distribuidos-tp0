import sys

class DockerYamlGenerator:
    def __init__(self, filename: str, clients: int):
        self.filename = filename
        self.clients = clients

    def _generate_string(self) -> str:
        file_start: str = """\
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    volumes:
      - ./server/config.ini:/config.ini
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - testing_net
""" 

        clients: str = ""

        for i in range(self.clients):
            clients += f"""
  client{i + 1}:
    container_name: client{i + 1}
    image: client:latest
    entrypoint: /client
    volumes:
      - ./client/config.yaml:/config.yaml
    environment:
      - CLI_ID=1
    networks:
      - testing_net
    depends_on:
      - server
"""

        file_end: str = """
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

        return file_start + clients + file_end

    def _save(self, content: str) -> None:
        with open(self.filename, "w") as file:
            file.write(content)
    
    def generate(self) -> None:
        content: str = self._generate_string()
        self._save(content)

def main():
    if len(sys.argv) != 3:
        raise Exception("Missing params.")
    
    filename_input: str = sys.argv[1]
    clients_input: int = sys.argv[2]

    generator: DockerYamlGenerator = DockerYamlGenerator(filename=filename_input, clients=int(clients_input))
    generator.generate()

main()