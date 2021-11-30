from pathlib import Path
import csv
import json
from compute_engine.src.file_readers import ViterbiPathReader, CoordsBedFile
from compute_engine.src.enumeration_types import JobResultEnum


def compute_bed_comparison(task_id: str, step_size: int = -1) -> dict:

    # avoid circular imports
    from .models import BedComparisonModel

    # attempt to get the model
    #response_dict = BedComparisonModel.response_dict()

    try:
        model = BedComparisonModel.objects.get(task_id=task_id)

        viterbi_filename = Path(model.viterbi_filename)
        bed_filename = Path(model.bed_filename)
        state_counters, coords = __search(viterbi_filename=viterbi_filename,
                                          bed_filename=bed_filename,  step_size=step_size)

        with open(model.result_filename, 'w', newline='\n') as fh:
            writer = csv.writer(fh, delimiter=',')

            for item in coords:
                row = [item[0], item[1], item[2], coords[item]]
                writer.writerow(row)

        # save the summary
        with open(model.summary_filename, 'w') as fp:
            json.dump(state_counters, fp)

        model.result = JobResultEnum.SUCCESS.name
        model.save()
    except Exception as e:
        model.update_for_exception(err_msg=str(e), save=True)

    return dict() #response_dict


def __search(viterbi_filename: Path, bed_filename: Path, step_size: int) -> tuple:

    if step_size <=0:
        return __search_default(viterbi_filename=viterbi_filename, bed_filename=bed_filename)
    else:
        return __search_with_step_size(viterbi_filename=viterbi_filename,
                                       bed_filename=bed_filename, step_size=step_size)


def __search_with_step_size(viterbi_filename: Path,
                            bed_filename: Path, step_size: int) -> tuple:

    if step_size < 1:
        raise ValueError(f"Invalid step_size={step_size}. step_size must be > 1")

    viterbi_reader = ViterbiPathReader(mode='dict_coords_state')
    values = viterbi_reader(filename=viterbi_filename)
    bed_coords_reader = CoordsBedFile(mode='tuple_list', delimiter=",")
    bed_coords = bed_coords_reader(filename=bed_filename)

    state_counters = dict()
    state_counters['TUF'] = 0
    state_counters['OTHER'] = 0
    state_counters["NOT_FOUND"] = 0
    coords = dict()

    for item in bed_coords:

        chromosome = item[0]
        start = item[1]
        end = item[2]

        if start >= end:
            raise ValueError("Invalid start/end indexes {0}/{1}".format(start, end))

        ranges = [(i, i + step_size - 1) for i in range(start, end + 1, step_size)]

        if len(ranges) == 0:
            raise ValueError("Empty ranges")

        for item in ranges:

            if tuple((chromosome, item[0], item[1])) in values:
                if values[(chromosome, item[0], item[1])] == 'TUF':
                    state_counters['TUF'] += 1
                    coords[(item[0], item[1])] = 'TUF'
                else:
                    state_counters['OTHER'] += 1
                    coords[(item[0], item[1])] = 'OTHER'
            else:
                state_counters['NOT_FOUND'] += 1
                coords[(item[0], item[1])] = 'NOT_FOUND'

    return state_counters, coords


def __search_default(viterbi_filename: Path, bed_filename: Path) -> tuple:

    #import pdb
    #pdb.set_trace()

    viterbi_reader = ViterbiPathReader(mode='dict_coords_state')
    values = viterbi_reader(filename=viterbi_filename)
    bed_coords_reader = CoordsBedFile(mode='tuple_list', delimiter=",")
    bed_coords = bed_coords_reader(filename=bed_filename)

    state_counters = dict()
    state_counters['TUF'] = 0
    state_counters['OTHER'] = 0
    state_counters["NOT_FOUND"] = 0
    coords = dict()

    for item in bed_coords:

        if tuple(item) in values:
            if values[tuple(item)] == 'TUF':
                state_counters['TUF'] += 1
                coords[tuple(item)] = 'TUF'
            else:
                state_counters['OTHER'] += 1
                coords[tuple(item)] = 'OTHER'
        else:
            state_counters["NOT_FOUND"] += 1
            coords[tuple(item)] = 'NOT_FOUND'

    return state_counters, coords