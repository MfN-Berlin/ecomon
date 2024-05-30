import argparse
import os
from os import getenv

def generate_docker_compose(num_containers, output_filename):
    base_config = {
        "version": "3",
        "services": {}
    }

    for i in range(num_containers):
        service_name = f"birdid-{i}"
        base_config["services"][service_name] = {
            "cpuset": str(i + 1),
            "container_name": f"{getenv('MARIADB_DATABASE')}-{service_name}",
            "image": "birdid-europe254-2103-flask-v04",
            "restart": "always",
            "ipc": "host",
            "ports": [f"{9000 + i}:4000"],
            "volumes": [
                "${DATA_DIRECTORY}:/mnt/data",
                "${RESULT_DIRECTORY}:/mnt/result"
            ]
        }

    with open(output_filename, "w") as f:
        f.write("# docker-compose.yml\n")
        f.write("version: \"3\"\n")
        f.write("services:\n")

        for service, data in base_config["services"].items():
            f.write(f"   {service}:\n")
            for key, value in data.items():
                if key == "ports" or key == "volumes":
                    f.write(f"      {key}:\n")
                    for item in value:
                        f.write(f"         - \"{item}\"\n")
                else:
                    f.write(f"      {key}: \"{value}\"\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate docker-compose.yml file.")
    parser.add_argument("num_containers", type=int, help="Number of containers to create")
    parser.add_argument("output_filename", type=str, help="Output filename for the docker-compose.yml file")

    args = parser.parse_args()

    generate_docker_compose(args.num_containers, args.output_filename)
