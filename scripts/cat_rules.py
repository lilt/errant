def auto_type_edit(edit, orig_sent, cor_sent):
    # Get the tokens in the edit.
    orig_toks = orig_sent[edit[0]:edit[1]]
    cor_toks = cor_sent[edit[4]:edit[5]]
    # Nothing to nothing is a detected, but not corrected edit.
    if not orig_toks and not cor_toks:
        return "UNK"
    # Missing
    elif not orig_toks and cor_toks:
        op = "M:"
        cat = "OTHER"
    # Unnecessary
    elif orig_toks and not cor_toks:
        op = "U:"
        cat = "OTHER"
    # Replacement and special cases
    else:
        # Same to same is a detected, but not corrected edit.
        if orig_toks[0] == cor_toks[0]:
            return "UNK"
        # Special: Orthographic errors at the end of multi-token edits are ignored.
        # E.g. [Doctor -> The doctor], [The doctor -> Dcotor], [, since -> . Since]
        # Classify the edit as if the last token weren't there.
        elif orig_toks[-1][0].lower() == cor_toks[-1][0].lower() and \
                (len(orig_toks) > 1 or len(cor_toks) > 1):
            min_edit = edit[:]
            min_edit[1] -= 1
            min_edit[5] -= 1
            return auto_type_edit(min_edit, orig_sent, cor_sent)
        # Replacement
        else:
            op = "R:"
            cat = "OTHER"
    return op + cat
