import argparse
import time
import csv
import os

# Import the kubernetes client library
from kubernetes import client, config

def get_metrics(namespace, deployment_name):
    """
    Retrieve the average CPU and memory usage for a deployment.
    
    Parameters:
        namespace (str): The namespace of the deployment.
        deployment_name (str): The name of the deployment.
    
    Returns:
        tuple: A tuple containing the average CPU usage and average memory usage.
    """
    # Create an instance of the CustomObjectsApi
    api = client.CustomObjectsApi()
    
    try:
        # Get the custom resource for pods in the specified namespace
        resource = api.list_namespaced_custom_object(
            group="metrics.k8s.io", version="v1beta1", namespace=namespace, plural="pods"
        )
        
        # Initialize the CPU and memory usage
        cpu_usage = 0
        memory_usage = 0
        
        # Iterate over the pods
        for pod in resource["items"]:
            # Check if the pod name starts with the deployment name
            if pod['metadata']['name'].startswith(deployment_name):
                # Iterate over the containers in the pod
                for container in pod["containers"]:
                    # Add the CPU usage of the container to the total
                    cpu_usage += float(container["usage"].get("cpu", 0).rstrip("n")) / 1000000
                    # Add the memory usage of the container to the total
                    memory_usage += float(container["usage"].get("memory", 0).rstrip("Ki")) / 1000
        
        # Return the average CPU and memory usage
        return cpu_usage / len(resource["items"]), memory_usage / len(resource["items"])
    except Exception as e:
        print(e)
        return None, None

def get_hpa_params(namespace, deployment_name):
    """
    Retrieve the HPA CPU averageUtilization threshold and scaleDown stabilizeWindowSeconds for a deployment.
    
    Parameters:
        namespace (str): The namespace of the deployment.
        deployment_name (str): The name of the deployment.
    
    Returns:
        tuple: A tuple containing the CPU averageUtilization threshold and the scaleDown stabilizeWindowSeconds.
    """
    # Create an instance of the AutoscalingV1Api
    api = client.AutoscalingV1Api()
    
    try:
        # Get the HPA for the specified deployment
        hpa = api.read_namespaced_horizontal_pod_autoscaler(name=deployment_name, namespace=namespace)
        
        # Retrieve the CPU averageUtilization threshold and scaleDown stabilizeWindowSeconds
        cpu_threshold = hpa.spec.metrics[0].resource.target.average_utilization
        scale_down_window = hpa.spec.scale_down_stabilization_window_seconds
        
        # Return the CPU averageUtilization threshold and scaleDown stabilizeWindowSeconds
        return cpu_threshold, scale_down_window
    except Exception as e:
        print(e)
        return None, None


def main():
    """
    Main function to retrieve metrics for a Kubernetes deployment.
    """
    # Define the command-line arguments
    parser = argparse.ArgumentParser(description="Retrieve metrics for a Kubernetes deployment")
    parser.add_argument("--namespace", type=str, default="default", help="The namespace of the deployment")
    parser.add_argument("--deployment_name", type=str, required=True, help="The name of the deployment")
    parser.add_argument("--filename", type=str, default="deployment_metrics.csv", help="The output file name")
    parser.add_argument("--kubeconfig", type=str, default="kube_config.yaml", help="The kubernetes cluster configuration file name")
    parser.add_argument("--sleep_time", type=int, default=15, help="The sleep time between metrics requests")
    parser.add_argument("--observation_time", type=int, default=300, help="The time to observe metrics, in seconds")
    parser.add_argument("--append", action='store_true', help="Append to the existing output file")
    args = parser.parse_args()

    # Retrieve the values of the command-line arguments
    namespace = args.namespace
    deployment_name = args.deployment_name
    filename = args.filename
    kubeconfig = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.kubeconfig)
    sleep_time = args.sleep_time
    observation_time = args.observation_time

    config.load_kube_config(config_file=kubeconfig)

    # Define the headers for the output file
    headers = ["timestamp", "cpu_usage_avg", "memory_usage_avg"]
    # Determine the mode in which to open the file (append or write)
    mode = "a" if args.append else "w"
    with open(filename, mode) as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if mode == "w":
            writer.writeheader()
        
        # Calculate the number of iterations needed to observe metrics for the specified time
        iterations = observation_time // sleep_time

        # Loop for the number of iterations, retrieving metrics and writing them to the file
        for i in range(iterations):
            cpu_usage, memory_usage = get_metrics(namespace, deployment_name)
            if cpu_usage is None or memory_usage is None:
                print("Failed to retrieve metrics, retrying in {} seconds".format(sleep_time))
            else:
                row = {
                    "timestamp": time.time(),
                    "cpu_usage_avg": cpu_usage,
                    "memory_usage_avg": memory_usage
                }
                writer.writerow(row)
                print("Wrote metrics to file: {}".format(row))
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()