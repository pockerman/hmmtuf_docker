import itertools
import csv
import multiprocessing as mp
import sys

if "/home/alex/qi3/hmmtuf" not in sys.path:
    sys.path.append("/home/alex/qi3/hmmtuf")

from compute_engine.src.string_sequence_calculator import TextDistanceCalculator
from compute_engine.src.file_readers import NuclOutFileReader
from compute_engine.src.utils import INFO
from compute_engine.src.utils import read_json


def reverse_complement_table(seq, tab):
    return seq.translate(tab)[::-1]

def write_pair_segments_distances(proc_id, master_proc, start, end, input_file,
                                  line_counter, outdir, distance_type, error_map):

    try:

        import sys
        from pathlib import Path

        if "/home/alex/qi3/hmmtuf" not in sys.path:
            sys.path.append("/home/alex/qi3/hmmtuf")

        from compute_engine.src.string_sequence_calculator import TextDistanceCalculator
        from compute_engine.src.file_readers import NuclOutFileReader
        from compute_engine.src.utils import INFO

        # read original seqs
        filereader = NuclOutFileReader(exclude_seqs=["NO_REPEATS"])  # NuclOutFileReader()
        sequences = filereader(filename=input_file)

        if end == -1:
            end = len(sequences)

        if start >= end:
            raise ValueError("Error: start index={0} greater than end index={1}".format(start, end))
            
        if proc_id == master_proc:
            print("{0} Master process is working on [{1}, {2})".format(INFO, start, end))

        tab = str.maketrans("ACTGRMW", "TGACYKS")
        tabPP = str.maketrans("AGCT", "RRYY")
        tabAK = str.maketrans("ACGT", "MMKK")
        tabWS = str.maketrans("ATCG", "WWSS")

        # build the wrapper
        calculator = TextDistanceCalculator.build_calculator(name=distance_type)

        part_counter = 0
        touched = []
        lines = []

        # only work on the part assigned [start, end)
        for i in range(start, end, 1):
            for j in range(start, len(sequences)):
                if (i, j) not in touched and (j, i) not in touched:

                    chr_seq_1 = sequences[i][0].strip()
                    start1 = sequences[i][1]
                    end1 = sequences[i][2]
                    seq1 = sequences[i][3].strip()
                    state1 = sequences[i][4].strip()

                    # print(sequences[j])
                    chr_seq_2 = sequences[j][0].strip()
                    start2 = sequences[j][1]
                    end2 = sequences[j][2]
                    seq2 = sequences[j][3].strip()
                    state2 = sequences[j][4].strip()

                    if len(seq1) + len(seq2) < 200:

                        # calculate the distance
                        distance1 = calculator.normalized_distance(seq1, seq2)
                        distance2 = calculator.normalized_distance(seq1, reverse_complement_table(seq=seq2, tab=tab))

                        distance = min(distance1, distance2)

                        PPseq1 = seq1.translate(tabPP)
                        AKseq1 = seq1.translate(tabAK)
                        WSseq1 = seq1.translate(tabWS)

                        PPseq2 = seq2.translate(tabPP)
                        AKseq2 = seq2.translate(tabAK)
                        WSseq2 = seq2.translate(tabWS)

                        PPdist = calculator.normalized_distance(PPseq1, PPseq2)
                        PPdist_rev = calculator.normalized_distance(PPseq1,
                                                                    reverse_complement_table(seq=PPseq2, tab=tab))

                        pp_distance = min(PPdist, PPdist_rev)

                        AKdist = calculator.normalized_distance(AKseq1, AKseq2)
                        AKdist_rev = calculator.normalized_distance(AKseq1,
                                                                    reverse_complement_table(seq=AKseq2, tab=tab))

                        ak_distance = min(AKdist, AKdist_rev)

                        WSdist = calculator.normalized_distance(WSseq1, WSseq2)
                        WSdist_rev = calculator.normalized_distance(WSseq1,
                                                                    reverse_complement_table(seq=WSseq2, tab=tab))

                        ws_distance = min(WSdist, WSdist_rev)

                        lines.append([chr_seq_1, start1, end1, seq1, state1,
                                      chr_seq_2, start2, end2, seq2, state2,
                                      distance, pp_distance, ak_distance, ws_distance])

                        # if we reached the batch then flush
                        # to the output file
                        if len(lines) == line_counter:

                            filename = Path(outdir + "part_seqs_pairs_proc_" + str(proc_id) + "_" + str(part_counter) + ".csv")

                            if filename.is_file():
                                raise ValueError("ERROR: filename={0} Exists".format(filename))

                            if proc_id == master_proc:
                                print("{0} Writing to {1}".format(INFO, filename))

                            with open(filename, 'w', newline="\n") as fh:
                                writer = csv.writer(fh, delimiter=",")

                                writer.writerow(["#", "ChrSeq-1", "StartSeq-1", "EndSeq-1", "Seq-1", "HMM-State-1",
                                                 "ChrSeq-2", "StartSeq-2", "EndSeq-2", "Seq-2", "HMM-State-2",
                                                 "Distance", "Distance-PP", "Distance-AK", "Distance-WS"])

                                for line in lines:
                                    writer.writerow(line)

                            if proc_id == master_proc:
                                print("{0} Finished writing to {1}".format(INFO, filename))

                            lines = []
                            part_counter += 1
                    touched.append((i, j))
                    touched.append((j, i))

        # make sure that we flush any remaining
        # lines

        if len(lines) != 0:

            if len(lines) >= line_counter:
                raise ValueError("ERROR: Detected len(lines) >={0} not written to file".format(len(lines)))

            filename = Path(outdir + "part_seqs_pairs_proc_" + str(proc_id) +"_" + str(part_counter) + ".csv")

            if filename.is_file():
                raise ValueError("ERROR: filename={0} Exists".format(filename))

            if proc_id == master_proc:

                print("{0} Writing remaining lines to {1}".format(INFO, filename))
                print("{0} Writing to {1}".format(INFO, filename))

            with open(filename, 'w', newline="\n") as fh:
                writer = csv.writer(fh, delimiter=",")

                writer.writerow(["#", "ChrSeq-1", "StartSeq-1", "EndSeq-1", "Seq-1", "HMM-State-1",
                                 "ChrSeq-2", "StartSeq-2", "EndSeq-2", "Seq-2", "HMM-State-2",
                                 "Distance", "Distance-PP", "Distance-AK", "Distance-WS"])

                for line in lines:
                    writer.writerow(line)

            if proc_id == master_proc:
                print("{0} Finished writing remaining lines to {1}".format(INFO, filename))

            lines = []
            part_counter += 1

        error_map[proc_id] = "FINISHED SUCCESS"
    except Exception as e:
        error_map[proc_id] = str(e)

def main():

    print("{0} Starting...".format(INFO))

    configuration = read_json(filename="config_cluster.json")
    distance_type = configuration["distance_type"]
    line_counter = configuration["line_counter"]
    load = configuration["load"]

    input_file = configuration["input_file"]
    outdir = configuration["output_file"]
    num_procs = configuration["num_procs"]

    MASTER_PROC_ID = configuration["master_proc_id"]

    print("{0} Master Process is {1}".format(INFO, MASTER_PROC_ID))
    print("{0} Number of processes is {1}".format(INFO, num_procs))
    print("{0} Distance type is {1}".format(INFO, distance_type))
    print("{0} Process load {1}".format(INFO, load))

    manager = mp.Manager()
    err_map = manager.dict()

    for i in range(num_procs):
        err_map[i] = "NO_ERROR"

    procs = []

    start = configuration["start"]
    end = configuration["end"]
    for p in range(num_procs-1):
        print("{0} Process {1} works in [{2},{3})".format(INFO, p, start, (p+1)*load))
        procs.append(mp.Process(target=write_pair_segments_distances,
                                group=None,
                                args=(p, MASTER_PROC_ID,
                                      start, (p+1)*load, input_file,
                                      line_counter, outdir,
                                      distance_type, err_map)))
        procs[p].start()
        start = (p+1)*load

    print("{0} Master Process {1} works in [{2},{3})".format(INFO, MASTER_PROC_ID, start, end))

    # main process is working as well
    write_pair_segments_distances(proc_id=MASTER_PROC_ID, master_proc=MASTER_PROC_ID,
                                  start=start, end=end,
                                  input_file=input_file,
                                  line_counter=line_counter,
                                  outdir=outdir,
                                  distance_type=distance_type, error_map=err_map)

    # make sure we wait here
    for p in procs:
        p.join()


    for i in range(num_procs):

        if err_map[i] != "FINISHED SUCCESS":
            print("{0} ERROR detected for process {1}. Error Message {2}".format(INFO, i, err_map[i]))
        else:
            print("{0} Process {1} finished with success".format(INFO, i))
    print("{0} Finished...".format(INFO))

if __name__ == '__main__':
    main()
