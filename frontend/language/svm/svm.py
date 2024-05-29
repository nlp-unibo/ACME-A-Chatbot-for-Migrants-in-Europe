import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.svm import SVC
from joblib import dump, load
import os
from scipy.spatial.distance import braycurtis
from language.language import get_embeddings


class DialogueActClassifier:

    def __init__(self, data_path, model_path) -> None:
        self.data_path = data_path
        self.model_path = model_path

        self.best_hyperparams = None


    def prepare_data(self, test_size=0.1):
        df = pd.read_csv(self.data_path)

        df = df.rename(columns={'Category_1': 'dialogue_act'})
        df = df[df['dialogue_act'].isin(['y',  'n', 'y-d', 'n-d'])]
        labels = df['dialogue_act']
        train = df.drop(['dialogue_act', 'Q/A'], axis=1)

        train_texts, test_texts, train_labels, test_labels = train_test_split(train, labels, test_size=test_size, random_state=42, shuffle=False)
        train_texts, test_texts, train_labels, test_labels = train_texts.values.ravel(), test_texts.values.ravel(), train_labels.values, test_labels.values
        return train_texts, test_texts, train_labels, test_labels

    def train(self, train_texts, train_labels, folds=5, scoring='f1_micro'):
        
        if not os.path.exists(self.model_path):
            parameters = {'C': [0.1, 0.5, 1, 1.5, 2, 10],
                        'kernel': ['poly', 'rbf', 'linear', 'sigmoid'],
                        'gamma': ['scale', 'auto']}
            
            model = SVC(random_state=42, class_weight='balanced', probability=True)
            # grid_classifier = GridSearchCV(model, parameters, cv=folds, scoring=scoring) # micro bc class imbalance
            grid_classifier = GridSearchCV(model, parameters, cv=folds, scoring=scoring) # micro bc class imbalance
            current_module_path = os.path.dirname(os.path.realpath(__file__))
            _, train_embeddings = get_embeddings(train_texts, embedding_file=os.path.join(current_module_path, 'train_embs.json'))

            grid_classifier.fit(train_embeddings, train_labels)
            
            best_classifier = grid_classifier.best_estimator_
    
           
            self.best_hyperparams = grid_classifier.best_params_

            dump(best_classifier, self.model_path)
            
        else:
            model = load(self.model_path)


        return model

    def predict(self, sentence):
        
        model = load(self.model_path)

        _, test_embeddings = get_embeddings(sentence)
        
        probabilities = model.predict_proba(test_embeddings.reshape(1,-1))
        pred = model.classes_[np.argmax(probabilities[0])]
            

        if pred in ['y', 'y-d']:
            
            return 'yes'
        elif pred in ['n', 'n-d']:
            return 'no'
        
        return ''


