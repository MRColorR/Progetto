import argparse
import time
import csv
import os

# Import the kubernetes client library
from kubernetes import client, config

def get_pod_metrics(namespace, pod_name):
    """
    Retrieve the CPU and memory usage for a specific pod.
    
    Parameters:
        namespace (str): The namespace of the pod.
        pod_name (str): The name of the pod.
    
    Returns:
        tuple: A tuple containing the CPU usage and memory usage.
    """
    # Create an instance of the CustomObjectsApi
    api = client.CustomObjectsApi()
    
    try:
        # Get the custom resource for the pod
        resource = api.get_namespaced_custom_object(
            group="metrics.k8s.io", version="v1beta1", name=pod_name, namespace=namespace, plural="pods"
        )

        # Initialize the CPU and memory usage
        cpu_usage = 0
        memory_usage = 0
        
        # Iterate over the containers in the pod
        for container in resource["containers"]:
            # Retrieve CPU usage value
            cpu_str = container["usage"].get("cpu", 0)
            # Add the CPU usage of the container to the total
            if cpu_str.endswith("n"):
                cpu_usage += float(cpu_str.rstrip("n")) / 1000000
            else:
                print(f"Could not parse CPU usage value: {cpu_str}")
            # Retrieve Memory usage value
            memory_str = container["usage"].get("memory", 0)
            # Add the memory usage of the container to the total
            if memory_str.endswith("Ki"):
                memory_usage += float(memory_str.rstrip("Ki")) / 1000
            elif memory_str.endswith("Mi"):
                memory_usage += float(memory_str.rstrip("Mi"))
            else:
                print(f"Could not parse memory usage value: {memory_str}")
        
        # Return the CPU and memory usage
        return cpu_usage, memory_usage
    except Exception as e:
        print(e)
        return None, None

def main():
    """
    Main function to retrieve metrics for a Kubernetes deployment and its pods.
    """
    # Define the command-line arguments
    parser = argparse.ArgumentParser(description="Retrieve metrics for a Kubernetes deployment and its pods")
    parser.add_argument("--namespace", type=str, default="default", help="The namespace of the deployment")
    parser.add_argument("--deployment_name", type=str, required=False, help="The name of the deployment")
    parser.add_argument("--kubeconfig", type=str, default="kube_config.yaml", help="The kubernetes cluster configuration file name")
    parser.add_argument("--sleep_time", type=int, default=15, help="The sleep time between metrics requests")
    parser.add_argument("--observation_time", type=int, default=300, help="The time to observe metrics, in seconds")
    parser.add_argument("--append", action='store_true', help="Append to the existing output files")
    parser.add_argument("--all_pods", action='store_true', help="Retrieve metrics for all pods regardless of the deployment")
    args = parser.parse_args()

    # Retrieve the values of the command-line arguments
    namespace = args.namespace
    deployment_name = args.deployment_name
    kubeconfig = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.kubeconfig)
    sleep_time = args.sleep_time
    observation_time = args.observation_time
    all_pods = args.all_pods

    config.load_kube_config(config_file=kubeconfig)
    
    # Create an instance of the CoreV1Api
    api = client.CoreV1Api()

    # Get all the pods in the namespace
    pods = api.list_namespaced_pod(namespace).items

    # If --all_pods is not specified, filter the pods to include only those belonging to the specified deployment
    if not all_pods and deployment_name is not None:
        pods = [pod for pod in pods if pod.metadata.name.startswith(deployment_name)]
    elif deployment_name is None and not all_pods:
        raise Exception("Either provide a deployment name or use the --all_pods option to get metrics for all pods.")

    # Determine the mode in which to open the files (append or write)
    mode = "a" if args.append else "w"

    # Calculate the number of iterations needed to observe metrics for the specified time
    iterations = observation_time // sleep_time

    # Loop for the number of iterations, retrieving metrics for each pod and writing them to the file
    for i in range(iterations):
        for pod in pods:
            cpu_usage, memory_usage = get_pod_metrics(namespace, pod.metadata.name)
            # Check if CPU usage or memory usage is None
            if cpu_usage is None or memory_usage is None:
                print(f"Failed to retrieve metrics for pod {pod.metadata.name}, retrying in {sleep_time} seconds")
            else:
                # Create a dictionary with the metrics
                row = {
                    "timestamp": time.time(),
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                }
                filename = f"{pod.metadata.name}_metrics.csv"
                with open(filename, mode) as f:
                    writer = csv.DictWriter(f, fieldnames=row.keys())
                    if mode == "w":
                        writer.writeheader()
                    # Write the metrics to the file
                    writer.writerow(row)
                    print(f"Wrote metrics to file for pod {pod.metadata.name}: {row}")
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()
