import os
import ray
from pathlib import Path

from compute_engine.src.exceptions import Error
from compute_engine.src.enumeration_types import JobResultEnum
from compute_engine.src.actors import  ViterbiPathActor

class TestRayActors:

    def test_viterbi_path_actor_1(self):
        try:

            #create a remote object
            actor = ViterbiPathActor.remote(input=None)
        except Exception as e:
            assert  'ViterbiPathActor with None input' == str(e)

    def test_viterbi_path_actor_2(self):
        try:
            actor = ViterbiPathActor.remote(input={})
            obj_ref = actor.start.remote()
            result = ray.get(obj_ref)
            assert result["error_msg"] == "Key 'region_filename' not found"
        except Exception as e:
            print(str(e))

    def test_viterbi_path_actor_3(self):
        try:
            actor = ViterbiPathActor.remote(input={'region_filename': Path("/home/alex/qi3/hmmtuf/compute_engine/tests/data/region_0_REGION_1_CHR_1_MEAN_CUTOFF.txt"),
                                                   'viterbi_path_filename': Path("/home/alex/qi3/hmmtuf/compute_engine/tests/data/test_viterbi_path_actor.txt"),
                                                   'tuf_del_tuf_path_filename': Path("/home/alex/qi3/hmmtuf/compute_engine/tests/data/test_tuf_del_tuf_path_actor.txt"),
                                                   'hmm_model_filename': Path('/home/alex/qi3/hmmtuf/compute_engine/tests/data/HMM1.json'),
                                                   'chromosome': 'chr1'})
            obj_ref = actor.start.remote()
            result = ray.get(obj_ref)
            assert result["state"] == JobResultEnum.SUCCESS
        except Exception as e:
            print(str(e))

    def run(self):
        self.test_viterbi_path_actor_1()
        self.test_viterbi_path_actor_2()
        self.test_viterbi_path_actor_3()


if __name__ == '__main__':

    ray.init(num_cpus=2, num_gpus=0)
    tests = TestRayActors()
    tests.run()