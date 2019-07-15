import argparse
import os
import spacy
import sys
from contextlib import ExitStack
import scripts.align_text as align_text
import scripts.cat_rules as cat_rules
import scripts.toolbox as toolbox


def get_weights_from_edits(edits, cor_line):

    weights = ["1"] * len(cor_line.split())
    for edit in edits:
        cor_start, cor_end = edit[-2:]
        weights[cor_start:cor_end] = ["3"] * (cor_end - cor_start)

    assert len(weights) == len(cor_line.split()), "%s, %s" % (weights, cor_line.split())
    return " ".join(weights)


def main(args):

    print("Loading Spacy resources")
    nlp = spacy.load(args.lang)
    # Setup output m2 file
    out_m2 = open(args.out, "w")
    out_weights = None
    if args.weights is not None:
        out_weights = open(args.weights, "w")

    # ExitStack lets us process an arbitrary number of files line by line simultaneously.
    # See https://stackoverflow.com/questions/24108769/how-to-read-and-process-multiple-files-simultaneously-in-python
    print("Processing files...")
    with ExitStack() as stack:
        in_files = [stack.enter_context(open(i)) for i in [args.orig]+args.cor]
        # Process each line of all input files.
        for line_id, line in enumerate(zip(*in_files)):
            orig_sent = line[0].strip()
            cor_sents = line[1:]
            # If orig sent is empty, skip the line
            if not orig_sent: continue
            # Write the original sentence to the output m2 file.
            out_m2.write("S "+orig_sent+"\n")
            # Markup the original sentence with spacy (assume tokenized)
            proc_orig = toolbox.applySpacy(orig_sent.split(), nlp)
            # Loop through the corrected sentences
            for cor_id, cor_sent in enumerate(cor_sents):
                cor_sent = cor_sent.strip()
                # Identical sentences have no edits, so just write noop.
                if orig_sent == cor_sent:
                    out_m2.write("A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||"+str(cor_id)+"\n")
                    if out_weights is not None:
                        out_weights.write(" ".join(["1"] * len(cor_sent.split())) + "\n")
                # Otherwise, do extra processing.
                else:
                    # Markup the corrected sentence with spacy (assume tokenized)
                    proc_cor = toolbox.applySpacy(cor_sent.strip().split(), nlp)
                    # Auto align the parallel sentences and extract the edits.
                    auto_edits = align_text.getAutoAlignedEdits(proc_orig, proc_cor, args)
                    if out_weights is not None:
                        out_weights.write(get_weights_from_edits(edits=auto_edits, cor_line=cor_sent) + "\n")
                    # Loop through the edits.
                    for auto_edit in auto_edits:
                        # Give each edit an automatic error type.
                        cat = cat_rules.auto_type_edit(auto_edit, proc_orig, proc_cor)
                        auto_edit[2] = cat
                        # Write the edit to the output m2 file.
                        out_m2.write(toolbox.formatEdit(auto_edit, cor_id)+"\n")
            # Write a newline when we have processed all corrections for a given sentence.
            out_m2.write("\n")
            if (line_id + 1) % 1000 == 0:
                sys.stdout.write("Processed %d lines\r" % (line_id + 1))
                sys.stdout.flush()


if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(description="Convert parallel original and corrected text files (1 sentence per line) into M2 format.\nThe default uses Damerau-Levenshtein and merging rules and assumes tokenized text.",
                                formatter_class=argparse.RawTextHelpFormatter,
                                usage="%(prog)s [-h] [options] -orig ORIG -cor COR [COR ...] -out OUT")
    parser.add_argument("-orig", help="The path to the original text file.", required=True)
    parser.add_argument("-cor", help="The paths to >= 1 corrected text files.", nargs="+", default=[], required=True)
    parser.add_argument("-out", help="The output filepath.", required=True)
    parser.add_argument("-lev", help="Use standard Levenshtein to align sentences.", action="store_true")
    parser.add_argument("-lang", help="language for corpus.")
    parser.add_argument("-weights", help="target weights file.")
    parser.add_argument("-merge", choices=["rules", "all-split", "all-merge", "all-equal"], default="rules",
                        help="Choose a merging strategy for automatic alignment.\n"
                            "rules: Use a rule-based merging strategy (default)\n"
                            "all-split: Merge nothing; e.g. MSSDI -> M, S, S, D, I\n"
                            "all-merge: Merge adjacent non-matches; e.g. MSSDI -> M, SSDI\n"
                            "all-equal: Merge adjacent same-type non-matches; e.g. MSSDI -> M, SS, D, I")
    args = parser.parse_args()
    # Run the program.
    main(args)
