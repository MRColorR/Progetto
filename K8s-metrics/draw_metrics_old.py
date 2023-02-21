import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

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

def get_replicas_stats(data):
    """
    Calculate the median, mean, max, and min of the replicas.
    """
    replicas_median = data["replicas"].median()
    replicas_mean = data["replicas"].mean()
    replicas_max = data["replicas"].max()
    replicas_min = data["replicas"].min()

    return [replicas_median, replicas_mean, replicas_max, replicas_min]

def get_latency_stats(data):
    """
    Calculate the median, mean, max, and min of the latency.
    """
    latency_median = data["Latency"].median()
    latency_mean = data["Latency"].mean()
    latency_max = data["Latency"].max()
    latency_min = data["Latency"].min()

    return [latency_median, latency_mean, latency_max, latency_min]

def get_latency_data(hpa_cpu_threshold):
    """
    Returns a list of latency values from the JMeter test results CSV file.
    This code will loop through all the folders with names starting with REPORT_HTML{hpa_cpu_threshold} and ending with a number from 0 to 9 (i.e., REPORT_HTML50_0, REPORT_HTML50_9
    """
    data_list = []
    for i in range(10):
        # Create the file name
        filename = os.path.join("..", "JmeterLoadTest", "REPORT_HTML{}_{}".format(hpa_cpu_threshold, i), "results.csv")
        
        try:
            # Load the data from the CSV file
            data = pd.read_csv(filename)
            
            # Filter the data to include only the "HTTP Request API" rows
            filtered_data = data[(data["label"] == "HTTP Request API") & (data["responseCode"] == "200")]
            
            # Calculate the IQR of the latency data
            q1 = filtered_data["Latency"].quantile(0.25)
            q3 = filtered_data["Latency"].quantile(0.75)
            iqr = q3 - q1
            
            # Remove any data points that fall outside of the lower and upper bounds
            lower_bound = q1 - 1.5*iqr
            upper_bound = q3 + 1.5*iqr
            filtered_data = filtered_data[(filtered_data["Latency"] >= lower_bound) & (filtered_data["Latency"] <= upper_bound)]
            
            # Save the filtered data to a CSV file
            filtered_filename = os.path.join("..", "JmeterLoadTest", "REPORT_HTML{}_{}".format(hpa_cpu_threshold, i), "{}_{}_results.csv".format(hpa_cpu_threshold, i))
            filtered_data.to_csv(filtered_filename, index=False)
            
            data_list.append(filtered_data)
        except:
            continue
        
    if data_list:
        data = pd.concat(data_list)
        
        # Calculate the IQR of the latency data
        q1 = data["Latency"].quantile(0.25)
        q3 = data["Latency"].quantile(0.75)
        iqr = q3 - q1
        
        # Remove any data points that fall outside of the lower and upper bounds
        lower_bound = q1 - 1.5*iqr
        upper_bound = q3 + 1.5*iqr
        data = data[(data["Latency"] >= lower_bound) & (data["Latency"] <= upper_bound)]
    else:
        data = pd.DataFrame(columns=["Latency"])
    
    # Return the latency data
    return data





def main():
    """
    Main function to draw boxplots of the CPU and memory usage.
    """
    # Define the command-line arguments
    parser = argparse.ArgumentParser(description="Draw boxplots of the CPU and memory usage")
    parser.add_argument("--filename", type=str, default="deployment_metrics.csv", help="The input file name")
    parser.add_argument("--latency", action='store_true', help="Draw boxplots of the HTTP Request API latencies")
    parser.add_argument("--replicas", action='store_true', help="Draw boxplots of the HTTP Request API replicas")
    args = parser.parse_args()

    # Load the data from the CSV file
    data = pd.read_csv(args.filename)

    # Get the unique values of the hpa_cpu_threshold and sort it in ascending order
    unique_thresholds = np.sort(data["hpa_cpu_threshold"].unique())

    fontsize=7

    # Draw the boxplots of the CPU usage
    fig, ax = plt.subplots(2 + args.latency + args.replicas, 1, figsize=(12, 12))
    cpu_thresholds = []
    cpu_means = []
    for i, hpa_cpu_threshold in enumerate(unique_thresholds):
        # Filter the data for the current hpa_cpu_threshold
        filtered_data = data[data["hpa_cpu_threshold"] == hpa_cpu_threshold]

        # Calculate the interquartile range (IQR) and remove any data points that fall outside of the lower and upper bounds, defined as Q1 - 1.5IQR and Q3 + 1.5IQR, respectively
        cpu_q75 = filtered_data["cpu_usage_avg"].quantile(0.75)
        cpu_q25 = filtered_data["cpu_usage_avg"].quantile(0.25)
        cpu_iqr = cpu_q75 - cpu_q25
        cpu_min = cpu_q25 - 1.5 * cpu_iqr
        cpu_max = cpu_q75 + 1.5 * cpu_iqr
        filtered_data = filtered_data[(filtered_data["cpu_usage_avg"] >= cpu_min) & (filtered_data["cpu_usage_avg"] <= cpu_max)]


        # Draw the boxplot of the CPU usage
        box = filtered_data.boxplot(column="cpu_usage_avg", ax=ax[0], positions=[i], return_type="dict")
        stats = get_stats(filtered_data)
        ax[0].text(i+0.032*fontsize, stats[2]+0.45*fontsize, "max: {:.2f}".format(stats[2]), horizontalalignment='center', color='red', fontsize=fontsize)
        ax[0].text(i+0.032*fontsize, stats[0]-0.75*fontsize, "median: {:.2f}".format(stats[0]), horizontalalignment='center', color='green', fontsize=fontsize)
        ax[0].text(i+0.032*fontsize, stats[1]+0.75*fontsize, "mean: {:.2f}".format(stats[1]), horizontalalignment='center', color='orange', fontsize=fontsize )
        ax[0].text(i+0.032*fontsize, stats[3]-0.80*fontsize, "min: {:.2f}".format(stats[3]), horizontalalignment='center', color='blue', fontsize=fontsize)

        # Calculate the mean value for the CPU usage
        cpu_mean = filtered_data["cpu_usage_avg"].mean()
        cpu_thresholds.append(i)
        cpu_means.append(cpu_mean)

    # Add the line connecting the mean values of the CPU usage
    ax[0].plot(cpu_thresholds, cpu_means, marker='o', color='orange')

    # Set the x-axis labels
    ax[0].set_xticklabels(unique_thresholds)
    ax[0].set_xticks(range(len(unique_thresholds)))
    ax[0].set_xticklabels(["hpa_tresh: {}".format(int(x)) for x in unique_thresholds])

    # Draw the boxplots of the memory usage
    mem_thresholds = []
    mem_means = []
    for i, hpa_cpu_threshold in enumerate(unique_thresholds):
        # Filter the data for the current hpa_cpu_threshold
        filtered_data = data[data["hpa_cpu_threshold"] == hpa_cpu_threshold]

        # Calculate the interquartile range (IQR) and remove any data points that fall outside of the lower and upper bounds, defined as Q1 - 1.5IQR and Q3 + 1.5IQR, respectively
        mem_q75 = filtered_data["memory_usage_avg"].quantile(0.75)
        mem_q25 = filtered_data["memory_usage_avg"].quantile(0.25)
        mem_iqr = mem_q75 - mem_q25
        mem_min = mem_q25 - 1.5 * mem_iqr
        mem_max = mem_q75 + 1.5 * mem_iqr
        filtered_data = filtered_data[(filtered_data["memory_usage_avg"] >= mem_min) & (filtered_data["memory_usage_avg"] <= mem_max)]


        # Draw the boxplot of the memory usage
        box = filtered_data.boxplot(column="memory_usage_avg", ax=ax[1], positions=[i], return_type="dict")
        stats = get_stats(filtered_data)
        ax[1].text(i+0.032*fontsize, stats[6]+0.012*fontsize, "max: {:.2f}".format(stats[6]), horizontalalignment='center', color='red', fontsize=fontsize)
        ax[1].text(i+0.032*fontsize, stats[4]+0.028*fontsize, "median: {:.2f}".format(stats[4]), horizontalalignment='center', color='green', fontsize=fontsize)
        ax[1].text(i+0.032*fontsize, stats[5]-0.048*fontsize, "mean: {:.2f}".format(stats[5]), horizontalalignment='center', color='orange', fontsize=fontsize)
        ax[1].text(i+0.032*fontsize, stats[7]-0.024*fontsize, "min: {:.2f}".format(stats[7]), horizontalalignment='center', color='blue', fontsize=fontsize)

        # Calculate the mean value for the memory usage
        mem_mean = filtered_data["memory_usage_avg"].mean()
        mem_thresholds.append(i)
        mem_means.append(mem_mean)

    # Add the line connecting the mean values of the memory usage
    ax[1].plot(mem_thresholds, mem_means, marker='o', color='orange')

    # Set the x-axis labels
    ax[1].set_xticklabels(unique_thresholds)
    ax[1].set_xticks(range(len(unique_thresholds)))
    ax[1].set_xticklabels(["hpa_tresh: {}".format(int(x)) for x in unique_thresholds])
    # Set the titles of the boxplots
    ax[0].set_title("CPU Usage")
    ax[1].set_title("Memory Usage")

    # Add labels to the y-axis of the boxplots
    ax[0].set_ylabel("CPU Usage (average in mCores)")
    ax[1].set_ylabel("Memory Usage (average in MB)")
    
    if args.latency:
        # Draw the boxplots of the HTTP Request API latencies
        latency_ax = ax[2] if args.latency else None
        latency_thresholds = []
        latency_means = []
        for i, hpa_cpu_threshold in enumerate(unique_thresholds):
            # Get the latency data for the current hpa_cpu_threshold
            latency_data = get_latency_data(hpa_cpu_threshold)
            
            # Draw the boxplot of the latency data
            box = latency_data.boxplot(column="Latency", ax=latency_ax, positions=[i], return_type="dict")
            # Add the statistics to the plot
            latency_stats = get_latency_stats(latency_data)
            latency_ax.text(i+0.032*fontsize, latency_stats[2]+0.75*fontsize, "max: {:.0f} ms".format(latency_stats[2]), horizontalalignment='center', color='red', fontsize=fontsize)
            latency_ax.text(i+0.032*fontsize, latency_stats[0]-0.68*fontsize, "median: {:.0f} ms".format(latency_stats[0]), horizontalalignment='center', color='green', fontsize=fontsize)
            latency_ax.text(i+0.032*fontsize, latency_stats[1]+0.68*fontsize, "mean: {:.0f} ms".format(latency_stats[1]), horizontalalignment='center', color='orange', fontsize=fontsize)
            latency_ax.text(i+0.032*fontsize, latency_stats[3]-0.98*fontsize, "min: {:.0f} ms".format(latency_stats[3]), horizontalalignment='center', color='blue', fontsize=fontsize)

            # Calculate the mean value for the latency
            latency_mean = latency_data["Latency"].mean()
            latency_thresholds.append(i)
            latency_means.append(latency_mean)

        # Add the line connecting the mean values of the latency
        latency_ax.plot(latency_thresholds, latency_means, marker='o', color='orange')

        # Set the x-axis labels
        latency_ax.set_xticklabels(unique_thresholds)
        latency_ax.set_xticks(range(len(unique_thresholds)))
        latency_ax.set_xticklabels(["hpa_tresh: {}".format(int(x)) for x in unique_thresholds])

        # Set the title and labels of the latency boxplot
        latency_ax.set_title("HTTP Request API Latency")
        latency_ax.set_ylabel("Latency (ms)")

    if args.replicas:
        # Draw the boxplots of the replicas
        replicas_ax = ax[3] if args.latency else None
        replicas_thresholds = []
        replicas_means = []
        for i, hpa_cpu_threshold in enumerate(unique_thresholds):
            # Filter the data for the current hpa_cpu_threshold
            filtered_data = data[data["hpa_cpu_threshold"] == hpa_cpu_threshold]

            # Calculate the interquartile range (IQR) and remove any data points that fall outside of the lower and upper bounds, defined as Q1 - 1.5IQR and Q3 + 1.5IQR, respectively
            replicas_q75 = filtered_data["replicas"].quantile(0.75)
            replicas_q25 = filtered_data["replicas"].quantile(0.25)
            replicas_iqr = replicas_q75 - replicas_q25
            replicas_min = replicas_q25 - 1.5 * replicas_iqr
            replicas_max = replicas_q75 + 1.5 * replicas_iqr
            filtered_data = filtered_data[(filtered_data["replicas"] >= replicas_min) & (filtered_data["replicas"] <= replicas_max)]

            # Draw the boxplot of the replicas
            box = filtered_data.boxplot(column="replicas", ax=replicas_ax, positions=[i], return_type="dict")
            stats = get_replicas_stats(filtered_data)
            replicas_ax.text(i+0.032*fontsize, stats[2]+0.012*fontsize, "max: {:.0f}".format(stats[2]), horizontalalignment='center', color='red', fontsize=fontsize)
            replicas_ax.text(i+0.032*fontsize, stats[0]-0.032*fontsize, "median: {:.0f}".format(stats[0]), horizontalalignment='center', color='green', fontsize=fontsize)
            replicas_ax.text(i+0.032*fontsize, stats[1]+0.032*fontsize, "mean: {:.0f}".format(stats[1]), horizontalalignment='center', color='orange', fontsize=fontsize)
            replicas_ax.text(i+0.032*fontsize, stats[3]-0.012*fontsize, "min: {:.0f}".format(stats[3]), horizontalalignment='center', color='blue', fontsize=fontsize)

            # Calculate the mean value for the replicas
            replicas_mean = filtered_data["replicas"].mean()
            replicas_thresholds.append(i)
            replicas_means.append(replicas_mean)

        # Add the line connecting the mean values of the replicas
        replicas_ax.plot(replicas_thresholds, replicas_means, marker='o', color='orange')

        # Set the x-axis labels
        replicas_ax.set_xticklabels(unique_thresholds)
        replicas_ax.set_xticks(range(len(unique_thresholds)))
        replicas_ax.set_xticklabels(["hpa_tresh: {}".format(int(x)) for x in unique_thresholds])

        # Set the title and labels of the replicas boxplot
        replicas_ax.set_title("Replicas")
        replicas_ax.set_ylabel("Number of replicas")
        
    # Set the layout of the subplots
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    # Save the figure as a SVG file
    plt.savefig("deployment_metrics_summary.svg")

if __name__ == "__main__":
    main()

