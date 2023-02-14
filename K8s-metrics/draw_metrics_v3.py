import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main():
    """
    Main function to draw boxplots of the CPU and memory usage.
    """
    # Define the command-line arguments
    parser = argparse.ArgumentParser(description="Draw boxplots of the CPU and memory usage")
    parser.add_argument("--filename", type=str, default="deployment_metrics.csv", help="The input file name")
    args = parser.parse_args()

    # Load the data from the CSV file
    data = pd.read_csv(args.filename)
    
    # Get the unique values of the hpa_cpu_threshold
    unique_thresholds = data["hpa_cpu_threshold"].unique()
    
    # Draw the boxplots of the CPU usage
    fig, ax = plt.subplots(2, 1, figsize=(10, 10))
    cpu_thresholds = []
    cpu_means = []
    for i, hpa_cpu_threshold in enumerate(unique_thresholds):
        # Filter the data for the current hpa_cpu_threshold
        filtered_data = data[data["hpa_cpu_threshold"] == hpa_cpu_threshold]
        
        # Draw the boxplot of the CPU usage
        filtered_data.boxplot(column="cpu_usage_avg", ax=ax[0], positions=[i])
        
        # Calculate the mean value for the CPU usage
        cpu_mean = filtered_data["cpu_usage_avg"].mean()
        cpu_thresholds.append(i)
        cpu_means.append(cpu_mean)
        
    # Add the line connecting the mean values of the CPU usage
    ax[0].plot(cpu_thresholds, cpu_means, marker='o', color='red')

    # Set the x-axis labels
    ax[0].set_xticklabels(unique_thresholds)
    ax[0].set_xticks(range(len(unique_thresholds)))
    ax[0].set_xticklabels(["HPA_CPU_Threshold: {}".format(int(x)) for x in unique_thresholds])

    # Draw the boxplots of the memory usage
    mem_thresholds = []
    mem_means = []
    for i, hpa_cpu_threshold in enumerate(unique_thresholds):
        # Filter the data for the current hpa_cpu_threshold
        filtered_data = data[data["hpa_cpu_threshold"] == hpa_cpu_threshold]
        
        # Draw the boxplot of the memory usage
        filtered_data.boxplot(column="memory_usage_avg", ax=ax[1], positions=[i])
        
        # Calculate the mean value for the memory usage
        mem_mean = filtered_data["memory_usage_avg"].mean()
        mem_thresholds.append(i)
        mem_means.append(mem_mean)
        
    # Add the line connecting the mean values of the memory usage
    ax[1].plot(mem_thresholds, mem_means, marker='o', color='red')

    # Set the x-axis labels
    ax[1].set_xticklabels(unique_thresholds)
    ax[1].set_xticks(range(len(unique_thresholds)))
    ax[1].set_xticklabels(["HPA_CPU_Threshold: {}".format(int(x)) for x in unique_thresholds])
    # Set the titles of the boxplots
    ax[0].set_title("CPU Usage")
    ax[1].set_title("Memory Usage")

    # Add labels to the y-axis of the boxplots
    ax[0].set_ylabel("CPU Usage (average in mCores)")
    ax[1].set_ylabel("Memory Usage (average in MB)")

    # Initialize lists to store the mean values of the CPU and memory usage
    cpu_mean_values = []
    mem_mean_values = []

    # Loop over the unique values of the hpa_cpu_threshold
    for hpa_cpu_threshold in unique_thresholds:
        # Filter the data for the current hpa_cpu_threshold
        filtered_data = data[data["hpa_cpu_threshold"] == hpa_cpu_threshold]
        
        # Calculate the mean values of the CPU and memory usage
        cpu_mean = filtered_data["cpu_usage_avg"].mean()
        mem_mean = filtered_data["memory_usage_avg"].mean()
        
        # Append the mean values to the lists
        cpu_mean_values.append(cpu_mean)
        mem_mean_values.append(mem_mean)


    # Save the figure as a SVG file
    postfix = "_threshold_{}".format(int(hpa_cpu_threshold))
    plt.savefig("deployment_metrics{}.svg".format(postfix))

if __name__ == "__main__":
    main()
