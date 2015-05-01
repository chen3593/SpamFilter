import os

def count_occurence():
    training_set_path = "training_set"
    lable_path = "label"
    files = os.listdir(training_set_path)
    for f in files:
        email_filename = os.path.join(training_set_path, f)
        fp = open(email_filename)
        body = fp.read()
        for i in body:
            token_list = extract_token
def generateSpamicityTable:
    good_token_occurence, bad_token_occurence = count_occurence()







def get_num_ham_spam():
    label_path = 
