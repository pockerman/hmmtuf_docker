import pysam
import numpy as np
import os
import shutil
import random
from pathlib import Path

#from hmmtuf import ENABLE_SPADE, SPADE_PATH
from compute_engine.src.constants import INFO, WARNING, ENABLE_SPADE, SPADE_PATH
from compute_engine.src.cengine_configuration import TREAT_ERRORS_AS_WARNINGS
from compute_engine.src.exceptions import Error
from compute_engine.src.tuf_core_helpers import write_from_weblogo
from compute_engine.src.tuf_core_helpers import gcpercent
from compute_engine.src.tuf_core_helpers import gquadcheck
from compute_engine.src.tuf_core_helpers import match
from compute_engine.src.tuf_core_helpers import create_bed
from compute_engine.src.tuf_core_helpers import remove_directories
from compute_engine.src.tuf_core_helpers import concatenate_bed_files


fas = None
outbedgraph = None
outtuf = None
outnor = None
outdel = None
outdup = None
outgap = None
outtdt = None
outquad = None
outrep = None
quadout = None
nucl_out = None
out_repeats_info = None

PATH = None
SPADE_OUTPATH = None


def spade(repseq, chrom, start, stop, region_type):

    """
    Call SPADE application in the SPADE_PATH
    """

    global outrep
    global nucl_out
    global  out_repeats_info

    global PATH
    global SPADE_OUTPATH

    if outrep is None:
        raise Exception("outrep file is None")

    if nucl_out is None:
        raise Exception("nucl_out file is None")

    if out_repeats_info is None:
        raise Exception("out_repeats_info is None")

    if PATH is None:
        raise Exception("PATH variable not specified")

    if SPADE_OUTPATH is None:
        raise Exception("SPADE_OUTPATH variable not specified")

    if not os.path.isdir(PATH + 'repeats'):
        try:
            os.mkdir(PATH + 'repeats')
        except OSError as e:

            if TREAT_ERRORS_AS_WARNINGS:
                print("%s Error: %s." % (WARNING, e.strerror))
            else:
                raise e

    fasta = open(PATH + 'repeats/tdtseq.fasta', 'w')

    folder = chrom + '_'+str(start) + '-' + str(stop) + '_' + region_type + '_' + gcpercent(repseq)
    working_dir = Path(SPADE_OUTPATH + folder)

    os.mkdir(working_dir)

    fasta.write('>'+folder+'\n')
    fasta.write(repseq+'\n')
    fasta.close()

    # system cmd to execute
    str_cmd = 'python3 {0} -in {1} -out_dir {2}'.format(SPADE_PATH + 'SPADE.py',
                                                        PATH + 'repeats/tdtseq.fasta',
                                                        SPADE_OUTPATH + folder + "/")
    print("{0} str_cmd {1}".format(INFO, str_cmd))
    os.system(str_cmd)

    # open the nucl files and attempt to write the
    # outrep file
    directories = os.listdir(path=working_dir)

    # collecte the nucleods files
    nucls_files = [name for name in directories if name.startswith('nucl_')]

    if len(nucls_files) == 0:
        # if we dont have a weblogo then we have
        # no repeats and then we want to document
        # that in the nucl_file
        nucl_out.write(chrom + '\t' + str(start) + '\t' + str(stop) +
                           '\t' + "NO_REPEATS" + '\t' + region_type + '\n')
    else:

        for name in nucls_files:

            # if this is a nucl_ directory
            #if name.startswith('nucl_'):

            # get the all the files in the path
            files = os.listdir(path=working_dir / name)

            if 'weblogo.txt' in files:

                    count_check = 12
                    # we do have a weblog file so extract nucleods
                    weblogo_dir = Path(working_dir / name)
                    write_from_weblogo(weblogo_dir=weblogo_dir, out_repeats=outrep,
                                       out_nucleods=nucl_out, start=start, stop=stop,
                                       out_repeats_info=out_repeats_info,
                                       region_type=region_type, chrom=chrom, count_check=12)


def do_TDT(tdtarray, outfile):

    global outtdt
    global outquad
    global fas

    if outquad is None:
        raise Exception("outquad file is None")

    if outtdt is None:
        raise Exception("outtdt file is None")

    if fas is None:
        raise Exception("fas file is None")

    for tdt in tdtarray:
        # check not a deletion beginning
        # do quad and repeat finding
        # print(tdt)
        seq = fas.fetch(tdt['chr'], tdt['start'], tdt['end'])
        if ENABLE_SPADE:
            spade(seq, tdt['chr'], tdt['start'], tdt['end'], region_type=tdt['type'])

        if tdt['type'] == 'Deletion' and len(seq) < 2000:
            outtdt.write(tdt['chr'] + '\t' +
                         str(tdt['start']) + '\t' +
                         str(tdt['end']) + '\n')

        gquad, mscore = gquadcheck(seq)

        if gquad:
            outquad.write(tdt['chr']+'\t'+str(tdt['start'])+'\t'+str(tdt['end'])+'\n')

        outfile.write(tdt['chr'] + ':' + str(tdt['start']) +
                      '-' + str(tdt['end']) + '_' + tdt['type'] +
                      '_' + gcpercent(seq) + '\t' + str(gquad) + str(mscore) + '\n')

def main(path: str, fas_file_name: str, chromosome: str,
         chr_idx: int, viterbi_file: str, nucleods_path: str,
         remove_dirs: bool=False, test_me: bool= False):

    print("{0} Start TUF-DEL-TUF".format(INFO))

    if not path.endswith("/"):
        path = path + "/"

    if not nucleods_path.endswith("/"):
        nucleods_path = nucleods_path + "/"

    global fas
    global outbedgraph
    global outtuf
    global outnor
    global outdel
    global outdup
    global outgap
    global outtdt
    global outquad
    global outrep
    global quadout
    global nucl_out
    global out_repeats_info

    global PATH
    global SPADE_OUTPATH

    print("{0} Path {1}".format(INFO, path))
    print("{0} FAS file {1}".format(INFO, fas_file_name))
    print("{0} Viterbi file {1}".format(INFO, viterbi_file))
    print("{0} Nucleods {1}".format(INFO, nucleods_path))

    #path = path + "/"
    NUCL_FILENAME = 'nucl_out.bed'
    OUT_REPEATS_INFO_FILENAME = "repeates_info_file.bed"
    PATH = path

    if ENABLE_SPADE:
        os.mkdir(PATH +  "repeats")
        os.mkdir(PATH + "spade_output")
        SPADE_OUTPATH = PATH + "spade_output/"

    # read global reference file
    fas = pysam.FastaFile(fas_file_name)

    # TODO: these should be set by the application
    conv = {'TUF': 10,
            'TUFDUP': 12,
            'Normal-I': 40,
            'Normal-II': 42,
            'Deletion': 30,
            'Duplication': 50,
            'GAP_STATE': 0}

    files_created = ["viterbi.bedgraph",
                     "tuf.bed",
                     "normal.bed",
                     "deletion.bed",
                     "duplication.bed",
                     "gap.bed",
                     "tdt.bed",
                     "quad.bed",
                     "rep.bed",
                     'gquads.txt',
                     NUCL_FILENAME,
                     OUT_REPEATS_INFO_FILENAME]

    # Open global files
    outbedgraph = open(path + "viterbi.bedgraph", "w")
    outtuf = open(path + "tuf.bed", "w")
    outnor = open(path + "normal.bed", "w")
    outdel = open(path + "deletion.bed", "w")
    outdup = open(path + "duplication.bed", "w")
    outgap = open(path + "gap.bed", "w")
    outtdt = open(path + "tdt.bed", "w")
    outquad = open(path + "quad.bed", "w")
    outrep = open(path + "rep.bed", "w")
    quadout = open(path + 'gquads.txt', 'w')
    nucl_out = open(path  + NUCL_FILENAME, 'w')
    out_repeats_info = open(path  + OUT_REPEATS_INFO_FILENAME, 'w')

    prevstate = ""
    start = 0
    end = 0
    chr = ''
    ptemp = True
    chrlistsorted = {chr_idx: viterbi_file}

    if not test_me:
        for i in sorted(chrlistsorted):

            flist = []
            viterbisorted = chrlistsorted

            for f in flist:
                # if 'tuf_delete_tuf' in f and '._' not in f:
                #     tdtsorted[int(f.split('_')[6])] = f
                if 'viterbi' in f and '._' not in f:
                    viterbisorted[int(f.split('_')[5])] = f

            tdtcheck = ''
            tdtlist = []

            for j in sorted(viterbisorted):
                print("{0} working with file: {1}".format(INFO, viterbisorted[j]))
                with open(viterbisorted[j]) as vfile:

                    ccheck = chrlistsorted[i].split('_')[2].rstrip()

                    for line in vfile:
                        vdata = create_bed(line, ccheck)

                        if len(vdata) == 0:
                            continue

                        outbedgraph.write(vdata['chr']+'\t' + str(int(float(vdata['loc'][0]))) +
                                          '\t'+str(int(float(vdata['loc'][1]))) + '\t'+str(conv[vdata['state']])+'\n')
                        curstate = vdata['state']

                        if curstate == 'TUFDUP':
                            curstate = 'TUF'
                        elif curstate == 'Normal-II':
                            curstate = 'Normal-I'
                        if prevstate == "":
                            prevstate = curstate
                            chr = vdata['chr']
                            start = int(float(vdata['loc'][0]))
                            end = int(float(vdata['loc'][1]))

                        if curstate == prevstate and chr == vdata['chr'] and (int(float(vdata['loc'][0])) == end+1 or ptemp):
                            end = int(float(vdata['loc'][1]))

                        if curstate != prevstate or chr != vdata['chr'] or (int(float(vdata['loc'][0])) != end+1 and not ptemp):

                            if prevstate == 'TUF':
                                tdtcheck = tdtcheck + 'T'
                                tdtlist.append({"chr": chr, "start": start, "end": end, "type": 'TUF'})
                                print(chr+'\t'+str(start)+'\t'+str(end)+'TUF')
                                outtuf.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')

                            if prevstate == 'Normal-I':
                                if 'TDT' in tdtcheck:
                                    print("{0} Processing TDT file".format(INFO))
                                    do_TDT(tdtlist, outfile=quadout)
                                    print("{0} Done Processing TDT file".format(INFO))

                                tdtcheck = ''
                                tdtlist = []
                                print("{0} {1}".format(INFO, chr+'\t'+str(start)+'\t'+str(end)+'Normal'))
                                outnor.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')

                                if (end - start) > 1000:
                                    p = random.randint(1, 10)
                                    print("{0} normal >1000, rand: {1}".format(INFO, p))
                                    if p in [1, 3, 5, 7, 9]:
                                        print("{0} processing random normal region".format(INFO))
                                        n = random.randint(start, end - 1000)
                                        nseq = fas.fetch(chr, n, n + 1000)
                                        # print("calculating random normal G Quad")
                                        gquad, mscore = gquadcheck(nseq)
                                        quadout.write(chr + ':' + str(n) + '-'+str(n + 1000) + '_' +
                                                      'Normal' + '_'+gcpercent(nseq) + '\t' +
                                                      str(gquad)+str(mscore)+'\n')

                                        if ENABLE_SPADE:
                                            spade(nseq, chr, n, n + 1000, 'Normal')
                                else:
                                    print("{0} normal section too short Only processing if section > 1000...".format(INFO))

                            if prevstate == 'Deletion':
                                if len(tdtcheck) > 0 and tdtcheck[0] == 'T':
                                    tdtcheck = tdtcheck+'D'
                                    tdtlist.append({"chr": chr, "start": start, "end": end, "type": 'Deletion'})

                                print("{0} {1}".format(INFO, chr+'\t'+str(start)+'\t'+str(end)+'Deletion'))
                                outdel.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')

                            if prevstate == 'Duplication':
                                if 'TDT' in tdtcheck:
                                    #print("{0} Processing TDT file".format(INFO))
                                    do_TDT(tdtlist, outfile=quadout)
                                    #print("{0} Done Processing TDT file".format(INFO))
                                tdtcheck = ''
                                tdtlist = []
                                print(chr+'\t'+str(start)+'\t'+str(end)+'Duplication')
                                outdup.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')

                            if prevstate == 'GAP_STATE':
                                if 'TDT' in tdtcheck:
                                    #print("{0} Processing TDT file".format(INFO))
                                    do_TDT(tdtlist, outfile=quadout)
                                    #print("{0} Done Processing TDT file".format(INFO))

                                tdtcheck = ''
                                tdtlist = []
                                print(chr+'\t'+str(start)+'\t'+str(end)+'GAP')
                                outgap.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')
                            chr = vdata['chr']
                            start = int(float(vdata['loc'][0]))
                            end = int(float(vdata['loc'][1]))
                            prevstate = curstate

    quadout.close()
    outbedgraph.close()
    outtuf.close()
    outnor.close()
    outdel.close()
    outdup.close()
    outgap.close()
    outtdt.close()
    outquad.close()
    outrep.close()
    nucl_out.close()
    out_repeats_info.close()
    print("{0} Closing files...".format(INFO))

    if remove_dirs:
        print("{0} Removing directories".format(INFO))
        remove_directories(chromosome=chromosome, spade_output=SPADE_OUTPATH)

    if path + NUCL_FILENAME != nucleods_path + NUCL_FILENAME:
        print("{0} Copying  {1} to {2}".format(INFO, path + NUCL_FILENAME, nucleods_path + NUCL_FILENAME))

        # copy the nucleods file produced
        shutil.copyfile(path + NUCL_FILENAME, nucleods_path + NUCL_FILENAME)

    if path + OUT_REPEATS_INFO_FILENAME != nucleods_path + OUT_REPEATS_INFO_FILENAME:
        print("{0} Copying {1} to {2}".format(INFO, path + OUT_REPEATS_INFO_FILENAME,
                                              nucleods_path + OUT_REPEATS_INFO_FILENAME))

        # copy the nucleods file produced
        shutil.copyfile(path + OUT_REPEATS_INFO_FILENAME, nucleods_path + OUT_REPEATS_INFO_FILENAME)

    print("{0} END TUF-DEL-TUF".format(INFO))
    return files_created




            


