labels = [
    "Mistranslation",
    "Addition",
    "MT Hallucination",
    "Omission",
    "Untranslated",
    "Wrong Name Entity & Term",
    "Grammar",
    "Punctuation",
    "Spelling",
    "Register",
    "Inconsistent Style",
    "Non-translation",
    "Unnatural Flow"
]

types = {
    "Mistranslation": "direct_semantic_error",
    "Addition": "indirect_semantic_error",
    "MT Hallucination": "indirect_semantic_error",
    "Omission": "direct_semantic_error",
    "Untranslated": "technical_error",
    "Wrong Name Entity & Term": "direct_semantic_error",
    "Grammar": "technical_error",
    "Punctuation": "technical_error",
    "Spelling": "technical_error",
    "Register": "style_and_register_error",
    "Inconsistent Style": "style_and_register_error",
    "Non-translation": "style_and_register_error",
    "Unnatural Flow": "style_and_register_error"
}

error_types = [
    "direct_semantic_error",
    "indirect_semantic_error",
    "technical_error",
    "style_and_register_error"
]

error_types_indexes = {
    "direct_semantic_error": 0,
    "indirect_semantic_error": 1,
    "technical_error": 2,
    "style_and_register_error": 3,
}

accuracy_labels = {
    "Mistranslation",
    "Addition",
    "MT Hallucination",
    "Omission",
    "Untranslated",
    "Wrong Name Entity & Term",
}
fluency_labels = {
    "Grammar",
    "Punctuation",
    "Spelling",
    "Register",
    "Inconsistent Style",
    "Unnatural Flow",
}
other_labels = {"Non-translation",}

labels_indexes = {label:idx for idx, label in enumerate(labels)}

class LabelSpecification(object):
    def __init__(self, label):
        if label.rfind("(") == -1:
            self.label = label.strip()
            self.label_severity = ""
            self.label_type = types[self.label]
        else:
            self.label = label[: label.rfind("(")].strip()
            if self.label == "Untraslated" or self.label == 'Untrasnalted':
                self.label = "Untranslated"
            if self.label == 'Grammer':
                self.label = 'Grammar'
            self.label_severity = label[label.rfind("(") + 1: label.rfind(")")].strip()

            # print(label.rfind(")"))
            try:
                self.label_type = types[self.label].strip()
            except:
                breakpoint()
        self.source = ""
        self.hyp = ""
        self.label_text = ""
        self.label_span = ()
        self.label_weight = 0.0

    def get_label(self):
        return self.label

    def get_label_severity(self):
        if self.label_severity != "Major":
            return "Minor"
        return "Major"

    def get_label_type(self):
        return self.label_type

    def compare_label(self, another_label):
        return self.label == another_label.get_label()

    def compare_label_severity(self, another_label):
        return self.label_severity == another_label.get_label_severity()

    def compare_label_type(self, another_label):
        return self.label_type == another_label.get_label_type()
    
    def get_label_category(self):
        if self.label in accuracy_labels:
            return 'accuracy'
        elif self.label in fluency_labels:
            return 'fluency'
        else:
            assert self.label in other_labels
            return 'other'

    def __str__(self):
        return self.label + "(" + self.label_severity + ") " + self.label_type

    def __repr__(self):
        return str(self)

    @staticmethod
    def get_error_type_index(error):
        return error_types_indexes[types[error.get_label()]]

    def get_label_type_index(error):
        return labels_indexes[error.get_label()]

    @staticmethod
    def get_all_labels():
        return labels

    @staticmethod
    def get_all_error_types():
        return error_types

    @staticmethod
    def get_error_types_indexes():
        return error_types_indexes

    def get_label_weight(self):
        if "Major" in self.label_severity:
            return 3
        else:
            return 1



def main():
    label = LabelSpecification("Unnatural Flow")
    print(label.get_label(), '\n',
          label.get_label_severity(), '\n',
          label.get_label_type(), '\n')


if __name__ == "__main__":
    main()
