import numpy as np
from pomegranate import *
from compute_engine.src.exceptions import Error

def create_hmm_model_from_form(form):


    hmm_model = HiddenMarkovModel(name=form.hmm_name,
                                  start=None, end=None)
    form_states = form.states

    states = []
    for name in form_states:

        state = form_states[name]
        comp_type = state["com_type"]
        if comp_type == "SingleComponent":

            dist_type = state["distribution"]
            if dist_type == "Uniform":
                upper = state["parameters"]["upper"]
                lower = state["parameters"]["lower"]
                state = create_uniform_state(upper=upper, lower=lower, name=name)
                states.append(state)
            elif dist_type == "Normal":
                means = state["parameters"]["means"]
                vars = state["parameters"]["vars"]
                state = create_normal_state(means=means, vars=vars, name=name)
                states.append(state)
            else:
                raise Error("No known SingleComponent distribution type")
        elif comp_type == "MixtureComponent":
            components = state["components"]

            comps = []
            for comp in components:

                if comp["distribution"] == 'Normal':
                    dist = create_normal_component(means=comp["parameters"]["means"],
                                                   vars=comp["parameters"]["vars"])
                    comps.append(dist)
                elif comp["distribution"] == "Uniform":
                    dist = create_uniform_component(upper=comp["parameters"]["upper"],
                                                    lower=comp["parameters"]["lower"])
                    comps.append(dist)
                else:
                    raise Error("No known MixtureComponent distribution type")

            state = State(GeneralMixtureModel(comps, weights=state["weights"]), name=name)
            states.append(state)

    # add states
    hmm_model.add_states(states)

    init_p_vector = form.init_p_vector
    if len(states) != len(init_p_vector):
        raise Error("Number of states is not equal to initial probability vector")

    # setup initial probability

    for name, state in zip(init_p_vector, states):
        hmm_model.add_transition(hmm_model.start, state, init_p_vector[name])

    #setup transition probabilities
    transition_probs = form.transition_probabilities

    for state1 in states:
        for state2 in states:
            hmm_model.add_transition(state1, state2, transition_probs[(state1.name, state2.name)])

    hmm_model.bake(verbose=True)
    return hmm_model


def create_uniform_component(upper, lower):
    dist = IndependentComponentsDistribution([UniformDistribution(upper[0], lower[0]),
                                              UniformDistribution(upper[1], lower[1])])
    return dist


def create_uniform_state(upper, lower, name):

    dist = create_uniform_component(upper=upper, lower=lower)
    state = State(dist, name=name)
    return state


def create_normal_component(means, vars):
    cov = np.array([[vars[0], 0.0], [0.0, vars[1]]])
    dist = MultivariateGaussianDistribution(np.array(means), cov)
    return dist


def create_normal_state(means, vars, name):
    dist = create_normal_component(means=means, vars=vars)
    state = State(dist, name=name)
    return state


def get_distributions_list_from_names(dists_name, params):

        dists = []

        for name in dists_name:
            if name == "normal":
                dists.append(NormalDistribution(params["mean"], params["std"]))
            elif name == "poisson":
                dists.append(PoissonDistribution(params["mean"]))
            elif name == "uniform":
                dists.append(UniformDistribution(params["uniform_params"][0],
                                                 params["uniform_params"][1]))
            else:
                raise Error("Name '{0}' is an unknown distribution ".format(name))
        return dists

