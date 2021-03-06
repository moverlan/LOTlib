
from scipy.io import loadmat
from LOTlib.DataAndObjects import FunctionData
from LOTlib.Visualization.MCMCSummary.VectorSummary import *


def sample_grammar_hypotheses(sampler, skip, cap, print_=False):
    summary = VectorSummary(skip=skip, cap=cap)
    if print_:
        i = 0
        print '^*'*60, '\nGenerating GrammarHypothesis Samples\n', '^*'*60
        for h in summary(sampler):
            i += 1
            if i % (sampler.steps/20) == 0:
                print ['%.3f' % v for v in h.value]
                print i, '-'*100
                print h.prior, h.likelihood, h.posterior_score
    else:
        for h in summary(sampler): pass
    return summary


def print_dist(vals, posteriors):
    print '@'*120
    for val, post in zip(vals, posteriors):
        print val, '\t', post
    print '@'*120


# ============================================================================================================

def import_data_from_mat():
    """Script for loading Joshs' number game data.

    Data is originally in probabilitiy (i.e. float) format, so (# yes, # no) pairs are estimated by
    assuming 20 human participants.

    """
    mat = loadmat('/Users/ebigelow35/Desktop/skool/piantado/LOTlib/LOTlib/Examples/GrammarInference'
                  '/NumberGame/number_game_data.mat')
    mat_data = mat['data']
    number_game_data = []

    for d in mat_data:

        input_data = d[0][0].tolist()
        output_data = {}

        for i in range(len(d[1][0])):
            key = d[1][0][i]
            associated_prob = d[2][0][i]
            associated_yes = int(associated_prob * 20)
            output_data[key] = (associated_yes, 20-associated_yes)    # est. (# yes, # no) responses

        function_datum = FunctionData(input=input_data, output=output_data)
        number_game_data.append(function_datum)

    return number_game_data


def visualize_dist(probs, dist, rule_name='RULE_'):
    """Visualize results from VectorHypothesis.conditional_distribution.

    The x-axis is the prior values we're inputting for the given rule (probs).
    The y-axis is the summed posterior of the human data given these prior values

    """
    fig, ax = plt.subplots()
    rects = plt.bar(probs, dist)

    plt.xlabel('Grammar Rule Probability')
    plt.ylabel('Pr. of human data')
    plt.title('Prob. of human data given prob. for rule: '+rule_name)
    plt.show()
