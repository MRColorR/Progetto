import argparse
import pandas as pd
import matplotlib.pyplot as plt

def get_stats(data):
    """
    Calculate the median, mean, max, and min of the CPU and memory usage.
    """
    cpu_median = data["cpu_usage_avg"].median()
    cpu_mean = data["cpu_usage_avg"].mean()
    cpu_max = data["cpu_usage_avg"].max()
    cpu_min = data["cpu_usage_avg"].min()

    mem_median = data["memory_usage_avg"].median()
    mem_mean = data["memory_usage_avg"].mean()
    mem_max = data["memory_usage_avg"].max()
    mem_min = data["memory_usage_avg"].min()

    return [cpu_median, cpu_mean, cpu_max, cpu_min, mem_median, mem_mean, mem_max, mem_min]

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
        box = filtered_data.boxplot(column="cpu_usage_avg", ax=ax[0], positions=[i], return_type="dict")
        stats = get_stats(filtered_data)
        ax[0].text(i+0.22, stats[2]+2, "max: {:.2f}".format(stats[2]), horizontalalignment='center', color='red')
        ax[0].text(i+0.22, stats[0]-7, "median: {:.2f}".format(stats[0]), horizontalalignment='center', color='green')
        ax[0].text(i+0.22, stats[1]+3, "mean: {:.2f}".format(stats[1]), horizontalalignment='center', color='orange')
        ax[0].text(i+0.22, stats[3]-7, "min: {:.2f}".format(stats[3]), horizontalalignment='center', color='blue')

        # Calculate the mean value for the CPU usage
        cpu_mean = filtered_data["cpu_usage_avg"].mean()
        cpu_thresholds.append(i)
        cpu_means.append(cpu_mean)

    # Add the line connecting the mean values of the CPU usage
    ax[0].plot(cpu_thresholds, cpu_means, marker='o', color='orange')

    # Set the x-axis labels
    ax[0].set_xticklabels(unique_thresholds)
    ax[0].set_xticks(range(len(unique_thresholds)))
    ax[0].set_xticklabels(["hpa_cpu_treshold: {}".format(int(x)) for x in unique_thresholds])

    # Draw the boxplots of the memory usage
    mem_thresholds = []
    mem_means = []
    for i, hpa_cpu_threshold in enumerate(unique_thresholds):
        # Filter the data for the current hpa_cpu_threshold
        filtered_data = data[data["hpa_cpu_threshold"] == hpa_cpu_threshold]

        # Draw the boxplot of the memory usage
        box = filtered_data.boxplot(column="memory_usage_avg", ax=ax[1], positions=[i], return_type="dict")
        stats = get_stats(filtered_data)
        ax[1].text(i+0.22, stats[6]+0.1, "max: {:.2f}".format(stats[6]), horizontalalignment='center', color='red')
        ax[1].text(i+0.22, stats[4]+0.1, "median: {:.2f}".format(stats[4]), horizontalalignment='center', color='green')
        ax[1].text(i+0.22, stats[5]+0.2, "mean: {:.2f}".format(stats[5]), horizontalalignment='center', color='orange')
        ax[1].text(i+0.22, stats[7]-0.1, "min: {:.2f}".format(stats[7]), horizontalalignment='center', color='blue')

        # Calculate the mean value for the memory usage
        mem_mean = filtered_data["memory_usage_avg"].mean()
        mem_thresholds.append(i)
        mem_means.append(mem_mean)

    # Add the line connecting the mean values of the memory usage
    ax[1].plot(mem_thresholds, mem_means, marker='o', color='orange')



    # Set the x-axis labels
    ax[1].set_xticklabels(unique_thresholds)
    ax[1].set_xticks(range(len(unique_thresholds)))
    ax[1].set_xticklabels(["hpa_cpu_treshold: {}".format(int(x)) for x in unique_thresholds])
    # Set the titles of the boxplots
    ax[0].set_title("CPU Usage")
    ax[1].set_title("Memory Usage")

    # Add labels to the y-axis of the boxplots
    ax[0].set_ylabel("CPU Usage (average in mCores)")
    ax[1].set_ylabel("Memory Usage (average in MB)")

    # Save the figure as a SVG file
    plt.savefig("deployment_metrics_summary.svg")

if __name__ == "__main__":
    main()

