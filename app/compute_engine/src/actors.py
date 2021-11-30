from abc import abstractmethod
from compute_engine.src.enumeration_types import JobResultEnum
from compute_engine.src.exceptions import Error
from compute_engine.src.region import Region
from compute_engine.src import hmm_loader
from compute_engine.src import tufdel
from compute_engine.src import viterbi_calculation_helpers as viterbi_helpers



class ActorBase(object):
    """
    Base class for deriving Ray Actors for the various
    computations
    """
    def __init__(self, input: dict) -> None:
        self._job_state = JobResultEnum.PENDING
        self._input = input
        self._output = {}

    @property
    def state(self) -> JobResultEnum:
        return self._job_state

    @state.setter
    def state(self, value: JobResultEnum):
        self._job_state = value

    @property
    def input(self) -> dict:
        return self._input

    @property
    def output(self) -> dict:
        return self._output

    @output.setter
    def output(self, value) -> dict:
        self._output = value

    def set_output_value(self, key, value) -> None:
        self._output[key] = value

    def input_item(self, key: str):

        if key not in self._input:
            return None

        return self._input[key]

    @abstractmethod
    def start(self):
        raise Error(message="RayJob.start must be overriden")

class ViterbiPathCalulation(ActorBase):

    def __init__(self, input: dict) -> None:
        ActorBase.__init__(self, input=input)

    def start(self) -> None:

        try:
            self.state = JobResultEnum.CREATED
            self.set_output_value("state", self.state)

            region = Region.load(filename=self._input['region_filename'])
            region.get_mixed_windows()

            # get the sequence from the region
            sequence = region.get_region_as_rd_mean_sequences_with_windows(size=None,
                                                                           window_type='BOTH',
                                                                           n_seqs=1,
                                                                           exclude_gaps=False)

            viterbi_path_filename = self._input['viterbi_path_filename']
            hmm_model_filename = self._input['hmm_model_filename']
            chromosome = self._input['chromosome']
            hmm_model = hmm_loader.build_hmm(hmm_file=hmm_model_filename)

            viterbi_path, observations, \
            sequence_viterbi_state = viterbi_helpers.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                                         chromosome=chromosome,
                                                                         filename=viterbi_path_filename,
                                                                         append_or_write='w')

            tuf_delete_tuf = viterbi_helpers.filter_viterbi_path(path=viterbi_path[1][1:],
                                                                 wstate='TUF',
                                                                 limit_state='Deletion',
                                                                 min_subsequence=1)

            segments = viterbi_helpers.get_start_end_segment(tuf_delete_tuf, sequence)

            filename = self._input['tuf_del_tuf_filename']
            viterbi_helpers.save_segments(segments=segments, chromosome=chromosome, filename=filename)
            self.state = JobResultEnum.SUCCESS
        except Exception as e:

            self.state = JobResultEnum.FAILURE
            self.set_output_value("error_msg", "Key {0} not found".format(str(e)))

        self.set_output_value("state", self.state)
        return self._output


class SpadeCalculation(ActorBase):
    """
    Wrap the Spade calculation
    """

    def __init__(self, input: dict) -> None:
        ActorBase.__init__(self, input=input)

    def start(self) -> None:

        try:
            self.state = JobResultEnum.CREATED
            self.set_output_value("state", self.state)

            # get the TUF-DEL-TUF this is for every chromosome and region
            # path = task_path + chromosome + "/" + region_model.name + "/"
            ref_seq_file = self._input["ref_seq_file"]
            chromosome = self._input["chromosome"]
            chromosome_idx = self._input["chromosome_idx"]
            viterbi_path_filename = self._input["viterbi_path_filename"]
            test_me = self._input["test_me"]
            nucleods_path = self._input["nucleods_path"]
            remove_dirs = self._input["remove_dirs"]
            path = self._input["path"]
            test_me = self._input["test_me"]
            files_created = tufdel.main(path=str(path),
                                        fas_file_name=str(ref_seq_file),
                                        chromosome=chromosome,
                                        chr_idx=chromosome_idx,
                                        viterbi_file=str(viterbi_path_filename),
                                        nucleods_path=str(nucleods_path),
                                        remove_dirs=remove_dirs, test_me=test_me)

            self.output["files_created"] = files_created
            self.state = JobResultEnum.SUCCESS
        except Exception as e:
            self.state = JobResultEnum.FAILURE
            self.set_output_value("error_msg", "Key {0} not found".format(str(e)))

        self.set_output_value("state", self.state)
        return self._output


class ViterbiPathActor(ActorBase):
    """
    Actor for computing the Viterbi paths
    """

    def __init__(self, input: dict) -> None:

        if input is None:
            raise Error(message="ViterbiPathActor with None input")
        ActorBase.__init__(self, input=input)

    def start(self):

        try:

            print("{0} use_spade {1}".format(INFO, self.input['use_spade']))
            print("{0} remove_dirs {1}".format(INFO, self.input['remove_dirs']))

            self.state = JobResultEnum.CREATED
            self.set_output_value("state", self.state)

            calculator = ViterbiPathCalulation(input=self.input)
            calculator.start()

            if "use_spade" in self.input and self.input["use_spade"]:
                spade = SpadeCalculation(input=self.input)
                spade.start()
            self.state = JobResultEnum.SUCCESS

        except KeyError as e:

            self.state = JobResultEnum.FAILURE
            self.set_output_value("error_msg", "Key {0} not found".format(str(e)))

        self.set_output_value("state", self.state)
        return self._output

"""
@ray.remote
class ViterbiGroupPathActor(RayActorBase):

    def __init__(self, input: dict) -> None:

        if input is None:
            raise Error(message="ViterbiPathActor with None input")
        RayActorBase.__init__(self, input=input)

    def start(self):

        try:

            print("{0} group_tip: {1}".format(INFO, self.input['group_tip']))
            print("{0} use_spade {1}".format(INFO, self.input['use_spade']))
            print("{0} remove_dirs {1}".format(INFO, self.input['remove_dirs']))

            self.state = JobResultEnum.CREATED
            self.set_output_value("state", self.state)

            calculator = ViterbiPathCalulation(input=self.input)
            calculator.start()

            if "use_spade" in self.input and self.input["use_spade"]:
                spade = SpadeCalculation(input=self.input)
                spade.start()

            self.state = JobResultEnum.SUCCESS

        except KeyError as e:

            self.state = JobResultEnum.FAILURE
            self.set_output_value("error_msg", "Key {0} not found".format(str(e)))

        self.set_output_value("state", self.state)
        return self._output
"""
