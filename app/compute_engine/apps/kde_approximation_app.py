import csv
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity


def app_kde_main(data, kernel, bandwidth):

    kde = KernelDensity(kernel=kernel, bandwidth=bandwidth)
    kde.fit(data)
    return kde


if __name__ == '__main__':

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/lengths/"
    OUTPUT_FILE = "part-00000"
    with open(OUTPUT_DIR + OUTPUT_FILE, 'r') as fh:
        reader = csv.reader(fh, delimiter=",")

        x = []

        counter = 0
        for line in reader:
            x.append(int(line[0]))
            counter += 1

        print("Number of items {0}".format(counter))

        new_data = np.array(x, dtype='U')
        new_data = new_data.reshape(-1, 1)
        kde_gaussian = app_kde_main(data=new_data, kernel='gaussian', bandwidth=0.7)

        kde_tophat = app_kde_main(data=new_data, kernel='tophat', bandwidth=0.7)

        # get samples
        samples_gausian = kde_gaussian.sample(n_samples=counter)

        print(samples_gausian)

        axes = sns.histplot(data=x, bins=160)
        plt.title("Original data")
        plt.show()

        axes = sns.histplot(data=samples_gausian, bins=160)
        plt.title("Gaussian kernel")
        plt.show()

        samples_tophat = kde_tophat.sample(n_samples=counter)
        axes = sns.histplot(data=samples_tophat, bins=160)
        plt.title("Tophat kernel")
        plt.show()
