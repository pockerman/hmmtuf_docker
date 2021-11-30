"""
Helper functions for tuf-core files manipulation
"""
import numpy as np
import os
import shutil
from pathlib import Path
from compute_engine.src.utils import INFO
from compute_engine.src.utils import get_sequence_chunks

def get_align_unit_seq_fasta(working_dir):

    with open(working_dir / "align.unit_seq.fasta", "r") as fh:

        seq = ""
        counter = 0
        for line in fh:
            if line.startswith(">"):
                counter += 1
            else:
                line = line.rstrip('\n')
                line = line.replace("-", "")
                seq += line

        #seq = seq.replace("-", "")
        return counter, seq

def get_unit_seq_fasta(working_dir):

    with open(working_dir / "unit_seq.fasta", "r") as fh:

        seq = ""
        counter = 0
        for line in fh:
            if line.startswith(">"):
                counter += 1
            else:
                line = line.rstrip('\n')
                line = line.replace("-","")
                seq += line

        #seq = seq.replace("-","")
        return counter, seq

def is_contributing_weblogo(weblogo_dir: Path, count_check: int=12) -> bool:

    nucleods = ['A', 'C', 'G', 'T']
    count = 0
    seq = ''


    line_counter = 0
    with open(weblogo_dir / 'weblogo.txt', 'r') as f:

        for line in f:
            count += 1

            # don't process the comment line
            if line.startswith('#'):
                continue

            # checkout from the line which has the maximum
            new_line = line.split('\t')

            if len(new_line) > 5:

                # get the bases counts
                new_line = new_line[1:5]
                new_line = [int(item) for item in new_line]
                max_item = max(new_line)
                nucleod_idx = new_line.index(max_item)

                if nucleod_idx >= 4:
                    raise ValueError("Invalid index for nucleod. "
                                     "Index {0} not in [0,3]".format(nucleod_idx))

                nucleod = nucleods[nucleod_idx]
                seq += nucleod
                line_counter += 1

        # TODO: Make this application defined?
        # write only if it is worth i.e. we have at least
        # 12 observations?
        if count > count_check:

            if len(seq) != 0:
                return True

            return False

        else:
            return False


def get_statistics_from_weblogo(weblogo_dir: Path,
                                repeat: str, count_check: int=12) -> tuple:

    nucleods = ['A', 'C', 'G', 'T']
    count = 0
    seq = ''

    # holds the counters for each base in the repeat
    stats_dir = {}
    line_counter = 0
    with open(weblogo_dir / 'weblogo.txt', 'r') as f:


        for line in f:
            count += 1

            # don't process the comment line
            if line.startswith('#'):
                continue

            # checkout from the line which has the maximum
            new_line = line.split('\t')

            if len(new_line) > 5:

                # get the bases counts
                new_line = new_line[1:5]
                new_line = [int(item) for item in new_line]
                stats_dir [ line_counter ] = new_line
                max_item = max(new_line)
                nucleod_idx = new_line.index(max_item)

                if nucleod_idx >= 4:
                    raise ValueError("Invalid index for nucleod. "
                                     "Index {0} not in [0,3]".format(nucleod_idx))

                nucleod = nucleods[nucleod_idx]
                seq += nucleod
                line_counter += 1

        # TODO: Make this application defined?
        # write only if it is worth i.e. we have at least
        # 12 observations?
        if count > count_check:

            if seq != repeat:
                return False, {}
                #raise ValueError("The given repeat does not "
                #                "match the constructed sequence")

            return True, stats_dir

        else:
            return False, {}
            #raise ValueError(f"The computed count {count} does not match the given {count_check}")


def write_from_weblogo(weblogo_dir: Path, out_repeats, out_nucleods,
                       out_repeats_info, chrom: str,
                       start: int, stop: int, region_type: str, count_check: int=12):

    """
    write to the outrep and to the nucl_out files
    information
    """

    nucleods = ['A', 'C', 'G', 'T']
    count = 0
    seq = ''

    with open(weblogo_dir / 'weblogo.txt', 'r') as f:

        for line in f:
            count += 1

            # don't process the comment line
            if line.startswith('#'):
                continue

            # checkout from the line which has the maximum
            new_line = line.split('\t')

            if len(new_line) > 5:
                new_line = new_line[1:5]
                new_line = [int(item) for item in new_line]
                max_item = max(new_line)
                nucleod_idx = new_line.index(max_item)

                if nucleod_idx >= 4:
                    raise ValueError("Invalid index for nucleod. "
                                     "Index {0} not in [0,3]".format(nucleod_idx))

                nucleod = nucleods[nucleod_idx]
                seq += nucleod

    # TODO: Make this application defined?
    # write only if it is worth i.e. we have at least
    # 12 observations?
    if count > count_check:

        #print("{0} Writing to: out_repeats".format(INFO))
        out_repeats.write(chrom + '\t' + str(start) + '\t' + str(stop) + '\n')

        if len(seq) != 0:

            # open the unit sequences
            align_seq_count, align_seq = get_align_unit_seq_fasta(working_dir=weblogo_dir)
            unit_seq_count, unit_seq = get_unit_seq_fasta(working_dir=weblogo_dir)

            out_nucleods.write(chrom + '\t' + str(start) + '\t' + str(stop) + '\t' + seq + '\t' + region_type + '\n')
            out_repeats_info.write(chrom + '\t' + str(start) + '\t' + str(stop) + "\t" +
                                   str(max(align_seq_count, unit_seq_count)) + "\t" + align_seq + "\t" + unit_seq +'\n')
    else:

        # this is now classified as NO_REPEATS
        out_nucleods.write(chrom + '\t' + str(start) + '\t' + str(stop) + '\t' + "NO_REPEATS" + '\t' + region_type + '\n')


def gcpercent(cseq, chunk_size=100):
    """
    Calculate GC percent from the sequence
    """

    count = 0
    count += cseq.count('G')
    count += cseq.count('g')
    count += cseq.count('C')
    count += cseq.count('c')
    count = str(int(count / len(cseq) * 100))

    # if sequence is less than the chunk_size
    # then non max/min calculation
    if len(cseq) <= chunk_size:
        return count + "_NA_" + "NA"

    # otherwise split the sequence into chuncks of size 100
    # amd calculate max/min GC percentage
    chunks = get_sequence_chunks(cseq=cseq, chunk_size=chunk_size) #[cseq[i:i + chunk_size] for i in range(0, len(cseq), chunk_size)]
    rslt = []
    for chunk in chunks:
        tmp = gcpercent(cseq=chunk, chunk_size=chunk_size)
        tmp = int(tmp.split("_")[0])
        rslt.append(tmp)

    min_rslt = min(rslt)
    max_rslt = max(rslt)
    return count + "_" + str(min_rslt) + "_" + str(max_rslt)

# this function copied from gquadfinder
def gquadcheck(sequence):

    minscore = 2
    window = 50

    cseq, scores = BaseScore(sequence)
    score = CalScore(scores, window)
    outG4 = GetG4(sequence, score, minscore, window, len(scores))

    if len(outG4) == 0:
        return False, []

    mscore = WriteSeq(sequence, score, outG4, window, len(scores))

    if len(mscore):
        return True, mscore
    else:
        return False, mscore

def remove_directories(chromosome, spade_output):

    #global SPADE_OUTPATH
    directories = os.listdir(path=spade_output)

    for name in directories:

        # remove gb files
        if name.endswith('gb'):
            os.remove(os.path.join(spade_output, name))

        if name.startswith(chromosome + '_'):
            if os.path.isdir(spade_output + name):
                shutil.rmtree(os.path.join(spade_output, name))

        # if this is a nucl_ directory
        if name.startswith('nucl_'):
            files = os.listdir(path=spade_output + name)

            for f in files:
                if f != 'weblogo.txt':
                    os.remove(os.path.join(spade_output + name, f))


def match(win, altwin):
    m = 0
    for a,b in zip (win,altwin):
        if a == b:
            m += 1
    if m > 8:
        return True
    else:
        return False

def create_bed(line, ccheck):

    data = {}
    line = line.split(':')
    if len(line) == 5:
        data['chr'] = line[0]
        data['loc'] = line[2]
        data['means'] = line[3]
        data['state'] = line[4].rstrip()
        data['loc'] = data['loc'].replace('(', '')
        data['loc'] = data['loc'].replace(')', '')
        data['loc'] = data['loc'].split(',')
    elif len(line) == 4:
        data['chr'] = ccheck
        data['loc'] = line[1]
        data['means'] = line[2]
        data['state'] = line[3].rstrip()
        data['loc'] = data['loc'].replace('(', '')
        data['loc'] = data['loc'].replace(')', '')
        data['loc'] = data['loc'].split(',')
    elif len(line) == 1:
        print("{0} start of file".format(INFO))
    else:

        # how to we expect the Viterbi path to be formated?
        print("{0} Incorrect format of viterbi".format(INFO))
        raise Error(message="Invalid Viterbi path formt")
    return data

# this function copied from gquadfinder
def WriteSeq(line,liste, LISTE, F, Len ):

    i,k,I=0,0,0
    a=b=LISTE[i]
    MSCORE=[]

    if len(LISTE) > 1:
        c = LISTE[i+1]
        while i < len(LISTE)-2:
            if c == b+1:
                k = k+1
                i = i+1
            else:
                I = I+1
                seq = line[a:a+F+k]
                sequence, liste2 = BaseScore(seq)
                MSCORE.append(abs(round(np.mean(liste2), 2)))
                k = 0
                i = i+1
                a = LISTE[i]
            b = LISTE[i]
            c = LISTE[i+1]
        I=I+1
        seq=line[a:a+F+k+1]
        sequence, liste2 = BaseScore(seq)
        MSCORE.append(abs(round(np.mean(liste2), 2)))
    else:
        I = I+1
        seq = line[a:a+F]
        MSCORE.append(abs(liste[a]))
    return MSCORE


# this function copied from gquadfinder
def BaseScore(line):
    item, liste = 0, []

    while item < len(line):
        if item < len(line) and (line[item] == "G" or line[item] == "g"):
            liste.append(1)
            if item + 1 < len(line) and (line[item + 1] == "G" or line[item + 1] == "g"):
                liste[item] = 2
                liste.append(2)
                if item + 2 < len(line) and (line[item + 2] == "G" or line[item + 2] == "g"):
                    liste[item + 1] = 3
                    liste[item] = 3
                    liste.append(3)
                    if item + 3 < len(line) and (line[item + 3] == "G" or line[item + 3] == "g"):
                        liste[item] = 4
                        liste[item + 1] = 4
                        liste[item + 2] = 4
                        liste.append(4)
                        item = item + 1
                    item = item + 1
                item = item + 1
            item = item + 1
            while item < len(line) and (line[item] == "G" or line[item] == "g"):
                liste.append(4)
                item = item + 1

        elif item < len(line) and line[item] != "G" and line[item] != "g" and line[item] != "C" and line[item] != "c":
            liste.append(0)
            item = item + 1

        elif item < len(line) and (line[item] == "C" or line[item] == "c"):
            liste.append(-1)
            if item + 1 < len(line) and (line[item + 1] == "C" or line[item + 1] == "c"):
                liste[item] = -2
                liste.append(-2)
                if item + 2 < len(line) and (line[item + 2] == "C" or line[item + 2] == "c"):
                    liste[item + 1] = -3
                    liste[item] = -3
                    liste.append(-3)
                    if item + 3 < len(line) and (line[item + 3] == "C" or line[item + 3] == "c"):
                        liste[item] = -4
                        liste[item + 1] = -4
                        liste[item + 2] = -4
                        liste.append(-4)
                        item = item + 1
                    item = item + 1
                item = item + 1
            item = item + 1

            while item < len(line) and (line[item] == "C" or line[item] == "c"):
                liste.append(-4)
                item = item + 1

        else:
            # la fin du la ligne ou y a des entrers
            item = item + 1
    return line, liste


# this function copied from gquadfinder
def CalScore(liste, k):

    Score_Liste=[]
    for i in range(len(liste)-(k-1)):
        j, Sum = 0, 0

        while j < k:
            Sum = Sum + liste[i]
            j = j + 1
            i = i + 1
        Mean=Sum/float(k)
        Score_Liste.append(Mean)
    return Score_Liste

# this function copied from gquadfinder
def GetG4(line, liste, Window, k, Len):

    LG4 = []
    for i in range(len(liste)):
        if liste[i] >= float(Window) or liste[i] <= - float(Window):
            seq = line[i:i+k]
            LG4.append(i)
    return LG4



def concatenate_bed_files(bedfiles, outfile):

    with open(outfile, 'a') as total_f:
        for file_name in bedfiles:
            with open(file_name, 'r') as f:

                for line in f:
                    total_f.write(line)