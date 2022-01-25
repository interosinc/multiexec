# multiexec
Simple utility for running a `kubectl exec` across multiple Pods.

## Usage
Call the script with your Pod filters (passed thru to `kubectl get pods`) and your command (passed thru to `kubectl exec -it`) as follows:

```sh
$ multiexec <POD FILTERS> -- <EXEC COMMAND>
```

pass `--once-per-node` to only run the command in a single Pod on each node


## Examples

### Say hello in every Pod on a given node
```sh
$ multiexec --all-namespaces --field-selector spec.nodeName=ip-1-2-3-4.ec2.internal -- /bin/bash -c "echo hello"

ip-1-2-3-4.ec2.internal
$ kubectl exec -it -n namespaceA some-pod-46vp8 -- /bin/bash -c echo hello
hello

$ kubectl exec -it -n namespaceB another-pod-fcvmq -- /bin/bash -c echo hello
hello

$ kubectl exec -it -n namespaceC foo-app-l95cj -- /bin/bash -c echo hello
hello

$ kubectl exec -it -n namespaceD bar-app-6zzb8 -- /bin/bash -c echo hello
hello
```


### Get GPU RAM usage via nvidia-smi on each node in namespaceA
```sh
$ multiexec --once-per-node -n namespaceA -- nvidia-smi --query-compute-apps=pid,used_memory --format=csv        

ip-1-2-3-4.ec2.internal
$ kubectl exec -it -n namespaceA foo-app-1 -- nvidia-smi --query-compute-apps=pid,used_memory --format=csv
pid, used_gpu_memory [MiB]
5276, 25 MiB
4860, 2437 MiB

ip-2-3-4-5.ec2.internal
$ kubectl exec -it -n namespaceA bar-app-2 -- nvidia-smi --query-compute-apps=pid,used_memory --format=csv
pid, used_gpu_memory [MiB]
12201, 25 MiB
11509, 2539 MiB
14466, 3713 MiB

ip-3-4-5-6.ec2.internal
$ kubectl exec -it -n namespaceA foo-app-2 -- nvidia-smi --query-compute-apps=pid,used_memory --format=csv
pid, used_gpu_memory [MiB]
20570, 25 MiB
19846, 2157 MiB
14641, 2149 MiB

ip-4-5-6-7.ec2.internal
$ kubectl exec -it -n namespaceA bar-app-1 -- nvidia-smi --query-compute-apps=pid,used_memory --format=csv
pid, used_gpu_memory [MiB]
23317, 25 MiB
7236, 4501 MiB
30002, 1009 MiB
```
