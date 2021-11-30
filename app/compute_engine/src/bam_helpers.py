"""
Utilities for working with bam files
"""

import pysam
import numpy as np
import re

from compute_engine.src.windows import Window
from compute_engine.src.constants import INFO


def extract_windows(chromosome, ref_filename, bam_filename, **args):
    """
    Extract the windows that couple the seq_file and ref_files
    for the given chromosome
    :param chromosome: chromosome name (str)
    :param ref_file: The reference file
    :param test_file: The sequence file
    :return:
    """

    windowcapacity = args["windowsize"]
    start_idx = args["start_idx"]
    end_idx = args["end_idx"]

    # the windows list
    windows = []

    with pysam.FastaFile(ref_filename) as fastafile:
        print("{0} Reference file: {1}".format(INFO, fastafile.filename))

        with pysam.AlignmentFile(bam_filename, "rb") as sam_file:
            print("{0} Sam file: {1} ".format(INFO, sam_file.filename))

            wcounter = 0
            while start_idx < end_idx:
                sam_output = window_sam_file(chromosome=chromosome,
                                             sam_file=sam_file,
                                             fastafile=fastafile,
                                             start=start_idx, end=start_idx + windowcapacity,
                                             **args)
                windows.append(Window(idx=wcounter,
                                      capacity=windowcapacity,
                                      samdata=sam_output))

                start_idx += windowcapacity
                wcounter += 1

    return windows


def window_sam_file(chromosome, sam_file, fastafile,
                    start, end, **kwargs):
    refseq = ''  # store for the refseq
    samseq = []  # stote for the sample
    pos = []  # reference pos
    nseq = []  # all reads
    nalign = []  # quality limited reads
    head = 0  # whether read starts in window
    head1 = 0  # start of read 1 in pair
    head2 = 0  # start of read 2 in pair
    read1 = 0  # equivalent nalign just for read 1s in pairs
    read2 = 0  # as above for read 2s
    errorAlert = False

    truncate = kwargs['sam_read_config']['truncate']
    ignore_orphans = kwargs['sam_read_config']['ignore_orphans']
    max_depth = kwargs['sam_read_config']['max_depth']
    qual = kwargs['sam_read_config'].get('quality_threshold', None)
    add_indels = kwargs['sam_read_config']['add_indels']

    try:

        for pcol in sam_file.pileup(chromosome, start, end,
                                    truncate=truncate,
                                    ignore_orphans=ignore_orphans,
                                    max_depth=max_depth):

            if qual is not None:
                pcol.set_min_base_quality(qual)

                # fill in start when there are no reads present
                while pcol.reference_pos != start:
                    samseq.append('_')
                    refseq += fastafile.fetch(chromosome, start, start + 1)
                    pos.append(start)
                    nseq.append(0)
                    nalign.append(0)
                    start += 1

                # collect metrics for pileup column
                pos.append(start)
                nseq.append(pcol.nsegments)  # all reads over a pileup column
                nalign.append(pcol.get_num_aligned())  # above but quality limited

                for p in pcol.pileups:
                    head += p.is_head  # start of read present
                    read1 += p.alignment.is_read1  # first of mate pair (from nalign)
                    read2 += p.alignment.is_read2  # second of mate pair (from nalign)
                    if p.is_head == 1 and p.alignment.is_read1 == 1:  # above but is start of read
                        head1 += 1
                    if p.is_head == 1 and p.alignment.is_read2 == 1:
                        head2 += 1

                # get bases from reads at pileup column (quality limited)
                try:
                    if pcol.get_num_aligned() == 0:
                        samseq.append('_')
                        refseq += fastafile.fetch(chromosome, pcol.reference_pos, pcol.reference_pos + 1)
                    else:
                        x = pcol.get_query_sequences(add_indels=add_indels)
                        x = [a.upper() for a in x]
                        samseq.append(set(x))  # store as unique set
                        refseq += fastafile.fetch(chromosome, pcol.reference_pos, pcol.reference_pos + 1)
                except Exception as e:  # may fail if large number of reads
                    try:
                        x = pcol.get_query_sequences(add_indels=add_indels)
                        x = [a.upper() for a in x]
                        samseq.append(set(x))  # store as unique set
                        refseq += fastafile.fetch(chromosome, pcol.reference_pos, pcol.reference_pos + 1)
                    except Exception as e:
                        errorAlert = True
                start += 1

        # fill in end if no reads at end of window
        while start < end:
            samseq.append('_')
            refseq += fastafile.fetch(chromosome, start, start + 1)
            pos.append(start)
            nseq.append(0)
            nalign.append(0)
            start += 1

        # Metrics for read depth
        allmean = np.mean(nseq)  # metrics, may not need all these
        qmean = np.mean(nalign)
        allmedian = np.median(nseq)
        qmedian = np.median(nalign)
        allsum = np.sum(nseq)
        qsum = np.sum(nalign)

        # GC content
        gcr = (refseq.count('G') + refseq.count('g') + refseq.count('C') + refseq.count('c')) / len(refseq)
        gapAlert = True if 'N' in refseq or 'n' in refseq else False

        gcmax = 0
        gcmaxlen = 0
        gcmin = 0
        gcminlen = 0
        for bs in samseq:
            minelgc = None
            lenminelgc = None
            maxelgc = None
            lenmaxelgc = None
            for el in bs:
                el = el.split('-')
                ellen = len(re.sub('[\+\-_Nn*]', '', el[0]))
                elgc = len(re.sub('[\+\-_Nn*AaTt]', '', el[0]))
                if minelgc == None or elgc < minelgc:
                    minelgc = elgc
                    lenminelgc = ellen
                if maxelgc == None or elgc > maxelgc:
                    maxelgc = elgc
                    lenmaxelgc = ellen
            gcmax += maxelgc
            gcmaxlen += lenmaxelgc
            gcmin += minelgc
            gcminlen += lenminelgc

        gcmax = gcmax / gcmaxlen if gcmaxlen > 0 else None
        gcmin = gcmin / gcminlen if gcminlen > 0 else None

        output = {'gcmax': gcmax,
                  'gcmin': gcmin,
                  'gcr': gcr,
                  'gapAlert': gapAlert,
                  'allmean': allmean,
                  'qmean': qmean,
                  'allmedian': allmedian,
                  'allsum': allsum,
                  'qsum': qsum,
                  'qmedian': qmedian,
                  'errorAlert': errorAlert,
                  'head': head,
                  'start': pos[0],
                  'end': pos[-1],
                  'minLen': gcminlen
                  }
        return output
    except MemoryError as e:
        raise
