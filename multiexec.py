# Execute a command on all pods
# Example: Run nvidia-smi on all pods in staging
# $ python3 multiexec.py -n staging -- nvidia-smi --query-compute-apps=pid,used_memory --format=csv

import argparse
import dataclasses
from itertools import groupby
from typing import List
import subprocess
import sys


@dataclasses.dataclass()
class Pod:
    namespace: str
    name: str
    node_name: str


def multiexec(
    pod_filters: List[str], exec_command: List[str], once_per_node: bool
) -> None:
    """Executes an `exec_command` in all pods matching the pod_filters criteria."""
    x = (
        'jsonpath="{range .items[*]}'
        "{@.metadata.namespace}, "
        "{@.metadata.name}, "
        "{@.spec.nodeName}"
        '\n{end}"'
    )
    pods = [
        Pod(*x.split(", "))
        for x in subprocess.run(
            ["kubectl", "get", "pods", *pod_filters, "-o", x], capture_output=True
        )
        .stdout.decode("utf-8")[1:-1]
        .split("\n")[:-1]
    ]
    for node, pods in groupby(pods, lambda x: x.node_name):
        print(f"\u001b[1m{node}\u001b[0m")
        for pod in pods:
            desired_command = [
                "kubectl",
                "exec",
                "-it",
                "-n",
                pod.namespace,
                pod.name,
                "--",
                *exec_command,
            ]
            output = subprocess.run(
                desired_command,
                capture_output=True,
            )
            print("$ " + " ".join(desired_command))
            if output.stdout:
                print(f"\u001b[32m{output.stdout.decode('utf-8')}\u001b[0m")
                if once_per_node:
                    break
            else:
                print(f"\u001b[31m{output.stderr.decode('utf-8')}\u001b[0m")


def main():
    parser = argparse.ArgumentParser(description="Execute a command in every pod")
    parser.add_argument("--once-per-node", action="store_true")
    params, unknown = parser.parse_known_args()
    if "--" not in unknown:
        print("Please pass a command with -- `my command`")
        exit(1)
    split = unknown.index("--")

    multiexec(unknown[:split], unknown[split + 1 :], once_per_node=params.once_per_node)


if __name__ == "__main__":
    exit(main())
