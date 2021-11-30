from pathlib import Path
from compute_engine import INFO
from compute_engine.src.enumeration_types import JobResultEnum


def update_for_exception(result, computation, err_msg):
    computation.error_explanation = err_msg
    computation.result = JobResultEnum.FAILURE.name
    result["result"] = JobResultEnum.FAILURE.name
    result["error_explanation"] = err_msg
    return result, computation


def build_files_map(files_created: list, files_created_map: dict,
                    counter_region_id: int, path: Path) -> None:
    for name in files_created:
        if name in files_created_map[counter_region_id]:
            files_created_map[counter_region_id][name].append(path / name)
        else:
            files_created_map[counter_region_id][name] = [path / name]


def concatenate_files(files_created_map, out_path):
    for idx in files_created_map:
        names = files_created_map[idx].keys()

        for name in names:
            print("{0} Concatenating bed {1} to {2}".format(INFO, files_created_map[idx][name],
                                                            out_path + name))
            # concatenate the files
            tufdel.concatenate_bed_files(files_created_map[idx][name], outfile=out_path + name)

