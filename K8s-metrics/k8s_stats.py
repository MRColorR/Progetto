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
        
        # Return the average CPU and memory usage
        return cpu_usage / len(resource["items"]), memory_usage / len(resource["items"])
    except Exception as e:
        print(e)
        return None, None

def get_hpa_cpu_threshold(namespace, deployment_name):
    """
    Retrieve the CPU utilization threshold for an HPA.
    
    Parameters:
        namespace (str): The namespace of the deployment.
        deployment_name (str): The name of the deployment.
    
    Returns:
        float: The CPU utilization threshold.
    """
    # Create an instance of the AutoscalingV2Api
    api = client.AutoscalingV2Api()
    
    try:
        # Get the HorizontalPodAutoscaler for the deployment
        hpa = api.read_namespaced_horizontal_pod_autoscaler(
            name=deployment_name, namespace=namespace
        )
        #print("hpa:", hpa)  # Debugging line
        # Get the CPU utilization threshold from the HPA
        if hpa.spec.metrics and hpa.spec.metrics[0].type == "Resource":
            hpa_cpu_threshold = hpa.spec.metrics[0].resource.target.average_utilization
        else:
            hpa_cpu_threshold = None
        
        #print("hpa_cpu_threshold:", hpa_cpu_threshold)  # Debugging line
        
        return hpa_cpu_threshold
    except Exception as e:
        print(e)
        return None

def get_replicas(namespace, deployment_name):
    """
    Retrieve the current replicas number for a deployment.
    
    Parameters:
        namespace (str): The namespace of the deployment.
        deployment_name (str): The name of the deployment.
    
    Returns:
        int: The current replicas number.
    """
    # Create an instance of the AppsV1Api
    api = client.AppsV1Api()
    
    try:
        # Get the deployment
        deployment = api.read_namespaced_deployment(
            name=deployment_name, namespace=namespace
        )
        # Get the current replicas number from the deployment
        replicas = deployment.spec.replicas
        
        return replicas
    except Exception as e:
        print(e)
        return None

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
    headers = ["timestamp", "cpu_usage_avg", "memory_usage_avg", "hpa_cpu_threshold", "replicas"]
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
            hpa_cpu_threshold = get_hpa_cpu_threshold(namespace, deployment_name)
            replicas = get_replicas(namespace, deployment_name)
            # Check if CPU usage, memory usage, HPA CPU threshold, or replicas is None
            if cpu_usage is None or memory_usage is None or hpa_cpu_threshold is None or replicas is None:
                print("Failed to retrieve metrics, retrying in {} seconds".format(sleep_time))
            else:
                # Create a dictionary with the metrics
                row = {
                    "timestamp": time.time(),
                    "cpu_usage_avg": cpu_usage,
                    "memory_usage_avg": memory_usage,
                    "hpa_cpu_threshold": hpa_cpu_threshold,
                    "replicas": replicas
                }
                # Write the metrics to the file
                writer.writerow(row)
                print("Wrote metrics to file: {}".format(row))
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()
