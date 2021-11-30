"""
Helpers for calculating HMM Viterbi paths
"""
from pathlib import Path
import csv
import numpy as np
from pomegranate import *

from compute_engine.src.constants import INFO


def get_window_ids_from_viterbi_path(path, wstate, limit_state):
    indices = []
    for i, item in enumerate(path):

        if item[1].name == wstate:
            indices.append((i, item[1].name))
        elif item[1].name == limit_state:
            indices.append((i, item[1].name))

    return indices


def is_solid_subseq(subseq, wstate):
    itis = True
    for sitem in subseq:
        if sitem[1].name != wstate:
            itis = False
            break
    return itis


def clean_up_subsequence(subseq, start):
    indices = []

    for item in subseq:
        indices.append((start, item[1].name))
        start += 1
    return indices


def get_state_bwd(path, counter_end, wstate):
    indices = []
    global_end = counter_end
    for item in reversed(path):
        if item[1].name == wstate:
            indices.append((global_end, wstate))
        else:
            break
        global_end -= 1
    if len(indices) != 0:
        return indices[::-1]
    return indices


def get_state_fwd(path, counter_start, wstate):
    indices = []
    global_start = counter_start
    for item in path:

        if item[1].name == wstate:
            indices.append((global_start, item[1].name))
        else:
            break
        global_start += 1
    return indices


def check_items(included, check_on):
    if check_on[-1][0] in included:
        # if the last is included all
        # the rest should be
        return True
    # are not in so put it in
    for item in check_on:
        included.append(item[0])
    return False


def filter_viterbi_path(path, wstate, limit_state, min_subsequence):

    print("{0} Length of Viterbi path {1}".format(INFO, len(path)))

    indices = []

    if len(path) == 0:
        return indices

    index_included = []
    path_counter = 0
    stop = False
    while not stop:

        if path_counter >= len(path):
            break

        # get the item from the viterbi path
        item = path[path_counter]

        # if this is the last item treat it differently
        # as we don't have any forward items
        if path_counter == len(path) - 1:
            # regardless of what this is ignore it
            break

        if item[1].name == limit_state:

            # we don't want to fall off the array
            if min_subsequence + path_counter >= len(path):
                break

            # get the subsequence
            subsequence = path[path_counter:min_subsequence + path_counter]

            # only do work if it is pure
            if is_solid_subseq(subseq=subsequence, wstate=limit_state):

                # bring the subsequence in the form (idx, state)
                subsequence = clean_up_subsequence(subseq=subsequence, start=path_counter)

                # what is after the extracted region
                counter_after = path_counter + min_subsequence

                # check what is after the extracted region
                has_wstate_after = False
                has_limit_state_after = False

                if path[counter_after][1].name == wstate:
                    # this is an island
                    has_wstate_after = True
                elif path[counter_after][1].name == limit_state:
                    has_limit_state_after = True

                # check what is before the extracted
                # region
                has_wstate_before = False

                if path[path_counter - 1][1].name == wstate:
                    has_wstate_before = True

                if has_wstate_before and has_wstate_after:
                    # subsequence is an island get the
                    # surrounding TUFs
                    tuf_before = get_state_bwd(path=path[:path_counter],
                                               counter_end=path_counter - 1,
                                               wstate=wstate)
                    tuf_after = get_state_fwd(path=path[counter_after:],
                                              counter_start=counter_after,
                                              wstate=wstate)
                    if not check_items(included=index_included, check_on=tuf_before):
                        indices.extend(tuf_before)
                    indices.extend(subsequence)
                    indices.extend(tuf_after)

                    # TUF after has been considered
                    # so record it
                    for titem in tuf_after:
                        index_included.append(titem[0])

                    path_counter += min_subsequence + len(tuf_after)

                elif has_wstate_before and has_limit_state_after:
                    # pick up all the limit_wstate as these are part
                    # of the island
                    limit_state_after = get_state_fwd(path=path[counter_after:],
                                                      counter_start=counter_after,
                                                      wstate=limit_state)
                    counter_after += len(limit_state_after)

                    if counter_after >= len(path):
                        print("{0} For position {1} cannot compute path. "
                              "Counter exceeds path length ".format(INFO, counter_after))
                        break

                    # only if the exactly next one is wstate
                    # then we have an island
                    if path[counter_after][1].name == wstate:

                        tuf_before = get_state_bwd(path=path[:path_counter],
                                                   counter_end=path_counter - 1,
                                                   wstate=wstate)

                        tuf_after = get_state_fwd(path=path[counter_after:],
                                                  counter_start=counter_after,
                                                  wstate=wstate)
                        subsequence.extend(limit_state_after)

                        if not check_items(included=index_included, check_on=tuf_before):
                            indices.extend(tuf_before)

                        indices.extend(subsequence)
                        indices.extend(tuf_after)

                        # TUF after has been considered
                        # so record it
                        for titem in tuf_after:
                            index_included.append(titem[0])

                        path_counter += len(subsequence) + len(tuf_after)
                    else:
                        # jump to counter_after
                        # as did a search and there are no islands
                        path_counter = counter_after
                else:

                    path_counter += 1
            else:
                path_counter += 1
        else:

            # simply increase the counter
            path_counter += 1

    return indices


def get_continuous(tuf_delete_tuf, start_tuf_counter, name):

    has_more = True
    item = None
    counter = start_tuf_counter
    while has_more:

        if counter >= len(tuf_delete_tuf):
            break

        new_item = tuf_delete_tuf[counter]

        if new_item[1] != name:
            has_more = False

        if item is not None:
            if int(new_item[0]) != int(item[0]) + 1:
                has_more = False

        if has_more:
            item = new_item
            counter += 1
    return item, counter


def get_start_end_segment(tuf_delete_tuf, sequence):

    if len(tuf_delete_tuf) == 0:
        print("{0} TUF_DELETE_TUF data is empty".format(INFO))
        return []

    start_tuf_counter = 0
    segments = []
    while True:

        start_item = tuf_delete_tuf[start_tuf_counter]
        start_seq = sequence[start_item[0]]

        end_item, counter = get_continuous(tuf_delete_tuf=tuf_delete_tuf,
                                           start_tuf_counter=start_tuf_counter + 1,
                                           name=start_item[1])
        if end_item is not None:
            assert end_item[1] == start_item[1]
            end_seq = sequence[end_item[0]]

            gap = int(end_seq[1][1]) - int(start_seq[1][0]) + 1
            segments.append((start_item[0], int(start_seq[1][0]),
                             int(end_seq[1][1]), gap,
                             start_item[1]))
        else:
            # this is on its own
            gap = int(start_seq[1][1]) - int(start_seq[1][0])
            segments.append((start_item[0], int(start_seq[1][0]), int(start_seq[1][1]), gap + 1, start_item[1]))

        start_tuf_counter = counter

        if start_tuf_counter >= len(tuf_delete_tuf):
            break

    return segments


def save_segments(segments, chromosome, filename):

    with open(filename, 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for segment in segments:
            row = [chromosome]
            row.extend(list(segment))
            writer.writerow(row)


def create_viterbi_path(sequence, hmm_model, chromosome: str,
                        filename: Path, append_or_write: str,
                        gap_state_obs: tuple=(-999.0, -999.0)) -> tuple:

    observations = []
    for i in range(len(sequence)):
        observations.append(sequence[i][0])

    print("{0} Observation length: {1}".format(INFO, len(observations)))
    viterbi_path = hmm_model.viterbi(observations)
    print("{0} Log-probability of ML Viterbi path: {1}".format(INFO, viterbi_path[0]))

    # for each item in the sequence
    # cache the index and state predicted
    sequence_viterbi_state = []

    if viterbi_path[1] is not None:
        print("{0} Viterbi path length: {1}".format(INFO, len(viterbi_path[1])))

        counter = 0
        with open(filename, append_or_write) as f:
            f.write(str(len(viterbi_path[1]) - 1) + "\n")
            for item in range(len(sequence)):

                if sequence[item][0] == gap_state_obs:
                    counter += 1

                r = (int(sequence[item][1][0]), int(sequence[item][1][1]))
                name = viterbi_path[1][item + 1][1].name
                f.write(chromosome + ":" + str(item) + ":" + str(r) + ":" + str(sequence[item][0]) + ":" + name + "\n")
                sequence_viterbi_state.append((item, viterbi_path[1][item + 1][1].name))

        print("{0} There should be {1} gaps".format(INFO, counter))
    else:
        print("{0} Viterbi path is impossible for the given sequence".format(INFO))

    return viterbi_path, observations, sequence_viterbi_state


def plot_state(state_dist, sample_size, min_, max_, n_bins):

     samples = state_dist.sample(n=sample_size)
     xdata = samples[:,[0]]
     ydata = samples[:,[1]]

     x = [item[0] for item in xdata]
     y = [item[0] for item in ydata]

     plt.hist2d(y, x,
                bins=[n_bins, n_bins], cmap='Blues', density=False,
    # cmax=1000,
    # cmin=0,
                alpha=0.99,
                range=((min_, max_), (min_, max_)))

     plt.show()
     state_dist.plot(bins=n_bins)
     plt.show()


def create_states(states_map, means, covariances,  means_to_use=None, plot=True):

    states={}
    for state in states_map:

        print("state name: ", state)
        name = state
        idx = states_map[state]

        # change the order of the means to match the order of the
        # data we will retrieve below in the prediction step
        mu_no_wga = means[idx][0]
        mu_wga = means[idx][1]
        mu = np.array([mu_wga, mu_no_wga])
        print("State means: ", means[idx])
        cov = covariances[idx]
        print("State covariance: ", cov)
        cov = np.array([[cov[1], 0.0], [0.0, cov[0]]])

        if state == "Duplication":
            mu[1] = 45.0

        state_dist = MultivariateGaussianDistribution(means=mu,
                                                      covariance=cov)

        if plot:

            if state == "Duplication":
                min_ = 0.0
                max_ = 70.0
            elif state == "Normal-I":
                min_ = 0.0
                max_ = 70.0
            elif state == "Normal-II":
                min_ = 0.0
                max_ = 70.0
            elif state == 'Deletion':
                min_ = 0.0
                max_ = 70.0

            plot_state(state_dist=state_dist,
                       sample_size=10000, n_bins=30,
                       min_=min_, max_=max_)

        states[name] = State(state_dist, name=name)
    return states


def create_tuf_state(comp1_means, comp1_cov, comp2_means, comp2_cov):

    tuf_dist = MultivariateGaussianDistribution(means=comp1_means,
                                                covariance=comp1_cov)

    n_bins = 100
    samples = tuf_dist.sample(n=15000)
    xdata = samples[:, [0]]
    ydata = samples[:, [1]]

    x = [item[0] for item in xdata]
    y = [item[0] for item in ydata]
    # print(samples)
    plt.hist2d(y, x,
               bins=[n_bins, n_bins], cmap='Blues', density=False,
               cmax=1000,
               cmin=0,
               alpha=0.99,
               range=((0.0, 140.), (0.0, 70.0)))

    plt.show()

    # only change the means
    #tuf_mu = np.array([tuf_mu_wga, 40.0])

    # also add the dist that is not modeled by the data
    tuf_dist_double = MultivariateGaussianDistribution(means=comp2_means,
                                                       covariance=comp2_cov)

    n_bins = 100
    samples = tuf_dist_double.sample(n=15000)
    xdata = samples[:, [0]]
    ydata = samples[:, [1]]

    x = [item[0] for item in xdata]
    y = [item[0] for item in ydata]
    # print(samples)
    plt.hist2d(y, x,
               bins=[n_bins, n_bins], cmap='Blues', density=False,
               cmax=1000,
               cmin=0,
               alpha=0.99,
               range=((0.0, 140.), (0.0, 70.0)))

    plt.show()

    tuf_mixture = GeneralMixtureModel([tuf_dist, tuf_dist_double], weights=[0.5, 0.5])

    tuf_dist.plot(bins=n_bins)
    tuf_dist_double.plot(bins=n_bins)
    plt.show()

    return State(tuf_mixture, name='TUF')


def get_states_counter(states_counter, observations, sequence_viterbi_state):

    state_data = {}

    for state in states_counter:
        state_data[state] = [[], []]

    # collect counters for error statistics
    for i, obs in enumerate(observations):

        # what dows the Viterbi path says
        viterbi_state = sequence_viterbi_state[i][1]
        if obs == (-999.0, -999.0):

            # if we predict that increase the success
            # otherwise increase errors
            if viterbi_state == 'GAP_STATE':
                states_counter[viterbi_state] += 1
            else:
                states_counter["GAP_STATE_INCORRECT"] += 1
        else:
            states_counter[viterbi_state] += 1

        state_data[viterbi_state][0].append(obs[0])
        state_data[viterbi_state][1].append(obs[1])
    return states_counter, state_data


def plot_hmm_states_to_labels(hmm_states_to_labels, observations,
                              sequence_viterbi_state, no_wga_obs,
                              title, wga_obs, xlim, ylim,
                              show_plt, save_file=False, save_filename=None):
    hmm_labels = []
    state_obs = {}

    for state in hmm_states_to_labels:
        state_obs[state] = {'wga': [], 'nwga': []}

    # collect the labels as these are predicted by the HMM
    for i, obs in enumerate(observations):

        # do not account for GAPs
        if obs != (-999.0, -999.0):
            viterbi_state = sequence_viterbi_state[i][1]
            hmm_labels.append(hmm_states_to_labels[viterbi_state])
            state_obs[viterbi_state]['wga'].append(obs[0])
            state_obs[viterbi_state]['nwga'].append(obs[1])

    colors = np.array(['green', 'blue', 'red', 'yellow', 'pink', 'black', 'purple'])
    colors = colors[hmm_labels]

    color_comp_assoc_hmm = {}
    for label, color in zip(hmm_labels, colors):
        if color in color_comp_assoc_hmm.keys():
            assert color_comp_assoc_hmm[color][0] == label
            color_comp_assoc_hmm[color][1] += 1
        else:
            color_comp_assoc_hmm[color] = [label, 1]

    with open(save_filename, 'w', newline="\n") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['nwga', 'wga', 'state', 'color'])
        counter = 0
        for color in color_comp_assoc_hmm:
            label = color_comp_assoc_hmm[color][0]

            if counter == 1:
                break

            for state in hmm_states_to_labels:

                if counter == 1:
                    break

                if hmm_states_to_labels[state] == label:
                    nwga = state_obs[state]['nwga']
                    wga = state_obs[state]['wga']

                    for item1, item2 in zip(nwga, wga):
                        writer.writerow([item1, item2, state, color])

                    counter += 1


    """
    plt.scatter(no_wga_obs, wga_obs, color=colors)
    plt.xlabel("NO-WGA")
    plt.ylabel("WGA")
    plt.title(title)
    plt.legend(loc='upper right', title="States")
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.grid(True)

    if show_plt:
        plt.show()
    elif save_file:
        plt.savefig(save_filename, bbox_inches='tight', dpi=85, transparent=True)

    plt.close()
    """

    return color_comp_assoc_hmm, hmm_states_to_labels, hmm_labels


def plot_hmm_label_state(hmm_states_to_labels, hmm_labels,
                         no_wga_obs, wga_obs, nbins, xlim, ylim):

    for label in hmm_states_to_labels:

        print("State: ", label)
        label_idx = hmm_states_to_labels[label]

        state_labels = []

        state_no_wga_obs = []
        state_wga_obs = []
        for i, item in enumerate(hmm_labels):
            if item == label_idx:
                state_labels.append(label_idx)
                state_no_wga_obs.append(no_wga_obs[i])
                state_wga_obs.append(wga_obs[i])

        colors = np.array(['green', 'yellow', 'blue', 'red', 'pink', 'purple', 'magenta'])

        if len(state_no_wga_obs) != 0:

            print("Length: {0}".format(len(state_no_wga_obs)))

            colors = colors[state_labels]

            # plot the observations
            plt.scatter(state_no_wga_obs, state_wga_obs, color=colors)

            kernel = kde.gaussian_kde(np.vstack([state_no_wga_obs, state_wga_obs]))

            min_x = 0.0
            max_x = 70.0
            min_y = 0.0
            max_y = 70.0

            if xlim is not None and ylim is not None:
                min_x = xlim[0]
                max_x = xlim[1]
                min_y = ylim[0]
                max_y = ylim[1]

            xi, yi = np.mgrid[min([min_x]):max([max_x]):nbins * 1j,
                              min([min_y]):max([max_y]):nbins * 1j]

            zi = kernel(np.vstack([xi.flatten(), yi.flatten()]))
            plt.contour(xi, yi, zi.reshape(xi.shape), 24)

            plt.xlabel("NO-WGA ")
            plt.ylabel("WGA")

            if xlim is not None and ylim is not None:
                plt.xlim(xlim)
                plt.ylim(ylim)
            elif label == "Duplication":
                plt.xlim(0.0, 70.0)
                plt.ylim(0.0, 70.0)
            elif label == "Normal-I":
                plt.xlim(0.0, 70.0)
                plt.ylim(0.0, 70.0)
            elif label == "Normal-II":
                plt.xlim(0.0, 80.0)
                plt.ylim(0.0, 80.0)
            elif label == "Deletion":
                plt.xlim(0.0, 70.0)
                plt.ylim(0.0, 70.0)
            elif label == "TUF":
                plt.xlim(0.0, 70.0)
                plt.ylim(0.0, 70.0)

            plt.show()
        else:
            print("For state: {0} could not plot empty observations".format(label))


def plot_hmm_cluster_contours(state_colors, state_vars, obs_state, nbins, ncontours, state_min_max):

    for state in state_colors:

        print("state: ", state)
        min_x = state_min_max[state]['min_x']
        max_x = state_min_max[state]['max_x']
        min_y = state_min_max[state]['min_y']
        max_y = state_min_max[state]['max_y']

        if state != 'TUF':

            params = state_vars[state]
            state_dist = MultivariateGaussianDistribution(means=np.array(params[0]),
                                                          covariance=np.array(params[1]))

            state_wga_obs = [item[0] for item in obs_state[state]]
            state_no_wga_obs = [item[1] for item in obs_state[state]]

            # plot the observations
            plt.scatter(state_no_wga_obs, state_wga_obs, color=state_colors[state])

            xi, yi = np.mgrid[min([min_x]):max([max_x]):nbins * 1j,
                              min([min_y]):max([max_y]):nbins * 1j]
            zi = []
            valsxi = xi[:, [0]]

            for obs_no_wga in valsxi:
                for obs_wga in yi[0]:
                    zi.append(state_dist.probability((obs_wga, obs_no_wga)))

            zi = np.array(zi)
            zi = zi.reshape(yi.shape)
            plt.contour(xi, yi, zi, ncontours, colors='black')

        elif state == 'TUF':

            params = state_vars[state]
            comp1 = MultivariateGaussianDistribution(means=np.array(params["comp0"][0]),
                                                     covariance=np.array(params["comp0"][1]))

            comp2 = MultivariateGaussianDistribution(means=np.array(params["comp1"][0]),
                                                     covariance=np.array(params["comp1"][1]))

            tuf_mixture = GeneralMixtureModel([comp1, comp2], weights=params["weights"])

            state_wga_obs = [item[0] for item in obs_state[state]]
            state_no_wga_obs = [item[1] for item in obs_state[state]]

            # plot the observations
            plt.scatter(state_no_wga_obs, state_wga_obs, color=state_colors[state])

            xi, yi = np.mgrid[min([min_x]):max([max_x]):nbins * 1j,
                              min([min_y]):max([max_y]):nbins * 1j]

            zi = []
            valsxi = xi[:, [0]]

            for obs_no_wga in valsxi:
                for obs_wga in yi[0]:
                    prob = tuf_mixture.probability(np.array([[obs_wga, obs_no_wga]], dtype='object'))
                    zi.append(prob)

            zi = np.array(zi)
            zi = zi.reshape(yi.shape)
            plt.contour(xi, yi, zi, 14, colors='black')

    plt.xlabel("NO-WGA ")
    plt.ylabel("WGA")
    plt.grid(True)
    plt.show()



