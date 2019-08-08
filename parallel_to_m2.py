import argparse
import pickle
import sys
from contextlib import ExitStack
import scripts.align_text as align_text
import scripts.cat_rules as cat_rules
import scripts.toolbox as toolbox

from tagger.Utils import readDictionary
from tagger.RDRPOSTagger import RDRPOSTagger


def get_weights_from_edits(edits, cor_line):

    weights = ["1"] * len(cor_line.split())
    for edit in edits:
        cor_start, cor_end = edit[-2:]
        weights[cor_start:cor_end] = ["3"] * (cor_end - cor_start)

    assert len(weights) == len(cor_line.split()), "%s, %s" % (weights, cor_line.split())
    return " ".join(weights)


def main(args):

    tagger = RDRPOSTagger()
    tagger.constructSCRDRtreeFromRDRfile(rulesFilePath="{}/train.UniPOS.RDR".format(args.tagger))
    tagger_dict = readDictionary(inputFile="{}/train.UniPOS.DICT".format(args.tagger))

    out_m2 = open(args.out, "w")
    out_weights = None
    edits = None
    if args.weights is not None:
        out_weights = open(args.weights, "w")
    if args.edits is not None:
        edits = []

    print("Processing files...")
    with ExitStack() as stack:
        in_files = [stack.enter_context(open(i)) for i in [args.orig]+args.cor]
        for line_id, line in enumerate(zip(*in_files)):
            orig_sent = line[0].strip()
            cor_sents = line[1:]

            if not orig_sent:
                continue

            out_m2.write("S "+orig_sent+"\n")
            if edits is not None:
                edits.append([])

            proc_orig = tagger.tag_raw_sentence(DICT=tagger_dict, rawLine=orig_sent)
            for cor_id, cor_sent in enumerate(cor_sents):
                cor_sent = cor_sent.strip()

                if orig_sent == cor_sent:
                    out_m2.write("A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||"+str(cor_id)+"\n")
                    if out_weights is not None:
                        out_weights.write(" ".join(["1"] * len(cor_sent.split())) + "\n")

                else:
                    proc_cor = tagger.tag_raw_sentence(DICT=tagger_dict, rawLine=cor_sent)
                    auto_edits = align_text.get_auto_aligned_edits(proc_orig, proc_cor, args)

                    if out_weights is not None:
                        out_weights.write(get_weights_from_edits(edits=auto_edits, cor_line=cor_sent) + "\n")

                    for auto_edit in auto_edits:
                        cat = cat_rules.auto_type_edit(auto_edit, proc_orig, proc_cor)
                        auto_edit[2] = cat
                        out_m2.write(toolbox.formatEdit(auto_edit, cor_id)+"\n")
                        if edits is not None:
                            edits[line_id].append(((auto_edit[0], auto_edit[1]), (auto_edit[-2], auto_edit[-1])))

            out_m2.write("\n")
            if (line_id + 1) % 1000 == 0:
                sys.stdout.write("Processed %d lines\r" % (line_id + 1))
                sys.stdout.flush()

    if out_weights is not None:
        out_weights.close()
    if edits is not None:
        with open(args.edits, "wb") as edits_fp:
            pickle.dump(edits, edits_fp)


if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(description="Convert parallel original and corrected text files (1 sentence per line) into M2 format.\nThe default uses Damerau-Levenshtein and merging rules and assumes tokenized text.",
                                formatter_class=argparse.RawTextHelpFormatter,
                                usage="%(prog)s [-h] [options] -orig ORIG -cor COR [COR ...] -out OUT")
    parser.add_argument("-orig", help="The path to the original text file.", required=True)
    parser.add_argument("-cor", help="The paths to >= 1 corrected text files.", nargs="+", default=[], required=True)
    parser.add_argument("-out", help="The output filepath.", required=True)
    parser.add_argument("-lev", help="Use standard Levenshtein to align sentences.", action="store_true")
    parser.add_argument("-tagger", help="tagger_path.")
    parser.add_argument("-weights", help="target weights file.")
    parser.add_argument("-edits", help="edits file.")
    parser.add_argument("-merge", choices=["rules", "all-split", "all-merge", "all-equal"], default="rules",
                        help="Choose a merging strategy for automatic alignment.\n"
                            "rules: Use a rule-based merging strategy (default)\n"
                            "all-split: Merge nothing; e.g. MSSDI -> M, S, S, D, I\n"
                            "all-merge: Merge adjacent non-matches; e.g. MSSDI -> M, SSDI\n"
                            "all-equal: Merge adjacent same-type non-matches; e.g. MSSDI -> M, SS, D, I")
    args = parser.parse_args()
    # Run the program.
    main(args)
