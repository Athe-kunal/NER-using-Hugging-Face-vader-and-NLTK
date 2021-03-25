import pandas as pd
from transformers import TFAutoModelForTokenClassification, AutoTokenizer
import tensorflow as tf

class NER:
    def __init__(self,text):
        self.text = text
        self.label_list = [
            "O",       # Outside of a named entity
            "B-MISC",  # Beginning of a miscellaneous entity right after another miscellaneous entity
            "I-MISC",  # Miscellaneous entity
            "B-PER",   # Beginning of a person's name right after another person's name
            "I-PER",   # Person's name
            "B-ORG",   # Beginning of an organisation right after another organisation
            "I-ORG",   # Organisation
            "B-LOC",   # Beginning of a location right after another location
            "I-LOC"    # Location
        ]

        self.model = TFAutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-cased",return_attention_mask=False)
        self.main_()
    def main_(self):
        tokens = self.tokenizer.tokenize(self.tokenizer.decode(self.tokenizer.encode(self.text)))
        inputs = self.tokenizer.encode(self.text,return_tensors="tf")

        outputs = self.model(inputs)[0] 
        predictions = tf.argmax(outputs,axis=2)
        preds = predictions[0].numpy()
        final_token = []
        for token,tag in zip(tokens,preds):
            if self.label_list[tag]=="I-ORG":
                final_token.append(token)
        return final_token

if __name__ == "__main__":
    NER("Facebook is Evil, I guess")
