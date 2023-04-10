import langdetect
from langdetect.lang_detect_exception import LangDetectException
import fitz

from isv_nlp_utils.constants import BASE_ISV_TOKEN_REGEX, iterate_over_text

"""
import fasttext

path_to_pretrained_model = '/tmp/lid.176.bin'
fmodel = fasttext.load_model(path_to_pretrained_model)
fmodel.predict([text2])  # ([['__label__en']], [array([0.9331119], dtype=float32)]
"""


# TODO: just crawl https://slovjani.info/indexes/index.html


class Czlanok:
    def __init__(self):
        self.title_ISV = ""
        self.title_EN = ""
        self.abstract_ISV = ""
        self.abstract_EN = ""
        self.text = None 
        self.authors = ""
        self.state = 0

    def process_span(self, span):
        current_text = span["text"].strip() + "\n"
        if span["size"] == 18:
            if self.text is None:
                self.title_ISV += current_text
            else:
                self.title_EN += current_text
        if "Italic" in span["font"]:
            if self.text is None:
                self.abstract_ISV += current_text
            if self.text and not self.title_EN:
                self.text += current_text
            else:
                self.abstract_EN += current_text
        else:
             if not self.text and not self.abstract_ISV:
                 self.authors += current_text
        if span["size"] == 12 and span["flags"] == 4:
            if self.text is None:
                self.text = ""
            self.text += current_text
        if "Italic" in span["font"] and "Bold" in span['font']:
            self.title_EN += current_text

    def __repr__(self):
        return f"{self.title_ISV}\n{self.authors}\n{self.abstract_ISV}\n\n({self.title_EN})\n({self.abstract_EN})"




if __name__ == "__main__":
    filename = r"C:\dev\ISV_data_gathering\slovjani_info\archive_2020-1.pdf"
    
    czlanky = []
    with fitz.open(filename) as doc:
        text = []
        tuty_czlanok = Czlanok()
        for page_number, page in enumerate(doc):
            local_text = page.getText()
            if len(local_text.strip()):
                if page_number > 2:
                    # raise NameError
                    pass
                print(local_text)
                print(langdetect.detect_langs(local_text))
                text += [page.getText()]
                # if "Pandemija" in local_text and "ključne slova" in local_text:
                data = page.getText("dict")['blocks']
                for entry in data:
                    if entry['bbox'][3] > 780:
                        # probably a header
                        continue
                    # print(entry['number'])
                    for line in entry.get('lines', []):
                        for span in line['spans']:
                            if span["size"] == 18 and tuty_czlanok.text:
                                print(tuty_czlanok)
                                czlanky.append(tuty_czlanok)
                                tuty_czlanok = Czlanok()
                                if len(czlanky) > 4:
                                    print(czlanky)
                                    raise NameError
                            else:
                                tuty_czlanok.process_span(span)

    
    #for page in text[1:]:
    #    for token in iterate_over_text(page):
    #        print(token)

