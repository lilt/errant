from tagger.InitialTagger import initialize_sentence
from tagger.SCRDRLearnerObject import FWObject
from tagger.SCRDRTree import SCRDRTree


class RDRPOSTagger(SCRDRTree):
    """
    RDRPOSTagger for a particular language
    """
    def __init__(self):
        super().__init__(None)
        self.root = None

    def tag_raw_sentence(self, DICT, rawLine):
        word_tags = initialize_sentence(DICT, rawLine)
        sen = []
        for i, word_tag in enumerate(word_tags):
            fw_object = FWObject.get_FWObject(word_tags, i)
            word, tag = word_tag
            node = self.findFiredNode(fw_object)
            if node.depth > 0:
                sen.append((word, node.conclusion))
            else:  # Fired at root, return initialized tag
                sen.append((word, tag))
        return sen
