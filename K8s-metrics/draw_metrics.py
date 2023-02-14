import csv
import matplotlib.pyplot as plt

def plot_metrics(filename):
    """
    Plot the CPU usage and memory usage metrics stored in a CSV file.
    
    Parameters:
        filename (str): The name of the CSV file.
    """
    # Read the data from the CSV file
    cpu_usage = []
    memory_usage = []
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cpu_usage.append(float(row["cpu_usage_avg"]))
            memory_usage.append(float(row["memory_usage_avg"]))
    
    # Plot the CPU usage data as a box plot
    plt.figure()
    plt.boxplot(cpu_usage)
    plt.title("CPU Usage")
    plt.ylabel("Usage (mHz)")
    plt.savefig("cpu_usage_boxplot.svg")
    
    # Plot the memory usage data as a box plot
    plt.figure()
    plt.boxplot(memory_usage)
    plt.title("Memory Usage")
    plt.ylabel("Usage (MB)")
    plt.savefig("memory_usage_boxplot.svg")

if __name__ == "__main__":
    plot_metrics("deployment_metrics.csv")
