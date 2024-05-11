import pickle
import csv
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Spanish stop words
stop_words = nltk.corpus.stopwords.words('spanish')

def load_queries_from_csv(file_path):
    queries = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            queries.append((row['Category'], row['Query']))
    return queries

def train_classifier(training_data):
    # Tokenize and vectorize the training data
    vectorizer = CountVectorizer(tokenizer=word_tokenize, stop_words=stop_words, token_pattern=None)
    X_train = vectorizer.fit_transform([data[1] for data in training_data])
    y_train = [data[0] for data in training_data]

    # Train the classifier
    classifier = MultinomialNB()
    classifier.fit(X_train, y_train)
    return classifier, vectorizer

def predict_intent(text, classifier, vectorizer):
    # Tokenize and vectorize the input text
    text_vectorized = vectorizer.transform([text])
    # Predict the intent
    predicted_intent = classifier.predict(text_vectorized)
    return predicted_intent[0]

def save_model(classifier, vectorizer, model_file):
    with open(model_file, 'wb') as mf:
        pickle.dump((classifier, vectorizer), mf)

# Load queries from CSV
queries = load_queries_from_csv('datasets/assistant/assistant_queries.csv')

# Train classifier
classifier, vectorizer = train_classifier(queries)

# Example usage
user_input = "Necesito echar gasolina"
              
predicted_intent = predict_intent(user_input, classifier, vectorizer)
print("Intención predicha:", predicted_intent)

# Save the trained model
save_model(classifier, vectorizer, 'models/assistant_model.pkl')
