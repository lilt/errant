
class FWObject:
    """
    RDRPOSTaggerV1.1: new implementation scheme
    RDRPOSTaggerV1.2: add suffixes
    """

    def __init__(self, check = False):
        self.context = [None, None, None, None, None, None, None, None, None, None, None, None, None]
        if(check == True):
            i = 0
            while (i < 10):
                self.context[i] = "<W>"
                self.context[i + 1] = "<T>"
                i = i + 2
            self.context[10] = "<SFX>"# suffix
            self.context[11] = "<SFX>"
            self.context[12] = "<SFX>"
        self.notNoneIds = []

    @staticmethod
    def get_FWObject(start_word_tags, index):
        fw_object = FWObject(True)
        word, tag = start_word_tags[index]
        fw_object.context[4] = word
        fw_object.context[5] = tag

        decoded_word = word
        if len(decoded_word) >= 4:
            fw_object.context[10] = decoded_word[-2:]
            fw_object.context[11] = decoded_word[-3:]
        if len(decoded_word) >= 5:
            fw_object.context[12] = decoded_word[-4:]

        if index > 0:
            preWord1, preTag1 = start_word_tags[index - 1]
            fw_object.context[2] = preWord1
            fw_object.context[3] = preTag1

        if index > 1:
            preWord2, preTag2 = start_word_tags[index - 2]
            fw_object.context[0] = preWord2
            fw_object.context[1] = preTag2

        if index < len(start_word_tags) - 1:
            nextWord1, nextTag1 = start_word_tags[index + 1]
            fw_object.context[6] = nextWord1
            fw_object.context[7] = nextTag1

        if index < len(start_word_tags) - 2:
            nextWord2, nextTag2 = start_word_tags[index + 2]
            fw_object.context[8] = nextWord2
            fw_object.context[9] = nextTag2

        return fw_object
