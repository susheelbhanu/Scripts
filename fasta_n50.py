#!/usr/bin/env python
"""Calculate N50 from an assembled genome fasta file

Usage:
    python fasta_n50.py genome_file [min_length]
"""

# Importing modules
from signal import signal, SIGPIPE, SIG_DFL
from collections import defaultdict
import gzip
import sys

# Defining classes
class Fasta(object):
    """Fasta object with name and sequence
    """
    def __init__(self, name, sequence):
        self.name = name
        self.sequence = sequence
    def write_to_file(self, handle):
        handle.write(">" + self.name + "\n")
        handle.write(self.sequence + "\n")

# Defining functions
def myopen(_file, mode="rt"):
    if _file.endswith(".gz"):
        return gzip.open(_file, mode=mode)

    else:
        return open(_file, mode=mode)

def fasta_iterator(input_file):
    """Takes a fasta file input_file and returns a fasta iterator
    """
    with myopen(input_file) as f:
        sequence = ""
        name = ""
        begun = False
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if begun:
                    yield Fasta(name, sequence)
                name = line.replace(">", "")
                sequence = ""
                begun = True
            else:
                sequence += line

        if name != "":
            yield Fasta(name, sequence)

if __name__ == '__main__':
    # Prevent broken pipe error
    signal(SIGPIPE, SIG_DFL)

    # Parse user input
    try:
        input_file = sys.argv[1]
    except:
        print(__doc__)
        sys.exit(1)

    try:
        min_length = int(sys.argv[2])
    except:
        min_length = 1

    print("Including contigs/scaffolds with at least " + str(min_length) + " bp")

    # Cound kmers
    sequence_lengths = []

    for seq in fasta_iterator(input_file):
        length = len(seq.sequence)
        if length >= min_length:
            sequence_lengths.append(len(seq.sequence))

    sequence_lengths = sorted(sequence_lengths, reverse=True)
    total_length = sum(sequence_lengths)
    half_length = float(total_length) / 2.0

    print("Genome size: " + str(total_length))

    cumulative_length = 0
    for seq_len in sequence_lengths:
        cumulative_length += seq_len
        if cumulative_length >= half_length:
            print("N50: " + str(seq_len))
            break

