#!/usr/bin/python

# This script is only supposed to be run on the jenkins master or locally so use
# of Python is okay.

from __future__ import print_function

import argparse
import sys
import re

COMMENT_OUT = re.compile(r"([^#]*).*")

def get_args():
    ap = argparse.ArgumentParser(description="Tool to generate a Groovy expression specifying the " +
                                 "labels to run a jenkins job on")
    # this weird combination means that both '-e' and '-e 1' work
    ap.add_argument("-e", "--run-on-exotics", nargs="?", default=False, const=True,
                    help="Run on exotic labels if RUN_ON_EXOTICS is not specified " +
                    "or it is not one of '0', 'no'.")
    ap.add_argument("labels_file")
    ap.add_argument("exotics_file")

    return ap.parse_args()

def non_empty_lines(file_obj):
    for line in file_obj:
        match = COMMENT_OUT.match(line.strip())
        assert match is not None
        content = match.groups()[0]
        if content:
            yield content

def main(labels_f_path, exotics_f_path, run_on_exotics):
    labels_to_run = set()
    with open(labels_f_path, "r") as f:
        for label in non_empty_lines(f):
            labels_to_run.add(label.strip())
    if not run_on_exotics:
        with open(exotics_f_path, "r") as f:
            for label in non_empty_lines(f):
                labels_to_run.discard(label.strip())

    print("(", end="")
    labels_eqs = ('label == "%s"' % label for label in sorted(labels_to_run))
    print(" || \\\n ".join(labels_eqs) + ")")

    return 0

if __name__ == "__main__":
    args = get_args()
    ret = main(args.labels_file, args.exotics_file,
               args.run_on_exotics not in (False, '0', 0, "no"))
    sys.exit(ret)
