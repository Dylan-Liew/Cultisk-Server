import pickle
import pandas as pd
import re
import os


class SpamFilter:
    def __init__(self,training_set_clean,vocabulary,test_set):
        self.test_set = test_set
        self.spam_messages = training_set_clean[training_set_clean['Label'] == 'spam']
        self.ham_messages = training_set_clean[training_set_clean['Label'] == 'ham']

        # P(Spam) and P(Ham)
        self.p_spam = len(self.spam_messages) / len(training_set_clean)
        self.p_ham = len(self.ham_messages) / len(training_set_clean)

        # N_Spam
        n_words_per_spam_message = self.spam_messages['SMS'].apply(len)
        n_spam = n_words_per_spam_message.sum()

        # N_Ham
        n_words_per_ham_message = self.ham_messages['SMS'].apply(len)
        n_ham = n_words_per_ham_message.sum()

        # N_Vocabulary
        n_vocabulary = len(vocabulary)

        # Laplace smoothing
        alpha = 1

        # Initiate parameters
        self.parameters_spam = {unique_word: 0 for unique_word in vocabulary}
        self.parameters_ham = {unique_word: 0 for unique_word in vocabulary}

        # Calculate parameters
        for word in vocabulary:
            n_word_given_spam = self.spam_messages[word].sum()  # spam_messages already defined
            p_word_given_spam = (n_word_given_spam + alpha) / (n_spam + alpha * n_vocabulary)
            self.parameters_spam[word] = p_word_given_spam

            n_word_given_ham = self.ham_messages[word].sum()  # ham_messages already defined
            p_word_given_ham = (n_word_given_ham + alpha) / (n_ham + alpha * n_vocabulary)
            self.parameters_ham[word] = p_word_given_ham

    def classify(self,message):
        ori_message = message
        message = re.sub(r"\W", ' ', message)
        message = message.lower().split()
        p_spam_given_message = self.p_spam
        p_ham_given_message = self.p_ham

        for word in message:
            if word in self.parameters_spam:
                p_spam_given_message *= self.parameters_spam[word]
            if word in self.parameters_ham:
                p_ham_given_message *= self.parameters_ham[word]

        if p_ham_given_message > p_spam_given_message:
            print('Label: Ham(Non-Spam) Message')
            return 'ham'

        elif p_ham_given_message < p_spam_given_message:
            file_object = open('SMSSpamCollection', 'a')
            new_message = '\nspam\t' + ori_message
            # print(new_message)
            file_object.write(new_message)
            file_object.close()
            print('Label: Spam Message')
            return 'spam'
        else:
            print('Equal probabilities, have a human classify this!')
            return 'needs human classification'

    def classify_test_set(self,message):

        message = re.sub(r'\W', ' ', message)
        message = message.lower().split()

        p_spam_given_message = self.p_spam
        p_ham_given_message = self.p_ham

        for phrase in message:
            if phrase in self.parameters_spam:
                p_spam_given_message *= self.parameters_spam[phrase]

            if phrase in self.parameters_ham:
                p_ham_given_message *= self.parameters_ham[phrase]

        if p_ham_given_message > p_spam_given_message:
            return 'ham'
        elif p_spam_given_message > p_ham_given_message:
            return 'spam'
        else:
            return 'needs human classification'

    def testing_accuracy(self):
        test_set = self.test_set
        test_set['predicted'] = test_set['SMS'].apply(self.classify_test_set)
        test_set.head()

        correct = 0
        total = test_set.shape[0]

        for row in test_set.iterrows():
            row = row[1]
            if row['Label'] == row['predicted']:
                correct += 1

        print('Correct:', correct)
        print('Incorrect:', total - correct)
        print('Accuracy:', correct / total)


def update_mi():
    sms_spam = pd.read_csv('SMSSpamCollection', sep='\t', header=None, names=['Label', 'SMS'])

    # print(sms_spam.shape)
    sms_spam.head()
    # value1 = sms_spam['Label'].value_counts(normalize=True)

    # Randomize the dataset
    data_randomized = sms_spam.sample(frac=1, random_state=1)

    # Calculate index for split
    training_test_index = round(len(data_randomized) * 0.8)

    # Split into training and test sets
    training_set = data_randomized[:training_test_index].reset_index(drop=True)
    test_set = data_randomized[training_test_index:].reset_index(drop=True)

    # Before cleaning
    training_set.head(3)

    # After Cleaning
    #training_set['SMS'] = training_set['SMS'].str.replace('\W', ' ')# Removes punctuation
    #words = re.split(r'\W+', text)
    training_set['SMS'] = [re.sub(r'\W', ' ', e) for e in training_set['SMS']]
    #training_set['SMS'] = re.sub(r'\W',' ',training_set['SMS'])# Removes punctuation

    training_set['SMS'] = training_set['SMS'].str.lower()
    training_set.head(3)

    training_set['SMS'] = training_set['SMS'].str.split()

    vocabulary = []
    for sms in training_set['SMS']:
        for word in sms:
            vocabulary.append(word)

    vocabulary = list(set(vocabulary))

    # To create the dictionary
    word_counts_per_sms = {unique_word: [0] * len(training_set['SMS']) for unique_word in vocabulary}

    for index, sms in enumerate(training_set['SMS']):
        for word in sms:
            word_counts_per_sms[word][index] += 1

    word_counts = pd.DataFrame(word_counts_per_sms)
    word_counts.head()
    training_set_clean = pd.concat([training_set, word_counts], axis=1)
    training_set_clean.head()

    efilter = SpamFilter(training_set_clean, vocabulary, test_set)
    efilter.classify_test_set(
        "We regret to inform you that your account has been restricted. To continue using our services please download the file attached to this email and update your login in")
    efilter.testing_accuracy()

    filename = 'efilter_model.sav'
    if os.path.exists(filename):
        print('removed file')
        os.remove(filename)

    # save model in the .sav file
    with open(filename, "wb") as f:
        pickle.dump(efilter, f)

    # Load the pickled model
    # with open(filename, 'rb') as p:
    #     cols = pickle.load(p)
    #
    # # Use the loaded pickled model to make predictions
    # c = cols.classify_test_set("Sounds good, Tom, then see u there")
    # print(c)

#e=cols.classify_test_set("Sounds good, Tom, then see u there")


if __name__ == "__main__":
    update_mi()
