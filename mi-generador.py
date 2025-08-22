import sys

class DockerYamlGenerator:
    def __init__(self, clients: int):
        self.filename = "docker-compose-dev.yaml"
        self.clients = clients

    def _generate_string(self) -> str:
        file_start: str = """\
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
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
    environment:
      - CLI_ID=1
      - CLI_LOG_LEVEL=DEBUG
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
    clients_input: int = sys.argv[2] if len(sys.argv) > 2 else "1"

    generator: DockerYamlGenerator = DockerYamlGenerator(clients=int(clients_input))
    generator.generate()

main()