import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from compute_engine.src.string_sequence_calculator import TextDistanceCalculator
import textdistance

def compute_distinct_sequences_distances_app_main(sequences):

    calculator = TextDistanceCalculator.build_calculator(name='CPF')
    calculator._use_word_counts = True

    for seq in sequences:
        calculator.add_feature_vector(seq=seq)

    feature_vectors = calculator.get_feature_vectors()

    print(feature_vectors)

    distances = {}
    cosine_sim = {}
    cosine_dist = {}
    for vec1, seq1 in zip(feature_vectors, sequences):
        for vec2, seq2 in zip(feature_vectors, sequences):

            if (seq1, seq2) not in distances and (seq2, seq1) not in distances:
                feature_vec_1 = np.array(vec1)
                feature_vec_2 = np.array(vec2)
                distances[(seq1, seq2)] = np.linalg.norm(feature_vec_1 - feature_vec_2)
                feature_vec_1 = feature_vec_1.reshape(1, -1)
                feature_vec_2 = feature_vec_2.reshape(1, -1)
                cosine_sim[(seq1, seq2)] = cosine_similarity(feature_vec_1, feature_vec_2)
                cosine_dist[(seq1, seq2)] = cosine_distances(feature_vec_1, feature_vec_2)

    for item in distances:
        print("Sequences {0}".format(item))
        print("L2 norm={0} ".format(distances[item]))
        print("Cosine similarity={0} ".format(cosine_sim[item]))
        print("Cosine distance={0} ".format(cosine_dist[item]))


if __name__ == '__main__':
    sequences = ['CCCTCCCCTCCCCTCTACCTCATCACCCCCCACCCCCCC',
                 'CTCCCTCCTCCCTCTCCTTCTCTCTCTCCCTCTCCCCC',
                 'ATAAGTATTAGTCTGTAACATGCAGTCTTCTCTCACCATTGTA',
                 'TGTGTGTCAAATCTCCCTCTCCTTTTCTTAGAATACATGCTATT']

    compute_distinct_sequences_distances_app_main(sequences=['CCCTCCCCTCCCCTCTACCTCATCACCCCCCACCCCCCC',
                                                             'CTCCCTCCTCCCTCTCCTTCTCTCTCTCCCTCTCCCCC'])

    compute_distinct_sequences_distances_app_main(sequences=['ATAAGTATTAGTCTGTAACATGCAGTCTTCTCTCACCATTGTA',
                                                             'TGTGTGTCAAATCTCCCTCTCCTTTTCTTAGAATACATGCTATT'])


    """
    calculator = TextDistanceCalculator.build_calculator(name='CPF')
    calculator._use_word_counts = True

    for seq in sequences[0:2]:
        calculator.add_feature_vector(seq=seq)

    feature_vectors = calculator.get_feature_vectors()

    print(feature_vectors)

    distances = []
    for vec1, seq1 in zip(feature_vectors, sequences[0:2]):
        for vec2, seq2 in zip(feature_vectors, sequences[0:2]):
            feature_vec_1 = np.array(vec1)
            feature_vec_2 = np.array(vec2)
            distances.append((seq1, seq2, np.linalg.norm(feature_vec_1 - feature_vec_2)))

    for item in distances:
        print(item)

    calculator = TextDistanceCalculator.build_calculator(name='CPF')
    calculator._use_word_counts = True

    for seq in sequences[2:5]:
        calculator.add_feature_vector(seq=seq)

    feature_vectors = calculator.get_feature_vectors()

    print(feature_vectors)

    distances = []
    for vec1, seq1 in zip(feature_vectors, sequences[2:5]):
        for vec2, seq2 in zip(feature_vectors, sequences[2:5]):
            feature_vec_1 = np.array(vec1)
            feature_vec_2 = np.array(vec2)
            distances.append((seq1, seq2, np.linalg.norm(feature_vec_1 - feature_vec_2)))

    for item in distances:
        print(item)
    """
    #compute_distinct_sequences_distances_app_main(sequences=sequences)