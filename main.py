import sys
import os
import re
import time

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
            
def add_times_to_token_table(table, token):
    if token in table:
        table[token] += 1
    else:
        table[token] = 1
def count_token_in_training(label_table, training_set_size):
    ham_token_times = dict()
    spam_token_times = dict()
    training_set_path = "test_data/training_set"
    files = os.listdir(training_set_path)
    
    
    for file_count in range(1, 1+training_set_size):
        already_modified_token = set()
        email_path = training_set_path + "/TRAIN_"+ str(file_count) + ".eml"
        fp = open(email_path)
        token_list = re.split('[^a-zA-Z0-9_$-]+', fp.read())
        for token in token_list:
            if token.isdigit() or '<' in token or '>' in token:
                continue

            if label_table[file_count] == 0:
                if not token in already_modified_token:
                    add_times_to_token_table(spam_token_times, token)
                    already_modified_token.add(token)
                #if token in spam_token_times and not token in already_modified_token:
                #    addTokenToTable
                #    already_modified_token.add(token)
                #    spam_token_times[token] += 1
                #else:
                #    already_modified_token.add(token)
                #    spam_token_times[token] = 1
            
            if label_table[file_count] == 1:
                if not token in already_modified_token:
                    add_times_to_token_table(ham_token_times, token)
                    already_modified_token.add(token)
                #if token in ham_token_times and not token in already_modified_token:
                #    already_modified_token.add(token) 
                #    ham_token_times[token] += 1
                #else:
                #    already_modified_token.add(token)
                #    ham_token_times[token] = 1

        file_count += 1
    #print spam_token_times
    #print ham_token_times
    #print spam_token_times

    return spam_token_times, ham_token_times
            
def generateSpamicityTable(training_set_size):
    label_table, count_ham, count_spam = load_label()
    spam_token_times, ham_token_times= count_token_in_training(label_table, training_set_size)
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
    
    return spamicity_table, label_table, count_ham, count_spam

def calculate_rate(body, spamicity_table, num_interesting_count):
    spamicity_list = set()
    token_list = re.split('[^a-zA-Z0-9_$-]+', body)
    for token in token_list:
        if token.isdigit() or '<' in token or '>' in token:
            continue
        else:
            spamicity = spamicity_table.get(token, 0.4)
        spamicity_list.add((token, spamicity))

    sorted_spamicity_list = sorted(spamicity_list, key=lambda spamicity_distance : abs(spamicity_distance[1] - 0.5), reverse=True)
    #print sorted_spamicity_list

    combined_spamicity = 1
    combined_hamicity = 1
    for i in range(min(num_interesting_count, len(sorted_spamicity_list))):
    #for i in range(len(sorted_spamicity_list)):
        combined_spamicity *= sorted_spamicity_list[i][1]
        combined_hamicity *= (1 - sorted_spamicity_list[i][1])
    #try:
        #if combined_spamicity == 0:
        #    return 0.01
        prob_spam = combined_spamicity / (combined_spamicity + combined_hamicity)
    #except ZeroDivisionError:
    #    print sorted_spamicity_list
    #    raise 
    return prob_spam

def run(num_interesting_count, training_set_size, threshold):
    spamcity_table, label_table, count_ham, count_spam = generateSpamicityTable(training_set_size)
    training_set_path = "test_data/test_set"
    result_list = []
    for file_count in range(2001, 2501):
        email_path = training_set_path + "/TRAIN_"+ str(file_count) + ".eml"
        fp = open(email_path)
        result_list.append(calculate_rate(fp.read(), spamcity_table, num_interesting_count))

    file_num = 2001
    right_count = 0
    wrong_count = 0
    false_positive = 0
    false_positive_list = []
    false_negative = 0
    false_negative_list = []

    for result in result_list:
        spam = 0 if result > threshold else 1
        real = label_table.get(file_num)
        if spam == label_table.get(file_num):
            right_count += 1
        else:
            wrong_count += 1
            if spam == 0 and real == 1:
                false_positive_list.append(file_num)
                false_positive += 1
            else:
                false_negative_list.append(file_num)
                false_negative += 1
        file_num += 1

    #print "Right Filtering:" + str(right_count)
    #print "Wrong Filtering:" + str(wrong_count)
    #print "Rate of success :" +  str(float(right_count) / float(right_count + wrong_count))
    #print "Rate of false_positive :" +  str(float(false_positive) / float(right_count + wrong_count))
    #print "false positive list:"
    #print false_positive_list
    #print "false_negative List :" 
    #print false_negative_list
    score = (50 * float(false_positive) + float(false_negative)) / (count_ham * 50 + count_spam) 
    #print "Training Set Size:" + str(training_set_size)
    #print "Num interesting count:" + str(num_interesting_count) + " Score is " + str(score)
    print "threshold:", threshold
    print "score:", score
    
args = sys.argv

#t0 = time.time()
#for i in range(10):
run(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]))
#t1 = time.time()
#result = t1 - t0
#print "Total time:", t1 - t0, "sec"
#print "Average time:", result / 10, "sec"
