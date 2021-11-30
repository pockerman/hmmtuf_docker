import json
import os
from pathlib import Path
import csv
import sqlite3
from sqlite3 import Error
import pysam

from compute_engine.src.file_readers import TufFileReader
from compute_engine.src.file_readers import DeletionFileReader
from compute_engine.src.file_readers import DuplicationFileReader
from compute_engine.src.file_readers import NormalFileReader
from compute_engine.src.tuf_core_helpers import gcpercent





def main(input_path_dir: Path, fas_file_name: Path, db_conn) -> None:

    # table in the db
    sql = "CREATE TABLE IF NOT EXISTS extra_gc (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
          "chromosome TEXT NOT NULL, start_idx INT NOT NULL, end_idx INT NOT NULL, " \
          "sequence TEXT NOT NULL, state_name TEXT NOT NULL, gc FLOAT, gc_min FLOAT, gc_max FLOAT)"

    cursor = db_conn.cursor()
    cursor.execute(sql)
    db_conn.commit()

    fas = pysam.FastaFile(fas_file_name)

    # get th directories in the path
    directories = os.listdir(input_path_dir)

    repeats_statistics = {}
    total = 0

    data_dict = {"DUPLICATION": None, "TUF": None,
                 "NORMAL": None, "DELETION": None}
    for directory in directories:

        # only work if pattern is 'chr**'
        if 'chr' in directory and len(directory) <= 5:

            # this is a directory of interest
            directory += '/' + directory
            directory_path =  input_path_dir / directory

            # get the files
            deletion_name = 'deletion.bed'
            duplication_name = 'duplication.bed'
            tuf_name = 'tuf.bed'
            normal_name = 'normal.bed'

            deletion_reader = DeletionFileReader(mode='strip', delimiter='\t')
            deletion_data = deletion_reader(filename=directory_path / deletion_name)
            total += len(deletion_data)

            data_dict["DELETION"] = deletion_data

            nomral_reader = NormalFileReader(mode='strip', delimiter='\t')
            normal_data = nomral_reader(filename=directory_path / normal_name)
            total += len(normal_data)

            data_dict["NORMAL"] = normal_data

            tuf_reader = TufFileReader(mode='strip', delimiter='\t')
            tuf_data = tuf_reader(filename=directory_path / tuf_name)
            total += len(tuf_data)

            data_dict["TUF"] = tuf_data

            dupl_reader = DuplicationFileReader(mode='strip', delimiter='\t')
            dupl_data = dupl_reader(filename=directory_path / duplication_name)
            total += len(dupl_data)

            data_dict["DUPLICATION"] = dupl_data


            for name in data_dict:

                _data = data_dict[name]

                for data in _data:
                    chromosome = data[0]
                    start_idx = int(data[1])
                    end_idx = int(data[2])

                    seq = fas.fetch(chromosome, start_idx, end_idx)
                    gc_str = gcpercent(cseq=seq, chunk_size=100)

                    gc_data = gc_str.split('_')
                    gc = float(gc_data[0])
                    min_gc = float(gc_data[1]) if gc_data[1] != 'NA' else gc
                    max_gc = float(gc_data[2]) if gc_data[2] != 'NA' else gc

                    sql = '''INSERT INTO extra_gc(chromosome, start_idx, end_idx, sequence, state_name, gc, gc_min, gc_max) values(?,?,?,?,?,?,?,?)'''
                    values = (chromosome, start_idx, end_idx, seq, name, gc, min_gc, max_gc )

                    cursor.execute(sql, values)
                    db_conn.commit()

    print("Total data ", total)


if __name__ == '__main__':

    INPUT_PATH_DIR = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths')
    OUTPUT_PATH_DIR = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths/tmp/out')
    DB_PATH = '/home/alex/qi3/hmmtuf/release_db_v5.sqlite3'
    fas_file_name = Path('/home/alex/qi3/hmmtuf/data/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna')
    conn = sqlite3.connect(DB_PATH)
    main(input_path_dir=INPUT_PATH_DIR, fas_file_name=fas_file_name, db_conn=conn)
    conn.close()
