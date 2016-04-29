__author__ = 'roshani'

import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import string
from nltk.stem.lancaster import LancasterStemmer
import sys
import re

max_score = 0
name_list = []
location_list = []
month_list = []
time_list = []
occupation_list = []
location_prepo_list = []
preposition_list = []
numberInWords_list = []

stopwordSet = stopwords.words('english')
stopwordSet1 = set(['the','of','and','to','a','in','that','is','was','he','for','it','with','as','his','on','be','at','by','I'])
morePunctuations = set(['``','"','...',"''","n't","'re","'s","--"])
punctuationSet = set(string.punctuation) | morePunctuations
lancaster_stemmer = LancasterStemmer()


def parse_story(story_filename):
     story_dict = {}
     with open(story_filename) as myfile:
         parts = myfile.read().split("TEXT:")

         headline = parts[0].splitlines()[0]
         date = parts[0].splitlines()[1]
         storyid = parts[0].splitlines()[2]
         text = sent_tokenize(parts[1].lstrip("\n").replace("\n"," "))
         story_dict[(headline,date,storyid)] = text
     return story_dict


def removeStopWordsAndTagPOS(story_dict):
    storyWithoutStopWords_dict = {}
    storyPOS_dict = {}
    for key in story_dict:
        text = story_dict[key]
        for line in text:
            lineWithoutStopWord = removeStopWords(line)
            storyWithoutStopWords_dict[line] = lineWithoutStopWord
            storyPOS_dict[line] = nltk.pos_tag(lineWithoutStopWord)
    return storyWithoutStopWords_dict, storyPOS_dict

def camel(s):
    return (s != s.lower() and s != s.upper())

def contains_noun(questionWithoutStopWord):
    status = False
    proper_noun = ""
    for word in questionWithoutStopWord:
        if (camel(word)):
            proper_noun = proper_noun +" "+ word

    proper_noun_list = proper_noun.split()
    for each_proper_noun in proper_noun_list:
        if any(each_proper_noun in s for s in name_list):
            status = True
            return status
    return status

def contains_proper_noun(questionWithoutStopWord):
    status = False
    proper_noun = ""
    for word in questionWithoutStopWord:
        if (camel(word)):
            status = True
    return True


def semantic_classes(name_filename):
    with open(name_filename+"names.txt") as f:
        name_list.append(f.read().splitlines())

    with open(name_filename+"location.txt") as f:
        location_list.append(f.read().splitlines())

    with open(name_filename+"month.txt") as f:
        month_list.append(f.read().lower().splitlines())

    with open(name_filename+"time.txt") as f:
        time_list.append(f.read().lower().splitlines())

    with open(name_filename+"occupation.txt") as f:
        occupation_list.append(f.read().lower().splitlines())

    with open(name_filename+"location_prepo.txt") as f:
        location_prepo_list.append(f.read().lower().splitlines())

    with open(name_filename+"preposition.txt") as f:
        preposition_list.append(f.read().lower().splitlines())

    with open(name_filename+"numberInWords.txt") as f:
        numberInWords_list.append(f.read().lower().splitlines())

def contains_name_word(sentWithoutStopWords):
    status = False
    for word in sentWithoutStopWords:
        if (word == "name"):
            status = True
            return status
    return status

def contains_name_occupation(sentWithoutStopWord):
    proper_noun = ""
    status = False
    for word in sentWithoutStopWord:
        if (camel(word)):
            proper_noun = proper_noun +" "+ word

    proper_noun_list = proper_noun.split()

    for each_proper_noun in proper_noun_list:
        if any(each_proper_noun in s for s in name_list):
            status = True
            return status

    for word in sentWithoutStopWord:
        if any(word in s for s in occupation_list):
            status = True
            return status
    return False


def contains_month(question):
    wordsInAQuestion = wordTokenize(question)
    status = False
    for word in wordsInAQuestion:
        if word.lower() in month_list[0]:
            status = True
    return status

def contains_relativetime(sent):
    wordsInASentence = wordTokenize(sent)
    status = False
    for word in wordsInASentence:
        if ((word.lower() == "today") | (word.lower() == "yesterday")| (word.lower() == "tomorrow") | (word.lower() == "last night")):
            status = True
    return status

def contains_head(wordsAfterOfInAQues,wordsInASentence):
    status = False
    wordsInASentenceLowercase = []
    for word in wordsInASentence:
        wordsInASentenceLowercase.append(word.lower())

    for word in wordsAfterOfInAQues:
        if word in wordsInASentenceLowercase:
            status = True
    return status


def who(questionWithoutStopWords, sentWithoutStopWords, storyPOS_dict, scoreOfASentence):
    score = 0
    status = False
    score = score+ scoreOfASentence
    if(not contains_noun(questionWithoutStopWords) and contains_noun(sentWithoutStopWords)):
        score = score + 6
    if (not contains_noun(questionWithoutStopWords) and contains_name_word(sentWithoutStopWords)):
        score = score + 4
    status = contains_name_occupation(sentWithoutStopWords)
    if (status):
        score = score + 4
    return score


def contains_time_list(sent, time_list):
    wordsInASent = word_tokenize(sent)
    sentWithoutPunct = []
    for word in wordsInASent:
        if word.lower() not in punctuationSet:
            sentWithoutPunct.append(word)

    for word in sentWithoutPunct:
        if word in time_list[0]:
            status = True
        else:
            status = False
    return status

def contains_time_other(sent, check_list):
    wordsInASent = word_tokenize(sent)
    sentWithoutPunct = []
    for word in wordsInASent:
        if word.lower() not in punctuationSet:
            sentWithoutPunct.append(word)

    for word in sentWithoutPunct:
        if word in check_list:
            status = True
            return status
        else:
            status = False
    return status


def when_rule(question, sent, scoreOfASentence):
    score = 0
    score = score + scoreOfASentence
    if(contains_time_list(sent, time_list)):
        score = score + 4

    if(contains_time_other(question, ["last"]) and contains_time_other(sent,["first","last","since","ago"])):
        score = score + 20
    if(contains_time_other(question, ["start","begin"]) and contains_time_other(sent, ["start","begin","since","year"])):
        score = score + 20

    return score


def what_rule(question,sent, scoreOfASentence):
    wordsInAQuestion = wordTokenize(question)
    wordsInASentence = wordTokenize(sent)
    scoreOfWhatRule = 0

    wordsAfterOfInAQues = []

    #RULE 1
    scoreOfWhatRule = scoreOfWhatRule + scoreOfASentence

    #RULE 2
    if (contains_month(question) and contains_relativetime(sent)):
        scoreOfWhatRule = scoreOfWhatRule + 3

    #RULE 3
    for ques_word in wordsInAQuestion:
        if ques_word == "kind":
            for sent_word in wordsInASentence:
                if ((sent_word == "call" ) or (sent_word == "from")):
                    scoreOfWhatRule = scoreOfWhatRule + 4

    #RULE 4
    for ques_word in wordsInAQuestion:
        if ques_word == "name":
            for sent_word in wordsInASentence:
                if ((sent_word == "name") or (sent_word == "call" ) or (sent_word == "known")):
                    scoreOfWhatRule = scoreOfWhatRule + 20

    for ques_word_index in range(len(wordsInAQuestion)):
        if wordsInAQuestion[ques_word_index] == "of":
            of_index = ques_word_index
            for remaining_word_index in range(of_index+1,len(wordsInAQuestion)):
                wordsAfterOfInAQues.append(wordsInAQuestion[remaining_word_index].lower())

    #RULE 5
    for ques_word_index in range(len(wordsInAQuestion)):
        if wordsInAQuestion[ques_word_index] == "name":
            name_index = ques_word_index
            if wordsInAQuestion[name_index+1].lower() in preposition_list[0]:
                sentWithoutStopwords = removeStopWords(sent)
                if contains_proper_noun(sentWithoutStopwords):
                    if ((contains_proper_noun(sentWithoutStopwords)) and (contains_head(wordsAfterOfInAQues,wordsInASentence))):
                        scoreOfWhatRule = scoreOfWhatRule + 20

    return scoreOfWhatRule

def why_rule(sent,BESTlines,text_list, index):
    wordsInASent = wordTokenize(sent.lower())
    scoreOfWhyRule = 0

    if sent.lower() in BESTlines:
        scoreOfWhyRule = scoreOfWhyRule + 3

    if sent.lower() not in BESTlines:
        if (index + 1) < len(text_list):
            if text_list[index+1] in BESTlines:
                scoreOfWhyRule = scoreOfWhyRule + 3

        if text_list[index - 1] in BESTlines:
            scoreOfWhyRule = scoreOfWhyRule + 4

    for word in wordsInASent:
        if word.lower() == "want":
            scoreOfWhyRule = scoreOfWhyRule + 4
        if ((word.lower() == "so") or (word.lower() == "because")) :
            scoreOfWhyRule = scoreOfWhyRule + 4

    return scoreOfWhyRule

def get_bestlines(question,text_list,storyPOS_dict):
    scoreOfALine = {}
    BESTlines = []

    for line in text_list:
        scoreOfALine[line] = wordMatch(question,line,storyPOS_dict)

    maxindex = max(scoreOfALine, key = scoreOfALine.get)
    maxScore = scoreOfALine[maxindex]
    twothirdMaxScore = 2/3.0*(maxScore)

    for line in scoreOfALine:
        if scoreOfALine[line] >= twothirdMaxScore:
            BESTlines.append(line.lower())

    return BESTlines


def contains_location_prep(sent, location_prepo_list):
    wordsInASent = word_tokenize(sent)
    sentWithoutPunct = []
    for word in wordsInASent:
        if word.lower() not in punctuationSet:
            sentWithoutPunct.append(word)

    for word in sentWithoutPunct:
        if word in location_prepo_list[0]:
            status = True
        else:
            status = False
    return status

def contains_location_list(sent, location_list):
    wordsInASent = word_tokenize(sent)
    sentWithoutPunct = []
    for word in wordsInASent:
        if word.lower() not in punctuationSet:
            sentWithoutPunct.append(word)

    for word in sentWithoutPunct:
        if word in location_list[0]:
            status = True
        else:
            status = False
    return status

def where_rule(question, sent, scoreOfASentence):
    score = 0
    score = score + scoreOfASentence
    if(contains_location_prep(question, sent)):
        score = score + 4
    if(contains_location_list(question, sent)):
        score = score + 6

    return score

def contains_word(question,check):
    wordsInASent = word_tokenize(question)
    questionWithoutPunct = []
    for word in wordsInASent:
        if word.lower() not in punctuationSet:
            questionWithoutPunct.append(word)

    if check in questionWithoutPunct:
        status = True
    else:
        status = False
    return status


def dateline(question):

    score = 0
    if (contains_word(question,"happen")):
        score =score + 4
    if (contains_word(question,"take") and contains_word(question,"place")):
        score =score + 4
    if (contains_word(question,"this")):
        score =score + 20
    if (contains_word(question,"story")):
        score =score + 20
    return score

def how_rule(sent,question,storyPOS_dict):

    scoreOfHowRule = 0
    wordsInASentence = wordTokenize(sent.lower())
    wordsInAQuestion = wordTokenize(question.lower())

    #RULE 1
    scoreOfWordMatch = wordMatch(question,sent,storyPOS_dict)
    scoreOfHowRule = scoreOfHowRule + scoreOfWordMatch + 10

    #RULE 2
    if "cost" in wordsInAQuestion or "much" in wordsInAQuestion or "many" in wordsInAQuestion or "long" in wordsInAQuestion:

        if (("dollar" in wordsInASentence) or ("cost" in wordsInASentence) or (re.match(r'\d+',sent) != None) or ("weigh" in wordsInASentence)  ):
            scoreOfHowRule = scoreOfHowRule + 12
        for word in wordsInASentence:
            if word in numberInWords_list:
                scoreOfHowRule = scoreOfHowRule + 6

    #RULE 3
    if "age" in wordsInAQuestion or "old" in wordsInAQuestion:
        if (re.search(r'\d+',sent) != None):
            scoreOfHowRule = scoreOfHowRule + 20
        for word in wordsInASentence:
            if word in numberInWords_list:
                scoreOfHowRule = scoreOfHowRule + 20

    return scoreOfHowRule



def data_forward(questions_data,story_dict):
    storyWithoutStopWords_dict,storyPOS_dict = removeStopWordsAndTagPOS(story_dict)
    quest_words = set(['what','when','why','who','where','whose','which', 'how'])
    for question in questions_data:
        for story_key in story_dict:
            text_list = story_dict[story_key]
            questionWithoutStopWords = removeStopWords(question[1])
            BESTlines = get_bestlines(question[1],text_list,storyPOS_dict)

            for q in question[1].split():
                if q.lower() in quest_words:
                    if q.lower() == 'who' or q.lower() == 'whose' :
                        max_score_who = 0
                        answer = ""
                        for sent in text_list:
                            scoreOfASentence = wordMatch(question[1],sent,storyPOS_dict)
                            sentWithoutStopWords = removeStopWords(sent)
                            who_score = who(questionWithoutStopWords,sentWithoutStopWords, storyPOS_dict, scoreOfASentence)

                            if (max_score_who < who_score):
                                max_score_who = who_score
                                answer = sent
                        ans= ""

                        str1_list = word_tokenize(answer)
                        str2_list = word_tokenize(question[1].lower())
                        for word in str1_list:
                            if word.lower() not in str2_list and word.lower() not in punctuationSet and not word.islower():
                               ans = ans+" "+word
                        if ans == "":
                            for word in str1_list:
                                if word.lower() not in str2_list and word.lower() not in punctuationSet :
                                   ans = ans+" "+word

                        if 'being' in question[0] and 'being' in ans:
                            ans = ans.split('being')[1]


                        print "QuestionID:",question[0]
                        print "Answer:", ans


                        break;
                    if (q.lower() == 'when'):
                        max_score_when = 0
                        date = ""
                        count = 0
                        for sent in text_list:
                            scoreOfASentence = wordMatch(question[1],sent,storyPOS_dict)
                            when_score = when_rule(question[1],sent, scoreOfASentence)
                            dateline_score = dateline(question[1])
                           # dateline_score = 0
                            first_sent = text_list[0]
                            if (max_score_when < when_score):
                                max_score_when = when_score
                                answer = sent

                            if (when_score == max_score_when):
                                count = count+1

                            if count == len(text_list):
                                answer = first_sent
                            if  max_score_when == 0:
                                max_score_when = dateline_score
                                date = story_key[1].split(":")[1].lstrip()
                                answer = sent
                        date = ""
                        if date == "":
                            ans= ""
                            str1_list = word_tokenize(answer)
                            str2_list = word_tokenize(question[1].lower())
                            for word in str1_list:
                                if word.lower() not in str2_list and word.lower() not in punctuationSet:
                                   ans = ans+" "+word

                            if 'being' in question[0] and 'being' in ans:
                                ans = ans.split('being')[1]

                            print "QuestionID:",question[0]
                            if (re.search(r'\d+',ans) != None):
                                print "Answer:", re.sub('[^\d.]' , ' ', ans)
                            else:
                                print "Answer:", ans
                        else:
                            ans= ""
                            str1_list = word_tokenize(answer)
                            str2_list = word_tokenize(question[1].lower())
                            for word in str1_list:
                                if word.lower() not in str2_list and word.lower() not in punctuationSet:
                                   ans = ans+" "+word
                            print "QuestionID:",question[0]
                            print "Answer:", date
                        break;
                    if(q.lower() == 'where'):
                        max_score_where = 0
                        date = ""
                        count =1
                        for sent in text_list:
                            scoreOfASentence = wordMatch(question[1],sent,storyPOS_dict)
                            where_score = where_rule(question[1], sent, scoreOfASentence)
                            dateline_score = dateline(question[1])
                            first_sent = text_list[0]

                            if (max_score_where < where_score):
                                max_score_where = where_score
                                answer = sent

                            if (where_score == max_score_where):
                                count = count+1

                            if count == len(text_list):
                                answer = first_sent

                            if max_score_where == 0:
                                max_score_where = dateline_score
                                date = story_key[1].split(":")[1].lstrip()
                                answer = sent
                            date = ""

                        if date == "":
                            ans= ""
                            str1_list = word_tokenize(answer)
                            str2_list = word_tokenize(question[1].lower())
                            for word in str1_list:
                                if word.lower() not in str2_list and word.lower() not in punctuationSet and not word.islower():
                                   ans = ans+" "+word

                            if 'being' in question[0] and 'being' in ans:
                                ans = ans.split('being')[1]

                            if ('where' in question[0]) and 'from ' in ans:
                                ans = ans[ans.index('from '):]

                            print "QuestionID:",question[0]
                            print "Answer:", ans
                        else:
                            ans= ""
                            str1_list = word_tokenize(answer)
                            str2_list = word_tokenize(question[1].lower())
                            for word in str1_list:
                                if word.lower() not in str2_list and word.lower() not in punctuationSet:
                                   ans = ans+" "+word
                            print "QuestionID:",question[0]
                            print "Answer:", date
                        break;



                    if(q.lower() == 'what' or q.lower() == 'which'):
                        max_score_what = 0
                        answer = ""
                        for sent in text_list:
                            scoreOfASentence = wordMatch(question[1],sent,storyPOS_dict)
                            scoreOfWhatRule = what_rule(question[1], sent, scoreOfASentence)

                            if (scoreOfWhatRule == max_score_what):
                                answer = answer + " | "+sent

                            if (max_score_what < scoreOfWhatRule):
                                max_score_what = scoreOfWhatRule
                                answer = sent

                        ans= ""
                        if "|" in answer:
                            str1_list = word_tokenize(answer.split("|")[1])
                        else:
                            str1_list = word_tokenize(answer)
                        str2_list = word_tokenize(question[1].lower())
                        for word in str1_list:
                            if word.lower() not in str2_list and word.lower() not in punctuationSet:
                               ans = ans+" "+word

                        if 'being' in question[0] and 'being' in ans:
                            ans = ans.split('being')[1]

                        print "QuestionID:",question[0]
                        print "Answer:", ans
                        break;

                    if(q.lower() == 'why'):
                        index = -1
                        max_score_why = 0
                        answer = ""
                        for sent in text_list:
                            index = index + 1
                            scoreOfWhyRule = why_rule(sent,BESTlines,text_list, index)

                            if (scoreOfWhyRule == max_score_why):
                                answer = answer + " | "+sent

                            if (max_score_why < scoreOfWhyRule):
                                max_score_why = scoreOfWhyRule
                                answer = sent

                        ans= ""
                        str1_list = word_tokenize(answer)
                        str2_list = word_tokenize(question[1].lower())

                        if( "|" in answer ):
                            ans = answer.split("|")[-1]
                        else:
                            ans = answer

                        if 'being' in question[0] and 'being' in ans:
                            ans = ans.split('being')[1]
                        if 'because' in ans:
                            ans = ans[ans.index('because '):]

                        elif 'for ' in ans:
                            ans = ans[ans.index('for '):]

                        elif 'to ' in ans:
                            ans = ans[ans.index('to '):]

                        print "QuestionID:",question[0]
                        print "Answer:", ans
                        break;

                    if(q.lower() == 'how'):
                        max_score_how = 0
                        for sent in text_list:
                            scoreOfHowRule = how_rule(sent,question[1],storyPOS_dict)
                      #      print(scoreOfHowRule , sent )
                            if (scoreOfHowRule == max_score_how):
                                answer = answer + " | "+sent

                            if (scoreOfHowRule > max_score_how):
                                max_score_how = scoreOfHowRule
                                answer = sent

                        ans= ""

                        if ("|" in answer):
                            str1_list = word_tokenize(answer.split("|")[1])
                        else:
                            str1_list = word_tokenize(answer)
                        str2_list = word_tokenize(question[1].lower())

                        print "QuestionID:",question[0]
                        tagAnswer = nltk.pos_tag(str1_list)
                        if "how many" in question[1].lower() or "how much" in question[1].lower():
                            for i in range(0, len(tagAnswer)):
                                if 'CD' in tagAnswer[i][1]:
                                    ans = ans + " " + tagAnswer[i][0]
                                else:
                                    ans = answer
                        else:
                            for word in str1_list:
                                if word.lower() not in str2_list and word.lower() not in punctuationSet:
                                   ans = ans+" "+word

                        if 'being' in question[0] and 'being' in ans:
                            ans = ans.split('being')[1]

                        if 'how' in question[0] and 'by ' in ans:
                            ans = ans[ans.index('by '):]

                        if ('how' in question[0]) and 'from ' in ans:
                            ans = ans[ans.index('from '):]
                        print "Answer:", ans
                        break;


        if not any(word in question[1].lower().split() for word in quest_words):
                max_score_else = 0
                for sent in text_list:
                    current_score = wordMatch(question[1],sent,storyPOS_dict)

                    if (current_score == max_score_else):
                            answer = answer + " | "+sent

                    if current_score > max_score_else:
                        max_score_else = current_score
                        answer = sent

                ans= ""
                if ("|" in answer):
                    str1_list = word_tokenize(answer.split("|")[1])
                else:
                    str1_list = word_tokenize(answer)
                str2_list = word_tokenize(question[1].lower())
                for word in str1_list:
                    if word.lower() not in str2_list and word.lower() not in punctuationSet:
                        ans = ans+" "+word

                if 'being' in question[0] and 'being' in ans:
                    ans = ans.split('being')[1]

                print "QuestionID:",question[0]
                print "Answer:", ans
        print("\n")




def wordMatch(question, line, storyPOS_dict):
    wordsInAQuestion = word_tokenize(question)
    rootsInAQuestion = set()
    for word in wordsInAQuestion:
        root = lancaster_stemmer.stem(word)
        rootsInAQuestion.add(root)

    if line in storyPOS_dict:
        verbmatch_score = 0
        rootmatch_score = 0
        scoreOfALine = {}
        for (word,tag) in storyPOS_dict[line]:
            if 'V' in tag:
                verb_root = lancaster_stemmer.stem(word)
                if verb_root in rootsInAQuestion:
                    verbmatch_score = verbmatch_score + 6
            else:
                word_root = lancaster_stemmer.stem(word)
                if word_root in rootsInAQuestion:
                    rootmatch_score = rootmatch_score + 3
        scoreOfALine[line] = rootmatch_score + verbmatch_score
        return rootmatch_score + verbmatch_score

def wordTokenize(line):
    wordsInALine = word_tokenize(line)
    return wordsInALine

def removeStopWords(line):
    wordsInALine = wordTokenize(line)
    lineWithoutStopWords = []
    for word in wordsInALine:
        if word.lower() not in stopwordSet:
            if word.lower() not in punctuationSet:
                lineWithoutStopWords.append(word)
    return lineWithoutStopWords


def main():
 #   input_path = "/Users/roshaninagmote/PycharmProjects/question-answers/developset/"
  #  input_file = open(input_path+"/input_shreya.txt")
    semantic_classes("/Users/roshaninagmote/PycharmProjects/question-answers/")

    input_file_parameter = sys.argv[1]
    input_file = open(input_file_parameter)


    input_data = input_file.read().splitlines()
    input_path = input_data[0]
    for i in range(1,len(input_data)):

        each_story = input_data[i]+".story"
        each_question = input_data[i]+".questions"
        questions_file = open(input_path+each_question)
        questions_data_raw = questions_file.read().splitlines()
        questions_total = list(filter(None, questions_data_raw))

        questions_data = []
        for j in range(0,len(questions_total),3):
            question_temp = []
            quesid = questions_total[j].split(":")[1].lstrip(" ")
            question_temp.append(quesid)
            ques = questions_total[j+1].split(":")[1].lstrip(" ")
            question_temp.append(ques)
            question_temp.append(questions_total[j+2])

            questions_data.append(question_temp)


        story_dict = parse_story(input_path+each_story)
        data_forward(questions_data,story_dict)

if __name__ == "__main__":
    main()
