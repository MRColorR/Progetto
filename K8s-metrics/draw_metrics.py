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
        
        # Add the hpa_cpu_threshold to the x axis of the boxplots
        ax[0].axhline(y=hpa_cpu_threshold, color='r', linestyle='--')
        ax[1].axhline(y=hpa_cpu_threshold, color='r', linestyle='--')
        
        # Set the titles of the boxplots
        ax[0].set_title("CPU Usage")
        ax[1].set_title("Memory Usage")
        
        # Save the figure as a SVG file
        postfix = "_threshold_{}".format(int(hpa_cpu_threshold))
        plt.savefig("deployment_metrics{}.svg".format(postfix))

if __name__ == "__main__":
    main()

