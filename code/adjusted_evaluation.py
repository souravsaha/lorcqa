import json
from scipy.special import perm
import math
import yaml
from common import get_question_and_gold_answer, get_result_path, get_dr_qa_result_path
"""
    Hit@5 results: 
    Takes 2 argument one is input question path and another is 
    answer file found from the model

"""
from decimal import Decimal

def p_at_1(gold_answer, model_answers):
    gold_answer_list = []
    model_answer_1 = []
    score = 0

    for answer in gold_answer:
        gold_answer_list += answer.split("|")
    gold_answer_list = [x.strip() for x in gold_answer_list] 

    # fixed bug : if model answer doesn't retrieve any answer at all
    if len(model_answers) !=0 :
        model_answer_1 = [x.strip() for x in model_answers[0].split("|")] 
    #print(model_answer_i)
    if not set(model_answer_1).isdisjoint(gold_answer_list):
        score = 1
    
    if score == 1 :
        # number of correct by total number of retrieved
        total_retrieved_1 = len(model_answer_1) 
        correct_list_1 = [ans for ans in model_answer_1 if ans in gold_answer_list]
        correct_retrieved_1 = len(correct_list_1)

        score = score * (correct_retrieved_1 / total_retrieved_1)
    
    return score


def mrr_value(gold_answer, model_answers):
    gold_answer_list = []
    model_answer_i = []
    score = 0
    ans_found = False
    sum_ans_prev = 0 # \N_{i-1}
    sum_ans_curr = 0 # \N_{i}
    expected_value = 0

    for answer in gold_answer:
        gold_answer_list += answer.split("|")
    gold_answer_list = [x.strip() for x in gold_answer_list] 

    for i in range(1, 6):
        if len(model_answers) >=i :
            model_answer_i = [x.strip() for x in model_answers[i-1].split("|")] 
        #print(model_answer_i)
        sum_ans_prev = sum_ans_curr
        sum_ans_curr += len(model_answer_i)

        if not set(model_answer_i).isdisjoint(gold_answer_list):
            permute_value = 0
            ans_found = True
            correct_list_i = ([ans for ans in model_answer_i if ans in gold_answer_list])

            count_i = len(model_answer_i)   # n_{i}
            correct_count_i = len(correct_list_i)     # k
            wrong_count_i = count_i - correct_count_i   # n_{i} - k
            #expected_value = 0
            
            for j in range(1, wrong_count_i + 2):
                permute_value = Decimal(perm(wrong_count_i, j - 1))
                
                expected_value += (j * permute_value * correct_count_i * Decimal(math.factorial(count_i - j))) / (Decimal(math.factorial(count_i)))


            #score = (score + 1)/i
            break           # once matches with break from the loop
    
    if ans_found == True :
        score = 1 /(sum_ans_prev + expected_value)

    return score


def hit_at_5(gold_answer, model_answers):
    gold_answer_list = []
    model_answer_list = []
    score = 0
    model_answer_i = []
    sum_ans_prev = 0    # \N_{i-1}
    sum_ans_curr = 0    # \N_i

    for answer in gold_answer:
        gold_answer_list += answer.split("|")
    gold_answer_list = [x.strip() for x in gold_answer_list] 
    
    for i in range(1, 6):
        if len(model_answers) >= i :
            model_answer_i = [x.strip() for x in model_answers[i-1].split("|")]

        # if current answer found and sum_ans_cur(\N_i) < 5 return score = 1
        sum_ans_curr += len(model_answer_i)
        if not set(model_answer_i).isdisjoint(gold_answer_list) and sum_ans_curr < 5:
            score = 1 
            return score
        # if \N_i >= 5
        if sum_ans_curr >= 5 :
            permute_value = 0
            correct_list_i = ([ans for ans in model_answer_i if ans in gold_answer_list])
            
            count_i = len(model_answer_i)
            correct_count_i = len(correct_list_i)     # k
            wrong_count_i = count_i - correct_count_i   # n_{i} - k 
                
            # commenting this as scipy will take care of this

            if wrong_count_i < 5 - sum_ans_prev:
                pemute_value = 0 
            else:
                permute_value = Decimal(perm(wrong_count_i, 5 - sum_ans_prev))
                #permute_value = Decimal(math.factorial(wrong_count_i))/ Decimal(math.factorial(wrong_count_i-5 + sum_ans_prev))
                
            print("n_i", count_i)
            print("N_i", sum_ans_curr)
            print("k", correct_count_i)
            print("N_{i-1}", sum_ans_prev)
            score = 1 - ((permute_value) * Decimal(math.factorial(sum_ans_curr - 5)))/(Decimal(math.factorial(count_i)))
            return score

        sum_ans_prev = sum_ans_curr

    #for model_answer in model_answers:
    #    model_answer_list += model_answer.split("|")
    #model_answer_list = [x.strip() for x in model_answer_list] 

    #print("Gold Answer list: ", gold_answer_list)
    #print("Model Gives output: ", model_answer_list)

    #if not set(model_answer_list).isdisjoint(gold_answer_list):
    #    score = 1
    return score

# find the model output for the particular


def get_model_output(ques_exact_id, quesType, resultPathStart, samplingType):

    result_path = get_result_path(quesType, resultPathStart, samplingType)
    #result_path = get_dr_qa_result_path(quesType, resultPathStart, samplingType)
    # TODO hack for model output file
    #result_path = resultPathStart + "CQ_"+ quesType + "/"+ samplingType + "/sent-embeddings-score_v3_finetuned_type_" + quesType + ".json" 
    #result_path = resultPathStart + "CQ_"+ quesType + "/"+ samplingType + "/sent-embeddings-score_v3_finetuned_type_lg_spacy_" + quesType + ".json" 
    #result_path = resultPathStart + "CQ_"+ quesType + "/"+ samplingType + "/max_score_mul_doc_freq_flair_" + quesType + ".json" 
    #result_path = resultPathStart + "CQ_"+ quesType + "/"+ samplingType + "/max_score_plus_doc_freq_flair_" + quesType + ".json" 
    #result_path = resultPathStart + "CQ_"+ quesType + "/"+ samplingType + "/" + samplingType + "_" + quesType + ".json" 
    #result_path = resultPathStart + "CQ_"+ quesType + "/"+ samplingType + "/" + samplingType + "_part_" + quesType + ".json" 
    #result_path = resultPathStart + "CQ_"+ quesType + "/"+ samplingType + "/" + samplingType + "_re_rank_2_" + quesType + ".json" 
    #result_path = resultPathStart + "CQ_"+ quesType + "/"+ samplingType + "/" + samplingType + "_re_rank_2_part_" + quesType + ".json" 
    with open(result_path) as result_file:
        result_file_content = json.load(result_file)
        #result_file_value = json.loads(result_file_content)
        result_key = ques_exact_id
        #print(result_path)

        if result_key in result_file_content:
            return result_key, list(result_file_content[result_key]), 1

        return result_key, [], 0

config_file_name = 'configure.yml'

# defined it here too
with open(config_file_name) as config_file:
    config_file_values = yaml.load(config_file)

qid = config_file_values["qid"]
quesType = config_file_values["quesType"]
quesPathStart = config_file_values["quesPathStart"]
resultPathStart = config_file_values["resultPathStart"]
samplingType = config_file_values["samplingType"]

"""
# AVG score for Hit @5
for i in range(150):

    question, answer, ques_exact_id = get_question_and_gold_answer(
        int(qid) + i, quesType, quesPathStart)
    result_key, result_content, success = get_model_output(
        ques_exact_id, quesType, resultPathStart, samplingType)

    print("Ques_exact_id : ", ques_exact_id)
    print("Question is: ", question)
    #print("Gold Answer: ", answer)
    #print("Model Answer : ", result_content)
    if success:
        score = hit_at_5(answer, result_content)
        total_score += score
    else:
        print("Answer not found for the question:")
        score = 0
    print("Hit @5 score : ", score)
    print("\n \n")

print("Total Score", total_score)
print("Avg Hit @5 score : ", total_score/150)
"""
"""
# avg score for mrr
for i in range(150):
    question, answer, ques_exact_id = get_question_and_gold_answer(
        int(qid) +i, quesType, quesPathStart)
    result_key, result_content, success = get_model_output(
        ques_exact_id, quesType, resultPathStart, samplingType)

    print("Ques_exact_id : ", ques_exact_id)
    print("Question is: ", question)
    print("Gold Answer: ", answer)
    print("Model Answer : ", result_content)
    if success:
        score = mrr_value(answer, result_content)
        total_score += score
    else:
        print("Answer not found for the question:")
        score = 0
    print("MRR score : ", score)
    print("\n \n")

print("Total Score", total_score)
print("Avg mrr score : ", total_score/150)
"""
"""
# avg score for p@1
for i in range(150):
    question, answer, ques_exact_id = get_question_and_gold_answer(
        int(qid) +i, quesType, quesPathStart)
    result_key, result_content, success = get_model_output(
        ques_exact_id, quesType, resultPathStart, samplingType)

    print("Ques_exact_id : ", ques_exact_id)
    print("Question is: ", question)
    print("Gold Answer: ", answer)
    print("Model Answer : ", result_content)
    if success:
        score = p_at_1(answer, result_content)
        total_score += score
    else:
        print("Answer not found for the question:")
        score = 0
    print("P@1 score : ", score)
    print("\n \n")

print("Total Score", total_score)
print("Avg p@1 score : ", total_score/150)
"""
def compute_score(evaluation_type):
    evaluation_measure =""
    total_score = 0
    score = 0

    if evaluation_type == "t":
        evaluation_measure = "Hit@5"
        
    if evaluation_type == "m":
        evaluation_measure = "MRR"
        
    if evaluation_type == "p":
        evaluation_measure = "P@1"

    outputfile = open(args.filepath, "w+")

    for i in range(150):
        question, answer, ques_exact_id = get_question_and_gold_answer(
            int(qid) +i, quesType, quesPathStart)
        result_key, result_content, success = get_model_output(
            ques_exact_id, quesType, resultPathStart, samplingType)

        # lower case of result list
        result_content = [x.lower() for x in result_content ]

        print("Ques_exact_id : ", ques_exact_id)
        print("Question is: ", question)
        print("Gold Answer: ", answer)
        print("Model Answer : ", result_content)
        if success:
            #score = p_at_1(answer, result_content)
            if evaluation_type == "t":
                score = hit_at_5(answer, result_content)

            elif evaluation_type == "m":
                score = mrr_value(answer, result_content)

            elif evaluation_type == "p":
                score = p_at_1(answer, result_content)
            
            total_score += score
        else:
            print("Answer not found for the question:")
            score = 0
        #outputfile.write(evaluation_measure + "\t" + ques_exact_id + "\t" + str(score) + "\n")
        outputfile.write(evaluation_measure + "\t" + str(int(qid) +i) + "\t" + str(score) + "\n")
        print("{} score : {}".format(evaluation_measure,score))
        print("\n \n")

    print("Total Score", total_score)
    print("Avg {} score : {}".format(evaluation_measure,total_score/150))
    outputfile.close()

import argparse
import sys
parser = argparse.ArgumentParser()

# Adding argument
parser.add_argument("-t", "--top", help = "Hit @ 5 measure", action='store_true') 
parser.add_argument("-m", "--mrr", help = "MRR measure", action='store_true') 
parser.add_argument("-p", "--precision", help = "p@1 measure", action='store_true') 
parser.add_argument("-f", "--filepath", help="store outputfile")

# Read arguments from command line

args = parser.parse_args()

if not len(sys.argv) > 1: 
    parser.print_help()
    exit(1)

if args.top:
    avg_score = compute_score("t")
if args.mrr:
    avg_score = compute_score("m")
if args.precision:
    avg_score = compute_score("p")

#filepath = args.filepath
if None == args.filepath : 
    args.filepath = "foo"

#print(args.filepath)

