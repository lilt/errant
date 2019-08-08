import re


def initialize_sentence(freq_dict, sentence):
    words = sentence.strip().split()
    tagged_sentence = []
    for word in words:
        if word in ["“", "”", "\""]:
            tagged_sentence.append(("''/", freq_dict["''"]))
            continue

        decoded_word = word
        lower_word = decoded_word.lower().encode("utf-8")
        if word in freq_dict:
            tag = freq_dict[word]
        elif lower_word in freq_dict:
            tag = freq_dict[lower_word]
        else:
            if re.search(r"[0-9]+", word) is not None:
                tag = freq_dict["TAG4UNKN-NUM"]
            else:
                suffix_l2 = suffix_l3 = suffix_l4 = suffix_l5 = None
                decoded_word_length = len(decoded_word)
                if decoded_word_length >= 4:
                    suffix_l3 = ".*" + decoded_word[-3:]
                    suffix_l2 = ".*" + decoded_word[-2:]
                if decoded_word_length >= 5:
                    suffix_l4 = ".*" + decoded_word[-4:]
                if decoded_word_length >= 6:
                    suffix_l5 = ".*" + decoded_word[-5:]

                if suffix_l5 in freq_dict:
                    tag = freq_dict[suffix_l5]
                elif suffix_l4 in freq_dict:
                    tag = freq_dict[suffix_l4]
                elif suffix_l3 in freq_dict:
                    tag = freq_dict[suffix_l3]
                elif suffix_l2 in freq_dict:
                    tag = freq_dict[suffix_l2]
                elif decoded_word[0].isupper():
                    tag = freq_dict["TAG4UNKN-CAPITAL"]
                else:
                    tag = freq_dict["TAG4UNKN-WORD"]

        tagged_sentence.append((word, tag))

    return tagged_sentence
