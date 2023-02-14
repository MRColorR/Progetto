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
    
    # Loop over the unique values of the hpa_cpu_threshold
    for hpa_cpu_threshold in unique_thresholds:
        # Filter the data for the current hpa_cpu_threshold
        filtered_data = data[data["hpa_cpu_threshold"] == hpa_cpu_threshold]
        
        # Draw the boxplots of the CPU and memory usage
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))
        filtered_data.boxplot(column="cpu_usage_avg", ax=ax[0])
        filtered_data.boxplot(column="memory_usage_avg", ax=ax[1])
        
        # Set the titles of the boxplots
        ax[0].set_title("CPU Usage")
        ax[1].set_title("Memory Usage")

        # Add labels to the y-axis of the boxplots
        ax[0].set_ylabel("CPU Usage (average in mCores)")
        ax[1].set_ylabel("Memory Usage (average in MB)")
        
        # Calculate the median, mean, max, and min values
        cpu_median = filtered_data["cpu_usage_avg"].median()
        cpu_mean = filtered_data["cpu_usage_avg"].mean()
        cpu_max = filtered_data["cpu_usage_avg"].max()
        cpu_min = filtered_data["cpu_usage_avg"].min()
        mem_median = filtered_data["memory_usage_avg"].median()
        mem_mean = filtered_data["memory_usage_avg"].mean()
        mem_max = filtered_data["memory_usage_avg"].max()
        mem_min = filtered_data["memory_usage_avg"].min()
        
        # Display the median, mean, max, and min values for the CPU usage
        ax[0].text(x=1.1, y=cpu_median, s="Median: {:.2f}".format(cpu_median), color='blue')
        ax[0].text(x=1.1, y=cpu_mean, s="Mean: {:.2f}".format(cpu_mean), color='orange')
        ax[0].text(x=1.1, y=cpu_max, s="Max: {:.2f}".format(cpu_max), color='red')
        ax[0].text(x=1.1, y=cpu_min, s="Min: {:.2f}".format(cpu_min), color='green')

        # Display the median, mean, max, and min values for the memory usage
        ax[1].text(x=1.1, y=mem_median, s="Median: {:.2f}".format(mem_median), color='blue')
        ax[1].text(x=1.1, y=mem_mean, s="Mean: {:.2f}".format(mem_mean), color='orange')
        ax[1].text(x=1.1, y=mem_max, s="Max: {:.2f}".format(mem_max), color='red')
        ax[1].text(x=1.1, y=mem_min, s="Min: {:.2f}".format(mem_min), color='green')
        
        # Save the figure as a SVG file
        postfix = "_threshold_{}".format(int(hpa_cpu_threshold))
        plt.savefig("deployment_metrics{}.svg".format(postfix))


if __name__ == "__main__":
    main()

