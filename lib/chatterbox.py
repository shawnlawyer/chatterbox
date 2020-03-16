from flask import session
from tensorflow.keras.models import Sequential, load_model, save_model
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
from tensorflow.python.keras.backend import set_session
import tensorflow as tf
import nltk
from nltk.stem.lancaster import LancasterStemmer
from pandas import DataFrame
import numpy as np
import pickle
import random
import subprocess
import json
from models import *

from envs import env
from adapters.chat import Application

class ChatterBox(object):

    models = {}

    def __init__(self, agent=None, required_models=[], error_threshold=0.25, full_init=True):

        self.agent = agent
        self.required_models = required_models
        self.error_threshold = error_threshold
        self.stemmer = LancasterStemmer()
        self.graph = None
        self.session = None
        if full_init:
            self.initialize_agents()

    def initialize_agents(self):
        self.graph = tf.get_default_graph()
        self.session = tf.Session()
        set_session(self.session)

        for model in self.required_models:
            self.models[model] = ChatModule(model)

    def classify(self, model, sentence):

        with self.graph.as_default():

            set_session(self.session)
            bag = [0]*len(model.vocabulary)
            for s in [self.stemmer.stem(word.lower()) for word in nltk.word_tokenize(sentence)]:
                for i,w in enumerate(model.vocabulary):
                    if w == s:
                        bag[i] = 1

            results = model.model.predict(DataFrame([(np.array(bag))], dtype=float, index=['input']))[0]
            results = [[i,r] for i,r in enumerate(results) if r>self.error_threshold]
            results.sort(key=lambda x: x[1])

        return results

    def intent(self, model, results):

        result = results.pop()
        intent_name = model.classes[result[0]]
        if intent_name == 'not_found':
            return ChatAgentResponse(intent_name, '' , result[1])

        intent_model = Intent().select().where(Intent.name == intent_name).get()

        if not intent_model.dialogs:


            response = Application().handle_request(intent_name)
            if response:
                response = ChatAgentResponse(intent_name, response , result[1])
            else:
                intent_response = random.choice(intent_model.responses)
                response = ChatAgentResponse(intent_name, intent_response.text , result[1])

        else:

            dialogs = []
            for dialog in intent_model.dialogs:
                if not dialogs:
                    dialog_intent_model = Intent().select().where(Intent.name == dialog.name).get()
                    response = ChatAgentResponse(intent_name, random.choice(dialog_intent_model.responses).text, result[1], dialog.input_type)
                dialogs.append({'name': dialog.name, 'slot': dialog.slot, 'value':None, 'input_type':dialog.input_type})
            session['intent'] = intent_model.name
            session['dialogs'] = dialogs
            session['dialog_step'] = 0

        if intent_model.contexts:
            contexts = []
            for context in intent_model.contexts:
                contexts.append(intent_model.text)
            session['context'] = " ".join(contexts)

        return response

    def dialog(self, input):

        self.store_input(input)

        if self.dialog_has_next_step():
            response = self.dialog_next_step()
        else:
            response = self.complete_dialog()

        return response

    def dialog_has_next_step(self):

        return session.get('dialog_step') + 1 < len(session.get('dialogs'))

    def dialog_next_step(self):

        dialogs = session.get('dialogs')
        session['dialog_step'] += 1
        intent_name = dialogs[session.get('dialog_step')]['name']
        intent_model = Intent().select().where(Intent.name == intent_name).get()

        return ChatAgentResponse(intent_name, random.choice(intent_model.responses).text, input_type=dialogs[session.get('dialog_step')]['input_type'])

    def store_input(self, input):

        dialogs = session.get('dialogs')
        dialogs[session.get('dialog_step')]['value'] = input
        session['dialogs'] = dialogs

    def complete_dialog(self):

        dialogs = session.get('dialogs')
        intent_model = Intent().select().where(Intent.name == session.get('intent')).get()
        slots = {}
        for dialog in dialogs:
            slots[dialog['slot']] = dialog['value']

        response = Application().handle_request(session.get('intent'), slots)

        response = ChatAgentResponse(session.get('intent'), response)

        self.clean_session()

        return response

    def chat(self, sentence):

        if not session.get('intent'):
            for model in self.models:
                results = self.classify(self.models[model], sentence)
                response = self.intent(self.models[model], results)
                if response.confidence > .85:
                    if response.classification == 'not_found':
                        continue
                    else:
                        break

        else:
            response = self.dialog(sentence)

        return response

    def clean_session(self):

        session['intent'] = None
        session['dialogs'] = None
        session['dialog_step'] = None

class ChatAgentResponse(object):

    def __init__(self, classification='not_found', response=None, confidence=1.0, input_type='text'):
        self.response = response.replace("\n","<br/>")
        self.confidence = float(confidence)
        self.classification = classification
        self.input_type = input_type

class ChatModule(object):

    def __init__(self, name, load=True):

        self.name = name
        self.module = Module().select().where(Module.name == name).get()
        if load:
            try:
                data = pickle.load( open( "chat/"+name+".pkl", "rb" ) )
                self.vocabulary = data['vocabulary']
                self.classes = data['classes']
                self.model = load_model("chat/"+name+".h5")
                self.model._make_predict_function()
            except:
                pass

    def fit(self, module=None):

        if not module:
            module = self.module

        intents = {}
        for intent in module.intents:
            if intent.patterns:
                intents[intent.name] = {"patterns":[]}
                for pattern in intent.patterns:
                    intents[intent.name]['patterns'].append(pattern.text)

        garbage_training_intents = Intent().select().where(Intent.agent != module.id)
        intents['not_found'] = {"patterns":[]}
        for intent in garbage_training_intents:
            if intent.patterns:
                for pattern in intent.patterns:
                    intents['not_found']['patterns'].append(pattern.text)

        vocabulary = []
        classes = []
        documents = []
        ignore_words = ['?']

        for intent_name in intents:
            intent = intents[intent_name]
            for pattern in intent['patterns']:
                w = nltk.word_tokenize(pattern)
                vocabulary.extend(w)
                documents.append((w, intent_name))
                if intent_name not in classes:
                    classes.append(intent_name)


        stemmer = LancasterStemmer()
        vocabulary = [stemmer.stem(w.lower()) for w in vocabulary if w not in ignore_words]
        vocabulary = sorted(list(set(vocabulary)))

        classes = sorted(list(set(classes)))
        training = []
        output_empty = [0] * len(classes)

        for doc in documents:
            bag = []
            pattern_words = doc[0]
            pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
            for word in vocabulary:
                bag.append(1) if word in pattern_words else bag.append(0)

            output_row = list(output_empty)
            output_row[classes.index(doc[1])] = 1
            training.append([bag, output_row])

        random.shuffle(training)
        training = np.array(training)
        train_x = list(training[:,0])
        train_y = list(training[:,1])

        tf_model = Sequential()
        tf_model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        tf_model.add(Dropout(0.5))
        tf_model.add(Dense(64, activation='relu'))
        tf_model.add(Dropout(0.5))
        tf_model.add(Dense(len(train_y[0]), activation='softmax'))

        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        tf_model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

        tf_model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

        save_model(tf_model, 'chat/' + module.name + '.h5', True)
        #converter = tf.lite.TFLiteConverter.from_keras_model_file('chat/model.h5')
        #tflite_model = converter.convert()
        #open("chat/model.tflite", "wb").write(tflite_model);

        with open("chat/" + module.name + ".pkl", "wb") as dataFile:
            pickle.dump({'vocabulary':vocabulary, 'classes':classes, 'train_x':train_x, 'train_y':train_y}, dataFile )

def restart_chat_application(self):
    subprocess.call(['./restart-chat.sh'])
