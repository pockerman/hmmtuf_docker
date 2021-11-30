import numpy as np
import math
import itertools
from itertools import islice

# categories according to paper
categories = {'C1': {"R": ['A', 'G'], "Y": ["C", "T"]},
              'C2': {"M": ['A', 'C'], "K": ["G", "T"]},
              'C3': {"W": ['A', 'T'], "S": ["C", "G"]}}

# possible words for every category
categories_words = {'C1': ['RR', 'RY', 'YR', 'YY'],
                    'C2': ['MM', 'MK', 'KM', 'KK'],
                    'C3': ['WW', 'WS', 'SW', 'SS']}

# complements
complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}


def reverse_complement(seq):
    t = ''
    for base in seq:
        t = complement[base] + t
    return t


def map_seq_to_category(category, seq):
    """
    project the original seq into
    the given category
    """

    new_seq = ''
    g1 = category[list(category.keys())[0]]
    g2 = category[list(category.keys())[1]]

    for base in seq:

        if base in g1:
            new_seq += list(category.keys())[0]
        elif base in g2:
            new_seq += list(category.keys())[1]
        else:
            raise ValueError("base {0} not in {1} or in {2}".format(base, g1, g2))
    return new_seq


def get_sliding_window_sequence_words(seq, w):
    """Returns a sliding window (of width n) over data from the iterable
       s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
    """
    it = iter(seq)
    result = tuple(islice(it, w))
    if len(result) == w:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def collect_words(seq, k):
    words = []

    for word in get_sliding_window_sequence_words(seq=seq, w=k):
        words.append(word)
    return words


def shannon_entropy(ps):
    """
    Shannon entropy computation
    """

    entropy = 0.0

    for val in ps:

        if val < 1.0e-4:
            continue

        entropy += val * math.log(val, 2)

    return -1.0*entropy


def local_frequency(word, seq):
    """
    Compute the local frequency of the word
    in the qiven sequence
    """

    # this the counter which tracks
    # the occurrences of the word in the
    # seq. 
    r = 1

    # indexes will hold the locations of the 
    # word in the sequence. so len(indexes)
    # indicates how many times the word is found in the
    # sequence
    indexes = []
    for item in seq:

        if item == word:
            indexes.append(r)
        r += 1

    if len(indexes) == 0:
        print("WARNING: Word {0} not found in the sequence {1}".format(word, seq))
        return [0]

    if len(indexes) == 1:
        return [1.0 / indexes[0]]

    frequencies = []

    for i in range(len(indexes)):

        current = indexes[i]
        if i != 0:

            previous = indexes[i - 1]
            frequencies.append(1.0 / (current - previous))
        else:

            frequencies.append(1.0 / current)

    return frequencies


def partial_sums(seq):
    """
    Compute the partial sums of the sequence
    """

    return list(itertools.accumulate(seq))


def sequence_total_sum(s):
    return sum(s)


def calculate_p(s, z):
    probabilities = []

    for item in s:
        probabilities.append(item / z)

    return probabilities


def count_words(word, seq):
    """
    Compute the number of occurences of the word in the sequence
    """

    # this the counter which tracks
    # the occurrences of the word in the
    # seq.
    count = 0

    # indexes will hold the locations of the
    # word in the sequence. so len(indexes)
    # indicates how many times the word is found in the
    # sequence

    for item in seq:

        if item == word:
            count += 1

    return count


def sequence_feature_vector_from_counts(seq, k=2):
    """
       Build the feature vector for the given sequence using
       a word size k=2
    """

    # placeholder for shannon entropies
    feature_vec = []

    for C in categories:

        # map the bases in seq into the groups
        # of the category
        new_seq = map_seq_to_category(categories[C], seq)

        # collect the words in the sequence for
        # a sliding window of length k
        words = collect_words(seq=new_seq, k=k)

        # loop over the unique words that
        # each category can produce
        for word in categories_words[C]:

            tuple_word = (word[0], word[1])

            if tuple_word not in words:
                feature_vec.append(0)
                continue

            # compute the local frequencies
            # of the word in the sequence
            word_count = count_words(word=tuple_word, seq=words)

            # compute the partial sums of the sequence
            # which is basically the prefix sum

            # ...append it to list
            feature_vec.append(word_count)

    if len(feature_vec) != 12:
        raise ValueError("Invalid dimension for feature vector. {0} should be {1}".format(len(feature_vec), 12))

    return feature_vec


def sequence_feature_vector(seq, use_partial_sums=True, k=2):
    """
    Build the feature vector for the given sequence using
    a word size k=2
    """

    # placeholder for shannon entropies
    feature_vec = []

    for C in categories:

        # map the bases in seq into the groups
        # of the category
        new_seq = map_seq_to_category(categories[C], seq)

        # collect the words in the sequence for
        # a sliding window of length k
        words = collect_words(seq=new_seq, k=k)

        # loop over the unique words that
        # each category can produce
        for word in categories_words[C]:

            tuple_word = (word[0], word[1])

            if tuple_word not in words:
                feature_vec.append(0.0)
                continue

            # compute the local frequencies
            # of the word in the sequence
            lf_w = local_frequency(word=tuple_word, seq=words)

            # compute the partial sums of the sequence 
            # which is basically the prefix sum

            if use_partial_sums:
                S = partial_sums(seq=lf_w)
            else:
                S = lf_w

            # compute the total sum of the sequence with the
            # prefix sums
            z = sequence_total_sum(s=S)

            # calculate the sequence of probabilities
            probabilities = calculate_p(s=S, z=z)

            # compute the entropy
            entropy = shannon_entropy(ps=probabilities)

            # ...append it to list
            feature_vec.append(entropy)

    if len(feature_vec) != 12:
        raise ValueError("Invalid dimension for feature vector. {0} should be {1}".format(len(feature_vec), 12))

    return feature_vec


def cpf_from_counts(seq1, seq2, k=2):
    feature_vec_1 = sequence_feature_vector_from_counts(seq=seq1, k=k)
    feature_vec_2 = sequence_feature_vector_from_counts(seq=seq2, k=k)

    # calculate Euclidean distance
    feature_vec_1 = np.array(feature_vec_1)
    feature_vec_2 = np.array(feature_vec_2)
    dist = np.linalg.norm(feature_vec_1 - feature_vec_2)

    return dist


def cpf_from_counts_without_zeros(seq1, seq2, k=2):

    feature_vec_1 = sequence_feature_vector_from_counts(seq=seq1, k=k)
    feature_vec_2 = sequence_feature_vector_from_counts(seq=seq2, k=k)

    tmp1 = []
    tmp2 = []
    # remove the zeros
    for item1, item2 in zip(feature_vec_1, feature_vec_2):

        if int(item1) == 0 or int(item2) == 0: # and item1 == item2:
            continue

        tmp1.append(item1)
        tmp2.append(item2)

    feature_vec_1 = tmp1
    feature_vec_2 = tmp2

    # calculate Euclidean distance
    feature_vec_1 = np.array(feature_vec_1)
    feature_vec_2 = np.array(feature_vec_2)
    dist = np.linalg.norm(feature_vec_1 - feature_vec_2)

    return dist

def sequence_feature_vector_from_probability_counts(seq, k=2):
    """
        Build the feature vector for the given sequence using
        a word size k=2
    """

    # placeholder for shannon entropies
    feature_vec = []

    for C in categories:

        # map the bases in seq into the groups
        # of the category
        new_seq = map_seq_to_category(categories[C], seq)

        # collect the words in the sequence for
        # a sliding window of length k
        words = collect_words(seq=new_seq, k=k)

        # loop over the unique words that
        # each category can produce
        for word in categories_words[C]:

            tuple_word = (word[0], word[1])

            if tuple_word not in words:
                feature_vec.append(0.0)
                continue

            # count how many times the word occurs
            # in the sequnce
            word_count = count_words(word=tuple_word, seq=words)

            # frequency based probability calculation
            probability = float(word_count)/float(len(words))

            # ...append it to list
            feature_vec.append(probability)

    if len(feature_vec) != 12:
        raise ValueError("Invalid dimension for feature vector. {0} should be {1}".format(len(feature_vec), 12))

    return feature_vec


def cpf_from_probability_counts(seq1, seq2 , k=2):

    feature_vec_1 = sequence_feature_vector_from_probability_counts(seq=seq1, k=k)
    feature_vec_2 = sequence_feature_vector_from_probability_counts(seq=seq2, k=k)

    # calculate Euclidean distance
    feature_vec_1 = np.array(feature_vec_1)
    feature_vec_2 = np.array(feature_vec_2)
    dist = np.linalg.norm(feature_vec_1 - feature_vec_2)

    return dist


def cpf_from_probability_counts_remove_zeros(seq1, seq2, k=2):

    feature_vec_1 = sequence_feature_vector_from_probability_counts(seq=seq1, k=k)
    feature_vec_2 = sequence_feature_vector_from_probability_counts(seq=seq2, k=k)

    tmp1 = []
    tmp2 = []
    # remove the zeros
    for item1, item2 in zip(feature_vec_1, feature_vec_2):

        if item1 < 1.0e-5 or item2 < 1.0e-5:
            continue

        tmp1.append(item1)
        tmp2.append(item2)

    feature_vec_1 = tmp1
    feature_vec_2 = tmp2

    # calculate Euclidean distance
    feature_vec_1 = np.array(feature_vec_1)
    feature_vec_2 = np.array(feature_vec_2)
    dist = np.linalg.norm(feature_vec_1 - feature_vec_2)

    return dist


def cpf(seq1, seq2, use_partial_sums=True, k=2):
    feature_vec_1 = sequence_feature_vector(seq=seq1, use_partial_sums=use_partial_sums, k=k)
    feature_vec_2 = sequence_feature_vector(seq=seq2, use_partial_sums=use_partial_sums, k=k)

    # calculate Euclidean distance
    feature_vec_1 = np.array(feature_vec_1)
    feature_vec_2 = np.array(feature_vec_2)
    dist = np.linalg.norm(feature_vec_1 - feature_vec_2)

    return dist


class CPF(object):
    def __init__(self, k=2):
        self._feature_vectors = np.empty((0, 12), np.float)
        self._k = k
        self._use_partial_sums = True
        self._use_word_counts = False
        self._use_word_counts_and_remove_zeros = False
        self._use_probability_counts = False
        self._use_probability_counts_and_remove_zeros = False

    def add_feature_vector(self, seq):

        if self._use_word_counts:
            feature_vec = sequence_feature_vector_from_counts(seq=seq, k=self._k)
        elif self._use_probability_counts:
            feature_vec = sequence_feature_vector_from_probability_counts(seq=seq, k=self._k)
        else:
            feature_vec = sequence_feature_vector(seq=seq, k=self._k)
        self._feature_vectors = np.append(self._feature_vectors,
                                          np.array([feature_vec]), axis=0)

    def get_feature_vectors(self):
        return self._feature_vectors

    def set_options(self, **options):
        if "use_word_counts" in options:
            self._use_word_counts = options["use_word_counts"]

        if "use_word_counts_and_remove_zeros" in options:
            self._use_word_counts_and_remove_zeros = options["use_word_counts_and_remove_zeros"]

        if "use_probability_counts" in options:
            self._use_probability_counts = options["use_probability_counts"]

        if "use_probability_counts_and_remove_zeros" in options:
            self._use_probability_counts_and_remove_zeros = options["use_probability_counts_and_remove_zeros"]

        if "use_partial_sums" in options:
            self._use_partial_sums = options["use_partial_sums"]

    def similarity(self, seq1, seq2):

        if self._use_word_counts:
            return cpf_from_counts(seq1=seq1, seq2=seq2)
        elif self._use_word_counts_and_remove_zeros:
            return cpf_from_counts_without_zeros(seq1=seq1, seq2=seq2)
        elif self._use_probability_counts:
            return cpf_from_probability_counts(seq1=seq1, seq2=seq2)
        elif self._use_probability_counts_and_remove_zeros:
            return cpf_from_probability_counts_remove_zeros(seq1=seq1, seq2=seq2)

        return cpf(seq1=seq1, seq2=seq2, use_partial_sums=self._use_partial_sums)

    def __call__(self, *args, **kwargs):
        return self.similarity(seq1=args[0], seq2=args[1])


def get_unique_words(seq):
    unique_words = []

    for item in seq:
        if item not in unique_words:
            unique_words.append(item)

    return unique_words


def main():
    seq = 'ATGGTGCACCTGACT'
    dist = cpf(seq1=seq, seq2=seq)
    print("Seq1 {0}, seq2 {1} distance={2}".format(seq, seq, dist))

    reverse_complement_seq = reverse_complement(seq)
    dist = cpf(seq1=seq, seq2=reverse_complement_seq)
    print("Seq1 {0}, seq2 {1} distance={2}".format(seq, reverse_complement_seq, dist))

    reverse_complement_seq = reverse_complement_seq[0:5]
    dist = cpf(seq1=seq, seq2=reverse_complement_seq)
    print("Seq1 {0}, seq2 {1} distance={2}".format(seq, reverse_complement_seq, dist))


if __name__ == '__main__':
    main()
