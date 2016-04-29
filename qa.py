import sys
import nltk
import os
import re
from nltk.stem import SnowballStemmer
from collections import OrderedDict

morpher = SnowballStemmer("english")
stopwords = nltk.corpus.stopwords.words('english')

# CHECK NUMBER OF ARGUMENTS PROVIDED
if len(sys.argv) != 2:
    print ('Usage: qa <inputfile>')
    sys.exit()

# DEFINE CUSTOM LISTS
MONTH = {'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'}
AMONTH = {'today', 'yesterday', 'tomorrow', 'last night'}
TIME_A = {'first', 'last', 'since', 'ago'}
TIME_B = {'start', 'begin', 'since', 'year'}

LOCATION = set()
NAME = set()
TIME = set()
HUMAN = set()
LOCPREP = set()

loc = open('places.txt','r')
for lines in loc:
   LOCATION.add(lines.strip())
loc.close()

name = open('nameList.txt','r')
for lines in name:
    NAME.add(lines.strip())
name.close()

time = open('time.txt','r')
for lines in time:
    TIME.add(lines.strip())
for x in range(0,2050):
    TIME.add(x)
for month in MONTH:
    TIME.add(month)
time.close()

human = open('human.txt','r')
for lines in human:
    HUMAN.add(lines.strip())
human.close()

locPrep = open('locPrep.txt','r')
for lines in locPrep:
    LOCPREP.add(lines.strip())
locPrep.close()

sentenceScore = OrderedDict()
best = set()

# PROCESS ANSWER FOR BETTER PRECESSION
def answerFinalizer(questions, answer):

    answerOriginal = answer
    answer = answer.lower()
    tagQuestion = nltk.pos_tag(nltk.word_tokenize(questions))
    tagAnswer = nltk.pos_tag(nltk.word_tokenize(answer))


    if 'where' in questions:
        newAnswer = answer
        answer = ''

        # for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(answerOriginal)), binary = True):
        #     if type(chunk) is nltk.tree.Tree:
        #         answer += ' ' + ' '.join(c[0] for c in chunk.leaves())

        if answer == '':
            for items in LOCPREP:
                if items + ' ' in newAnswer:
                    answer = newAnswer[newAnswer.index(items):]
                    break
                else:
                    answer = ''
                    for item in tagAnswer:
                        if 'NN' in item[1]:
                            answer = answer + ' ' + item[0]

        if answer == '':
            answer = newAnswer

    if 'who' in questions:
        newAnswer = answer
        answer = ''
        # for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(answerOriginal)), binary = True):
        #     if type(chunk) is nltk.tree.Tree:
        #         answer += ' ' + ' '.join(c[0] for c in chunk.leaves())
        #

        if answer == '':
            for i in range(0, len(tagAnswer)):
                if tagAnswer[i][0] in HUMAN:
                    for j in range(i, len(tagAnswer)):
                        if 'NN' in tagAnswer[j][1]:
                            answer = answer + ' ' + tagAnswer[j + 1][0]

        if answer == '':
            answer = newAnswer

    if 'how many' in questions or 'how much' in questions:
        newAnswer = answer
        answer = ''
        for i in range(0, len(tagAnswer)):
            if 'CD' in tagAnswer[i][1]:
                answer = answer + ' ' + tagAnswer[i][0]
                if i + 1 < len(tagAnswer) and 'NN' in tagAnswer[i + 1][1]:
                    answer = answer + ' ' + tagAnswer[i + 1][0]

        if answer == '':
            answer = newAnswer

    if 'how' in questions and 'by ' in answer:
        answer = answer[answer.index('by '):]

    if 'why' in questions:
        if 'because' in answer:
            answer = answer[answer.index('because '):]

        elif 'for ' in answer:
            answer = answer[answer.index('for '):]

        elif 'to ' in answer:
            answer = answer[answer.index('to '):]

    if 'when' in questions:
        tagAnswer = nltk.pos_tag(nltk.word_tokenize(answer))
        newAnswer = answer
        answer = ''
        for i in range(0, len(tagAnswer)):
            if 'CD' in tagAnswer[i][1]:
                answer = tagAnswer[i][0]
        if answer == '':
            answer = newAnswer

    if 'what' in questions:
        verb = ''
        for item in tagQuestion:
            if 'VB' == item[1]:
                verb = item[0]
                break

        verb = morpher.stem(verb)

        newAnswer = answer.split()
        for item in newAnswer:
            if verb in morpher.stem(item):
                answer = answer[answer.index(item):]
                break

    if ('where' in questions or 'how' in questions) and 'from ' in answer:
        answer = answer[answer.index('from '):]

    if 'being' in questions and 'being' in answer:
        answer = answer.split('being')[1]

    # questionSet = set()
    # for item in questions.split():
    #     questionSet.add(morpher.stem(item.replace("?", "")))
    #
    # answerSet = set()
    # for item in answer.split():
    #     answerSet.add(morpher.stem(item.replace("?", "")))
    questionSet = parser(questions)
    answerSet = parser(answer)
    common = questionSet.intersection(answerSet)

    newAnswer = answer.split()
    answer = ''
    for word in newAnswer:
        if word not in common:
            answer = answer + ' ' + word

    return answer

# DATELINE RULES
def dateLine(question):
    score = 0
    if 'happen' in question:
        score += 4
    if 'take' in question and 'place' in question:
        score += 4
    if 'this' in question:
        score += 20
    if 'story' in question:
        score += 20
    return score

# HOW RULES
def howRules(question, sentence):

    score = 0
    if 'how many' in question or 'how much' in question:
        tagSentence = nltk.pos_tag(nltk.word_tokenize(sentence))
        for i in range(0, len(tagSentence)):
            if 'CD' in tagSentence[i][1]:
               score += 6

    if 'by ' in sentence:
        score += 6

    return score

# WHY RULES
def whyRules(sentence):

    score = 0
    # RULE 1
    if sentence in best:
        score += 3

    # RULE 2
    index = sentenceScore.keys().index(sentence)
    if index < len(sentenceScore) - 1:
        if sentenceScore.keys()[index + 1] in best:
            score += 3

    # RULE 3
    if index > 0:
        if sentenceScore.keys()[index - 1] in best:
            score += 4

    # RULE 4
    if 'want' in sentence:
        score += 4

    # RULE 5
    if 'so' in sentence or 'because' in sentence:
        score += 4
    print(score, sentence)
    return score

# WHERE RULES
def whereRules(sentenceOriginal):
    score = 0
    sentence = sentenceOriginal.lower()

    # for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentenceOriginal))):
    #         if type(chunk) is nltk.tree.Tree:
    #             if 'LOCATION' in chunk.label() or 'GPE' in chunk.label():
    #                 score += 10

    # RULE 2
    for word in LOCPREP:
        if word in sentence:
            score += 4

    # RULE 3
    for word in LOCATION:
        if word in sentence:
            score += 6

    return score

# WHEN RULES
def whenRules(question, sentence):
    score = 0
    hasSentenceTimeA = False
    hasSentenceTimeB = False
    hasQuestionTimeA = False
    hasQuestionTimeB = False

    if 'the last' in question:
        hasQuestionTimeA = True

    if 'start' in question or 'begin' in question:
        hasQuestionTimeB = True

    for word in sentence:
        # RULE 1
        if word in TIME:
            score += 3
            score += worMatch(question, sentence)
        if word in TIME_A:
            hasSentenceTimeA = True
        if word in TIME_B:
            hasSentenceTimeB = True

        # RULE 2
        if hasQuestionTimeA and hasSentenceTimeA:
            score += 20

        # RULE 3
        if hasQuestionTimeB and hasSentenceTimeB:
            score += 20

    tagSentence = nltk.pos_tag(nltk.word_tokenize(sentence))
    for i in range(0, len(tagSentence)):
        if 'CD' in tagSentence[i][1]:
            score += 4
            break

    return score


# WHO RULES
def whoRules(question, sentenceOriginal):
    score = 0
    hasNameQuestion = False
    hasNameSentence = False
    hasnameSentence = False
    hasHumanSentence = False
    sentence = sentenceOriginal.lower()

    # for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentenceOriginal))):
    #         if type(chunk) is nltk.tree.Tree:
    #             if 'PERSON' in chunk.label() or 'ORGANIZATION' in chunk.label():
    #                 score += 10

    for item in question:
        if item in NAME:
            hasNameQuestion = True
            #break

        if item in HUMAN and item in sentence:
            score += 10

    for item in sentence:
        if item in NAME:
            hasNameSentence = True
        if 'name' in item:
            hasnameSentence = True
        if item in HUMAN:
            hasHumanSentence = True

    # RULE 2
    if not hasNameQuestion and hasNameSentence:
        score += 6

    # RULE 3
    if not hasNameQuestion and hasnameSentence:
        score += 4

    # RULE 4
    if hasNameSentence or hasHumanSentence:
        score += 4

    return score


# WHAT RULES
def whatRules(question, sentence):
    score = 0
    hasMonthQuestion = False
    hasMonthSentence = False
    hasKindQuestion = False
    hasNameQuestion = False
    hasKindSentence = False
    hasKnownSentence = False
    hasRuleFive = False
    hasNameAnswer = False

    questions = nltk.pos_tag(nltk.word_tokenize(question))
    sentences = nltk.pos_tag(nltk.word_tokenize(sentence))

    for word in questions:
        if word[0] in MONTH:
            hasMonthQuestion = True
        if 'kind' == word[0]:
            hasKindQuestion = True
        if 'name' == word[0] :
            hasNameQuestion = True

    for word in sentences:
        if word[0] in AMONTH:
            hasMonthSentence = True
        if 'call' == word[0] or 'from' == word[0]:
            hasKindSentence = True
        if 'name' in word[0]:
            hasNameAnswer = True
        if 'call' == word[0] or 'known' == word[0]:
            hasKnownSentence = True

    # RULE 2
    if hasMonthQuestion and hasMonthSentence:
        score += 3

    # RULE 3
    if hasKindQuestion and hasKindSentence:
        score += 4

    # RULE 4
    if hasNameQuestion and (hasNameAnswer or hasKnownSentence):
        score += 20

    # RULE 5
    for i in range(0,len(questions) - 1):
        if 'name' == questions[i][0] and 'IN' == questions[i + 1][1]:
            for j in range(i + 1, len(questions)):
                if 'NN' == questions[j][1] and questions[j][0] in sentence:
                    hasRuleFive = True

    if hasRuleFive:
        score += 20

    return score

def addToSentenceScore(question, sentence):

    score = 0

    questionSet = set()
    for item in question.split():
        questionSet.add(morpher.stem(item.replace("?","")))

    sentenceSet = set()
    for item in sentence.split():
        sentenceSet.add(morpher.stem(item.replace("?","")))

    jaccard = float(len(questionSet.intersection(sentenceSet))) / float(len(questionSet.union(sentenceSet)))

    common = ' '.join(sentenceSet.intersection(questionSet))
    tagCommon = nltk.pos_tag(nltk.word_tokenize(common))
    if tagCommon:
        for item in tagCommon:
            if 'VB' in item[1]:
                score += 6
            else:
                score += 3

    # Add sentence and score to a hashmap
    sentenceScore[sentence] = score + (jaccard * 10)
    return score

# PARSER TO TOKENIZE, REMOVE STOP WORDS, MORPHOLOGY, ADD TO SET
def parser(line):
    tokLine = nltk.word_tokenize(line)
    keywords = list(set(tokLine) - set(stopwords))
    lineSet = set()
    for item in keywords:
        lineSet.add(morpher.stem(item.replace("?", "")))
    return lineSet


# WORD MATCH
def worMatch(question, sentence):

    score = 0

    questionSet = set()
    for item in question.split():
        questionSet.add(morpher.stem(item.replace("?","")))

    sentenceSet = set()
    for item in sentence.split():
        sentenceSet.add(morpher.stem(item.replace("?","")))

    jaccard = float(len(questionSet.intersection(sentenceSet))) / float(len(questionSet.union(sentenceSet)))

    common = ' '.join(sentenceSet & questionSet)
    tagCommon = nltk.pos_tag(nltk.word_tokenize(common))
    if tagCommon:
        for item in tagCommon:
            if 'VB' in item[1]:
                score += 6
            else:
                score += 3

    return score + (jaccard * 10)



# GET INPUT FILE NAME
inputFile = sys.argv[1]

# GET PATH FROM INPUT FILE
f = open(inputFile, 'r')
path = f.readline()

# OPEN EACH QUESTION FILE FROM THE GIVEN PATH AND READ THE STORY
for line in f:
    storyPath = path.strip() + line.strip() + '.story'
    questionPath = path.strip() + line.strip() + '.questions'

    storyFile = open(storyPath, 'r')
    HEADLINE = storyFile.readline()
    DATELINE = storyFile.readline()
    STORYID = storyFile.readline()

    while 'TEXT' not in storyFile.readline():
        continue

    story = storyFile.read()
    storyFile.close()

    match = re.findall(r"(\.(.)\.)",story)
    for x in match:
       val = ' ' + str(x[1]) + ' '
       story = story.replace(x[0], val)

    sentences = [HEADLINE.split(':')[1]] + [DATELINE.split(':')[1]] + nltk.tokenize.sent_tokenize(story)

    questionFile = open(questionPath, 'r')
    for questions in questionFile:
        if 'QuestionID:' in questions:
            print (questions.strip())

        elif 'Question:' in questions:
            #questionsOriginal = questions
            questions = questions.lower()
            question = questions.split(':')
            maxScore = 0
            answer = ''
            
            # WHY rules
            if 'why' in questions:
                # Find the best score and create a dictionary
                bestScore = 0
                best = set()
                sentenceScore = OrderedDict()
                for s in sentences:
                    s = s.lower()
                    currentScore = addToSentenceScore(question[1], s)
                    if currentScore > bestScore:
                        bestScore = currentScore

                # Add the best score sentence into a list
                for key in sentenceScore:
                    if sentenceScore[key] == bestScore:
                        best.add(key)

            localSentenceScore = OrderedDict()

            for sentence in sentences:
                sentenceOriginal = sentence
                sentence = sentence.lower()
                myscore = 0

                # Common function to find similarity between question and sentence
                myscore = worMatch(question[1], sentence)

                # WHO rules
                if 'who' in questions:
                    myscore += whoRules(question[1], sentenceOriginal)

                # WHAT rules
                elif 'what' in questions:
                    myscore += whatRules(question[1], sentence)

                # WHEN rules
                elif 'when' in questions:
                    myscore += whenRules(question[1], sentence)
                    if sentence in DATELINE.lower():
                        myscore += dateLine(question[1])

                # WHERE rules
                elif 'where' in questions:
                    myscore += whereRules(sentenceOriginal)
                    if sentence in DATELINE.lower():
                        myscore += dateLine(question[1])

                # WHY rules
                elif 'why' in questions:
                    myscore += whyRules(sentence)

                # HOW rules
                elif 'how' in questions:
                    myscore += howRules(question[1], sentence)

                localSentenceScore[sentenceOriginal.replace('\n',' ')] = myscore
                if myscore > maxScore:
                    maxScore = myscore

            # Multiple answers with same score
            for key in localSentenceScore:
                    if localSentenceScore[key] == maxScore:
                        if answer == '':
                            answer = key
                        else:
                            answer = answer + ' | ' + key

            # Tie breaker
            if '|' in answer:
                finalAnswer = answer.split('|')
                if 'why' in questions:
                    answer = finalAnswer[len(finalAnswer) - 1]
                else:
                    answer = finalAnswer[0]

            # No answers found
            if maxScore == 0:
                if 'why' in questions:
                    answer = localSentenceScore.keys()[len(localSentenceScore) - 1]
                elif 'when' in questions or 'where' in questions:
                    answer = DATELINE.split(':')[1]
                else:
                    answer = localSentenceScore.keys()[2]

            # Process the answer to improve precession
            myAnswer = answerFinalizer(questions, answer)
            print 'Answer:', myAnswer
            print ''

    questionFile.close()
f.close()