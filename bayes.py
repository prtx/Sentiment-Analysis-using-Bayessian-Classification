import nltk, sqlite3
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')


class Database:
	
	def __init__(self, x):
	
		self.conn = sqlite3.connect(x)
		self.conn.text_factory = str
	
	def instance(self):
		return self.conn.cursor()
	
	def commit(self):
		self.conn.commit()

class Bayessian_Classifier:
	
	def __init__(self, database = 'Data.db'):
		self.database = Database(database)
		self.stopwords = open('stopwords.txt').read().split('\n')
	
	def filter_words(self, text):

		word_cloud = {}
		words = tokenizer.tokenize(text.lower())
		for word in list(set(words)):

			if len(word) > 1 and not word.isdigit() and word not in self.stopwords:
				word_cloud[word] = words.count(word)
		
		return word_cloud

	def train(self, text, tag):
		
		db = self.database.instance()
		
		word_cloud = self.filter_words(text)
		print 'filtered'
		for word in word_cloud:
			db.execute('select count from BAG_OF_WORDS where word=? and tag=?', (word, tag))
			existing_count = db.fetchone()
			if existing_count:
				db.execute('update BAG_OF_WORDS set count=? where word=? and tag=?', (existing_count[0] + word_cloud[word], word, tag))
			else:
				db.execute('insert into BAG_OF_WORDS (word, tag, count) values (?,?,?)', (word, tag, 1))
		
		self.database.commit()
	
	def classify(self, text):
	
		db = self.database.instance()
		positive_count = 0.0
		negative_count = 0.0
	
		for word in self.filter_words(text):
			db.execute('select count from BAG_OF_WORDS where word=? and tag=?', (word,'P'))
			existing_positive = db.fetchone()
			if existing_positive:
				positive_count += existing_positive[0]
						
			db.execute('select count from BAG_OF_WORDS where word=? and tag=?', (word,'N'))
			existing_negative = db.fetchone()
			if existing_negative:
				negative_count += existing_negative[0]

		
		if positive_count + negative_count < 3:
			return 0.5
		elif positive_count == 0:
			return 0.05
		elif negative_count == 0:
			return 0.95
		else:
			return float(positive_count/(positive_count+negative_count))


if __name__ == '__main__':
	
	print 'Sentiment Analysis Accuracy Calculation\n'

	bayes = Bayessian_Classifier()
	
	#bayes.train(open('positive_training_set.py'), 'P')
	#bayes.train(open('negative_training_set.py'), 'N')
	
	positive_testing_set = open('positive_testing_set.txt').readlines()[2500:5000]
	negative_testing_set = open('negative_testing_set.txt').readlines()[2500:5000]

	true_positive = 0.00
	true_negative = 0.00
	false_positive = 0.00
	false_negative = 0.00

	for counter, positive_sentence in enumerate(positive_testing_set):
		if bayes.classify(positive_sentence) > 0.5:
			true_positive += 1
		else:
			false_negative += 1
		print counter
	print 'Total positive text set: ', counter + 1
	
	for counter, negative_sentence in enumerate(negative_testing_set):
		if bayes.classify(negative_sentence) < 0.5:
			true_negative += 1
		else:
			false_positive += 1
		print counter
	print 'Total negative text set: ', counter + 1

	print
	print 'True positive', true_positive
	print 'True negative', true_negative
	print 'False positive', false_positive
	print 'False negative', false_negative
	print
	print 'Accuracy: ', (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative)
	print 'Recall: ', true_positive / (true_positive + false_negative)
	print 'Precision: ', true_positive / (true_positive + false_positive)
	print '\n'*10
