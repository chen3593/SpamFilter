import os
import re

def load_label():
    label_path = "test_data/label"
    label_table = dict()
    count_spam = 0
    count_ham = 0
    with open(label_path) as label_fp:
        for line in label_fp:
            if "Id" in line:
                continue
            line_list = line.split(",")
            label_table[int(line_list[0])] = int(line_list[1])
            if int(line_list[1]) == 0:
                count_spam += 1
            else:
                count_ham += 1
    return label_table, count_ham, count_spam
            
def count_token_in_training(label_table):
    ham_token_times = dict()
    spam_token_times = dict()
    training_set_path = "test_data/training_set"
    files = os.listdir(training_set_path)
    
    for file_count in range(1, 2001):
        already_modified_token = set()
        email_path = training_set_path + "/TRAIN_"+ str(file_count) + ".eml"
        #email_path = os.path.join(training_set_path, f)
        fp = open(email_path)
        token_list = re.split('[^a-zA-Z0-9_$-]+', fp.read())
        for token in token_list:
            if '<' in token or '>' in token or token.isdigit():
                continue

            if label_table[file_count] == 0:
                if token in spam_token_times and not token in already_modified_token:
                    already_modified_token.add(token)
                    spam_token_times[token] += 1
                else:
                    already_modified_token.add(token)
                    spam_token_times[token] = 1
            
            if label_table[file_count] == 1:
                if token in ham_token_times and not token in already_modified_token:
                    already_modified_token.add(token) 
                    ham_token_times[token] += 1
                else:
                    already_modified_token.add(token)
                    ham_token_times[token] = 1

        file_count += 1
    #print spam_token_times
    #print ham_token_times
    #print spam_token_times

    return spam_token_times, ham_token_times
            
def generateSpamicityTable():
    label_table, count_ham, count_spam = load_label()
    spam_token_times, ham_token_times= count_token_in_training(label_table)
    token_set = set()
    spamicity_table = dict()

    for i in ham_token_times:
        token_set.add(i)
    for i in spam_token_times:
        token_set.add(i)
    
    for token in token_set:
        ham_occurrence = ham_token_times.get(token, 0) * 2
        spam_occurrence = spam_token_times.get(token, 0)
        if spam_occurrence + ham_occurrence >= 5:
            bad_rate = float(spam_occurrence) / float(count_spam)
            good_rate = float(ham_occurrence) / float(count_ham)
            spamicity = bad_rate / (bad_rate + good_rate)
            if spamicity == 1:
                spamicity = 0.99
            if spamicity == 0:
                spamicity = 0.01
            spamicity_table[token] = spamicity
    
    return spamicity_table, label_table

def calculate_rate(body, spamicity_table):
    spamicity_list = []
    token_list = re.split('[^a-zA-Z0-9_$-]+', body)
    for token in token_list:
        if token in spamicity_table:
            spamicity = spamicity_table.get(token, 0.4)
            spamicity_list.append((token, spamicity))

    sorted_spamicity_list = sorted(spamicity_list, key=lambda spamicity_distance : abs(spamicity_distance[1] - 0.5), reverse=True)
    #print sorted_spamicity_list

    combined_spamicity = 1
    combined_hamicity = 1
    for i in range(min(15, len(sorted_spamicity_list))):
        combined_spamicity *= sorted_spamicity_list[i][1]
        combined_hamicity *= (1 - sorted_spamicity_list[i][1])
    
    prob_spam = combined_spamicity / (combined_spamicity + combined_hamicity)

    
    return prob_spam

def run():
    spamcity_table, label_table = generateSpamicityTable()
    training_set_path = "test_data/test_set"
    result_list = []
    for file_count in range(2001, 2501):
        email_path = training_set_path + "/TRAIN_"+ str(file_count) + ".eml"
        fp = open(email_path)
        result_list.append(calculate_rate(fp.read(), spamcity_table))
    
    file_num = 2001
    right_count = 0
    wrong_count = 0
    false_positive = 0
    false_negative = 0
    for result in result_list:
        spam = 0 if result > 0.9 else 1
        real = label_table.get(file_num)
        if spam == label_table.get(file_num):
            right_count += 1
        else:
            wrong_count += 1
            if spam == 0 and real == 1:
                false_positive += 1
            else:
                false_negative += 1
        file_num += 1
    print right_count
    print wrong_count
    print "Rate of success :" +  str(float(right_count) / float(right_count + wrong_count))
    print "Rate of false_positve :" +  str(float(false_positive) / float(right_count + wrong_count))

run()
#generateSpamicityTable()
