import seaborn as sns
import csv
import numpy as np
import matplotlib.pyplot as plt


def get_data(output_dir, output_file, line_index):

    with open(output_dir + output_file, 'r') as fh:
        reader = csv.reader(fh, delimiter=",")

        x = []

        for line in reader:
            x.append(float(line[line_index]))

        print("Number of items {0}".format(len(x)))
        return x


def plot_distances_kde_main(output_dir, output_file, line_index,
                            title, xlabel, xlimits=None):

        x = get_data(output_dir=output_dir, output_file=output_file, line_index=line_index)
        sns.kdeplot(data=x)
        plt.title(title)

        if xlimits is not None:
            plt.xlim(xmin=xlimits[0], xmax=xlimits[1])

        plt.xlabel(xlabel)
        plt.show()


def plot_distances_kde_outlier_remove(output_dir, output_file, line_index,
                                      data_limiter, title, xlabel, xlimits=None):

    x = get_data(output_dir=output_dir, output_file=output_file, line_index=line_index)

    data_values = []

    if data_limiter is not None:
        if data_limiter["name"] == 'value_cutoff':

            for item in x:
                if item > data_limiter["cut_off_value"]:
                    continue
                else:
                    data_values.append(item)
        else:
            data_values = x
    else:
        data_values = x

    data_values = np.array(data_values)
    x_mean = np.mean(data_values)
    x_std = np.std(data_values)

    print("Mean={0}".format(x_mean))
    print("Std={0}".format(x_std))

    sns.kdeplot(data=data_values)
    plt.title(title)

    if xlimits is not None:
        plt.xlim(xmin=xlimits[0], xmax=xlimits[1])

    plt.xlabel(xlabel)
    plt.show()


if __name__ == '__main__':

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "random_sequences_distances_CPF.csv"
    LINE_INDEX = -1

    #plot_distances_kde_main(output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE,
    #                        line_index=LINE_INDEX, title="Random sequences CPF",
    #                        xlabel="Distance")

    #OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/full_sequences_distances_cpf/"

    #plot_distances_kde_main(output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE,
    #                        line_index=LINE_INDEX, title="Extracted sequences CPF",
    #                        xlabel="Distance")

    data_limiter = None #{"name": "value_cutoff", "cut_off_value": 100.0}
    plot_distances_kde_outlier_remove(output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE,
                                      line_index=LINE_INDEX, title="Random sequences Longest Common Subsequence",
                                      xlabel="Distance", data_limiter=data_limiter)

    OUTPUT_FILE = "full_sequences_distances_no_partial_sums_CPF.csv" #"full_sequences_distances_CPF.csv"
    plot_distances_kde_outlier_remove(output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE,
                                      line_index=LINE_INDEX, title="Extracted sequences Longest Common Subsequence",
                                      xlabel="Distance", data_limiter=data_limiter)


