import os
import ray
from pathlib import Path
import uuid

from compute_engine.src.exceptions import Error
from compute_engine.src.enumeration_types import JobResultEnum
from hmmtuf_compute.tasks import compute_group_viterbi_path
from hmmtuf_home.models import RegionModel

class TestRayTasks:

    def test_group_viterbi_task_1(self):
        try:

            regions = [] #RegionModel.objects.filter(group_tip__tip='none').order_by('chromosome', 'start_idx')
            task_id = str(uuid.uuid4())
            hmm_name = None
            group_tip = None
            remove_dirs = False
            use_spade = False
            actor = compute_group_viterbi_path(regions=regions, task_id=task_id,
                                               hmm_name=hmm_name, group_tip=group_tip,
                                               remove_dirs=remove_dirs, use_spade=use_spade)
        except Exception as e:
            assert  'ViterbiPathActor with None input' == str(e)


    def run(self):
        self.test_group_viterbi_task_1()

if __name__ == '__main__':

    ray.init(num_cpus=2, num_gpus=0)
    tests = TestRayTasks()
    tests.run()
