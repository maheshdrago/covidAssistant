import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import subprocess
import wikipedia
import sys
import requests
import random
import tflearn
from tensorflow.python.framework import ops
import numpy
import json
import pickle
import pyttsx3
import speech_recognition as sr
from corona_tracker import corona_tracker
from corona_predictor import track_covid
from sleep_tracker import sleeptime

import re
import spacy
import os
import os.path
import playsound
import time
import winsound
from datetime import datetime,timedelta
import multiprocessing
import sounddevice
from scipy.io import wavfile  
import random


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtGui import QMovie
from PyQt5.uic  import loadUiType
from ass import Ui_Assistant


global data
with open("intents.json") as file:
    data = json.load(file)

try:
    
    with open("data.pickle",'rb') as f:
        words,labels,training,output = pickle.load(f)


except:

    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["text"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["intent"])

        if intent["intent"] not in labels:
            labels.append(intent["intent"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)


    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle",'wb') as f:
        pickle.dump((words,labels,training,output),f)

ops.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    
    model.load("model.tflearn")

except:
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return numpy.array(bag)



class Inputs(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Assistant()
        self.ui.setupUi(self)
    
    def speak_s(self,text):

        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        engine.say(text)
        engine.runAndWait()
    
    def take_input(self):
        
        obj = Main()
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            while True:
                try:
                   
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                    string = r.recognize_google(audio)
                    return string
                except:
                    self.speak_s("I dont understand that")
                    continue

 
class AlarmThread(QThread):

    def __init__(self):
        super(AlarmThread,self).__init__()
        
    def ta_input(self):
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            
            try:
                print("Alarm input")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                string = r.recognize_google(audio)
                return string
            except:
                return "no"

    
    def run(self):
        
        self.check()
    
    def check(self):
        obj = Inputs()
        while True:
            if os.path.exists("alarms.txt"):
                
                fs,data = wavfile.read('alarm.wav')
                with open("alarms.txt",'r') as f:
                    alarms =f.readlines()

                    for i in range(len(alarms)):
                        alarms[i] = alarms[i].replace("\n","")
                    for i in alarms:
                        curr_obj = datetime.now()
                        curr_time = '{:%H:%M %p}'.format(curr_obj)
                        curr_day = '{:%d-%m-%Y}'.format(curr_obj)
                        
                        curr_pattern = '{} {}'.format(curr_day,curr_time)
                        
                        if curr_pattern==i:
                            tm = i.split(":")[1].replace("AM","").replace("PM","")
                            curr_min = curr_obj.minute
                            while curr_min <= int(tm):
                                curr_min = datetime.now().minute
                                sounddevice.play(data,fs)
                                ala_inp = self.ta_input().lower()
                                if ala_inp == 'stop' or ala_inp=="shut up" or ala_inp=="ok" :
                                    obj.speak_s("ok mahesh")
                                    sounddevice.stop()
                                    break
                                

                        time.sleep(10)

    def stop(self):
        
        playsound.playsound('alarm.mp3',False)



class MedThread(QThread):

    def __init__(self):
        super(MedThread,self).__init__()
    
    def run(self):
        self.check()

    def ta_input(self):
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            
            try:
                print("med input")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                string = r.recognize_google(audio)
                return string
            except:
                return "no"

    def check(self):
        obj = Inputs()
        with open("medication.txt","r") as med:
            meds = med.readlines()
        
        if len(meds)>0:
            for i in range(len(meds)):
                meds[i] = meds[i].replace("\n",'')
        
        if len(meds)>0:
          
            while True:
                curr_obj = datetime.now()
                curr_time = '{:%I:%M %p}'.format(curr_obj)
                for i in meds:
                    
                    if str(i) in curr_time:
                        fs,data = wavfile.read('medit.wav')
                        #tm = str(i).split(':')[1].replace('AM','').replace('PM','')
                        for i in range(5):
                            curr_min = datetime.now().minute
                            sounddevice.play(data,fs)
                            ala_inp = self.ta_input().lower()
                            if ala_inp == 'stop' or ala_inp=="shut up" or ala_inp=="ok" :
                                obj.speak_s("ok mahesh")
                                sounddevice.stop()
                                break
                    

                    time.sleep(10)
            

        

class MainThread(QThread):

    def __init__(self):
        super(MainThread,self).__init__()
    
    def run(self):
        
        self.chat()

    def speak_s(self,text):

        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        engine.say(text)
        engine.runAndWait()

    def take_input(self):
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            while True:
                try:
                    
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                    string = r.recognize_google(audio)
                    return string
                except:
                    
                    continue

    def takeY_input(self):
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            
            try:
                    
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                string = r.recognize_google(audio)
                return string
            except:
                    
                pass  

    def chat(self):
        
        with open("intents.json") as file:
            data = json.load(file)
        
        obj = Inputs()
        obj1 = AlarmThread()
        wake = "activate"
        
        while True:

            
            print("speak")
            #self.speak_s("activate to continue")
            active = self.take_input().lower()
            
            #active = "activate"
            print(active)
                
            if active.count(wake) > 0:
                if os.path.exists("initial.txt"):
                    playsound.playsound('chime.mp3')
                    self.speak_s("Hi mahesh what can i do for you")
    
                else:
                    with open("initial.txt",'w') as f:
                        
                        playsound.playsound('power up.mp3')
                        with open("tips.txt",'r') as f:
                            fs = f.readlines()

                    tips = []

                    for i in fs:
                        tips.append(i.replace("\n",'').strip())
                    
                    rand_int = random.randint(0,7)
                    
                    rand_tip = tips[rand_int]
                    
                    greet_time = '{:%I:%M %p}'.format(datetime.now())

                    if 'AM' in greet_time:
                        self.speak_s("Good Morning mahesh,hope you had a good sleep")
                    elif 'PM' in greet_time:

                        split_time = greet_time.split(':')
                        greet_time = int(split_time[0][1:])
                        
                        if greet_time<2:
                            self.speak_s("Good afternoon mahesh")
                        else:
                            self.speak_s("Good evening mahesh")
                    
                    self.speak_s("Heres a healthy tip for you mahesh:")
                    self.speak_s(rand_tip)
                    
                

                print("\n\n\t\t\t Started")

                #self.speak_s("Start talking with the bot (type quit to stop)!")

                inp = obj.take_input() 
                #inp = "make a note"
                print(inp)

                if inp.lower() == "quit":
                    break

                if 'alarm'  in inp.lower() or 'wake' in inp.lower():

                    
                    next_days = ['today','tomorrow']

                    nlp = spacy.load('en_core_web_sm')
                    doc = nlp(inp)
                    entities = []
                    for ent in doc.ents:
                        entities.append(ent)
                    print(entities)
                    
                    if len(entities)==1:

                        
                        inp_split = str(entities[0]).split()

                        if inp_split[1].lower()=="hours":

                            day_after_adding = datetime.now() + timedelta(hours=int(inp_split[0]))
                            formatted_time = '{:%H:%M %p}'.format(day_after_adding)
                            formatted_day = '{:%d-%m-%Y}'.format(day_after_adding)

                            data = '{} {}\n'.format(formatted_day,formatted_time)
                        
                        elif inp_split[1].lower()=="minutes":
                            
                            print(inp_split)
                            day_after_adding = datetime.now() + timedelta(minutes=int(inp_split[0]))
                            formatted_time = '{:%H:%M %p}'.format(day_after_adding)
                            formatted_day = '{:%d-%m-%Y}'.format(day_after_adding)

                            data = '{} {}\n'.format(formatted_day,formatted_time)
                        
                        elif inp_split[1].lower()=="seconds":
                            
                            print(inp_split)
                            day_after_adding = datetime.now() + timedelta(seconds=int(inp_split[0]))
                            formatted_time = '{:%H:%M %p}'.format(day_after_adding)
                            formatted_day = '{:%d-%m-%Y}'.format(day_after_adding)

                            data = '{} {}\n'.format(formatted_day,formatted_time)

                        
                        with open("alarms.txt",'a') as f:
                            f.write(data)
                        
                elif "sleep tracker" in inp.lower():
                    sleep_time = sleeptime()
                    self.speak_s("you have slept for "+sleep_time)
                
                elif "yoga mode" in inp.lower() or "yoga" in inp.lower():
                    yoga_inputs = {
                        "Triangle(Trikonasana)" : "Stand with your feet wide apart. Stretch your right foot out (90 degrees) while keeping the leg closer to the torso. Keep your feet pressed against the ground and balance your weight equally on both feet. Inhale and as you exhale Rest your right hand on your shin, ankle, or the floor outside your right foot, Stretch your left arm toward the ceiling.Turn your gaze up to the top hand and stay in this pose for 5-8 breaths. Inhale to come up and repeat on the opposite side.",

                        "Warrior(Virabhadrasana)" : "Stand in Tadasana (Mountain Pose). With an exhale, step or lightly jump your feet apart. Raise your arms perpendicular to the floor (and parallel to each other).Turn your left foot in 45 to 60 degrees to the right and your right foot out 90 degrees to the right. Align the right heel with the left heel. Exhale and rotate your torso to the right.With your left heel firmly on the floor, exhale and bend your right knee over the right ankle so the shin is perpendicular to the floor.To come up, inhale, press the back heel firmly into the floor and reach up through the arms, straightening the right knee. Turn the feet forward and release the arms with an exhalation. Take a few breaths, then turn the feet to the left and repeat for the same length.",

                        "Downward-Facing Dog(Adho Mukha Svanasana)" : "Come onto the floor on your hands and knees. With your hands slightly forward of your shoulders and knees below your hips.Spread your hands wide and press your index finger and thumb into your mat.Exhale and lift your knees away from the floor lift the butt toward the ceiling. Straighten your legs as much as you can and press your heels gently toward the floor.Your head should be between your arms, facing your knees, and your backs should be flat.Hold for 5-10 breaths.",

                        "Upward-Facing Dog(Urdhva Mukha Svanasana)" : "Lie on your stomach on mat . Stretch your legs back, with the tops of your feet on the mat. Bend your elbows and spread your palms on the mat beside your waist.Inhale and press your inner hands firmly into the mat Then straighten your arms and simultaneously lift your cheat up and your legs a few inches off the mat.Pull your shoulders back, squeeze your shoulder blades, and tilt your head toward the ceiling, to open up your chest.",

                        "Seated Forward Fold( Paschimottanasana )" : "Sit on the floor with ith your buttocks supported on a folded blanket your legs extended in front of you. Breathe in and raise your hands over your head and stretch. Extend the arms forward, reaching for your feet.Lift your chest engage your lower abdominals and imagine your belly button moving towards the top of your thighs.Hold the pose for up to 10 breath before slowly releasing with an inhalation.",

                        "Bridge Pose(Setubandhasana)" : "Begin lying comfortably on your back in a supine position and place your feet hip width apart.Press firmly on to your feet and lift your butt up off the mat. Interlock your palm and press the shoulder toword the floor.Imagine dragging your heels on the mat towards your shoulders to engage your hamstrings. Hold for 8-10 breaths then lower your hips down and repeat two more times.",

                        "Child Pose( Balasna )" : "Kneel on the floor. Touch your big toes together and sit on your heels, then separate your knees about as wide as your hips.Exhale and lay your abdomen resting between your inner thighs and rest your forehead on the mat.Rest your arms by your sides with your palms facing up near your feet.Stay in the pose from 5 to 10 breaths. To come up, first lengthen the front torso, and then with an inhalation Gently release back.",

                        "Tree Pose(Vrksasana)" : "Start with your feet together and place your right foot on your inner left upper thigh. Press your hands in prayer and find a spot in front of you that you can hold in a steady gaze.Hold and breathe for 8-10 breaths then change sides. Make sure you don't lean in to the standing leg and keep your core engaged and shoulders relaxed." 
                    }

                    
                    fs,data = wavfile.read('yoga.wav')
                    
                    while True:
                        inp1 = "warrior"
                        
                        
                        flag = True

                        for i in yoga_inputs.keys():
                            

                            if flag:
                                ind = [i[:i.index("(")].lower(),i[i.index("(")+1:len(i)-1].lower()]
                                out_seg = yoga_inputs[i] 
                                
                                if inp1.lower() in ind:
                                    
                                    sounddevice.play(data,fs)
                                    out_fin = out_seg.split(".")
                                    for i in out_fin:
                                        inp2 = self.takeY_input()
                                        
                                        if inp2:
                                            if(inp2.lower() == "stop" or inp2.lower() == "top" or inp2.lower() == "shut down" or inp2.lower() == "quit"  ):
                                                self.speak_s("Quiting yoga mode")
                                                flag =False
                                                sounddevice.stop()
                                                break
                                        self.speak_s(i)
                                        time.sleep(2)

                elif "search" in inp.lower() or "wikipedia" in inp.lower() or "search wikipedia" in inp.lower():
                    self.speak_s("what would you want me to search:")
                    query = self.take_input()
                    self.speak_s('Searching Wikipedia...')

                    try:
                        results = wikipedia.summary(query, sentences = 3)
                        self.speak_s("According to Wikipedia")
                        print(results)
                        self.speak_s(results)
                    except:
                        self.speak_s("Couldnt fetch it please try again")
                        


                elif "make a note" in inp.lower() or 'remember this' in inp.lower() or "write down" in inp.lower():
                    date =datetime.now()
                    file_name = str(date).replace(':','-')+"-note.txt"
                    self.speak_s("What would you like to note")
                    text = self.take_input()
                    print(text)
                    print("iii")
                    with open(file_name,'w') as f:
                        f.write(text)
                    subprocess.Popen(['notepad.exe',file_name])

                elif "future" in inp.lower() or 'prediction' in inp.lower():
                    self.speak_s("How many days :")
                    days = self.take_input()
                    print(days)

                    days = re.findall(r'\d+', days)
                    value = track_covid(int(days[0]))
                    self.speak_s("There is a high chance of covid cases to increase ,to be accurate the cases would be "+"{:,} by {} days".format(value,days))

                elif 'covid' in inp.lower() or 'covid-19' in inp.lower() or 'corona' in inp.lower() or 'covid 19' in inp.lower():
                    d = corona_tracker(inp)
                    self.speak_s("Total confirmed cases are "+"{:,}".format(d['confirmed']))
                    self.speak_s("Total deaths are "+"{:,}".format(d['deaths']))
                    self.speak_s("Total recovered cases are "+"{:,}".format(d['recovered']))
                
                elif 'play music' in inp.lower() :
                    fs,data = wavfile.read('go.wav')                    
                    sounddevice.play(data,fs)
                    while True:
                        ala_inp = self.take_input().lower()
                        print(ala_inp)
                        if ala_inp == 'top' or ala_inp == 'stop' or ala_inp=="shut up" or ala_inp=="ok" :
                            obj.speak_s("ok mahesh")
                            sounddevice.stop()
                            break

                
                elif 'medication' in inp.lower() or "schedule" in inp.lower() or 'medicine' in inp.lower():
                    
                    nlp = spacy.load('en_core_web_sm')
                    doc = nlp(inp.lower())
                    entities = []
                    for ent in doc.ents:
                        entities.append(ent)
                    
                    
                    s_time = str(entities[0]).replace(".","")
                    ap = ''
                    indx = -1
                    for i in range(len(s_time)):
                        if s_time[i].isalpha():
                            indx = i
                            break
                    
                    times = s_time[:indx]+s_time[indx:].upper()

                   
                    
                    with open("medication.txt",'a') as med:
                        med.write(times+"\n")
                    
                    self.speak_s("Medication time has been recorded")
                

                elif 'news' in inp.lower() or 'live news updates' in inp.lower() or 'news' in inp.lower() or 'news updates' in inp.lower():
                        
                        
                    res = requests.get("http://api.mediastack.com/v1/news?access_key=2e9c2356f359740ff6a8d8fb48ccf9ea&languages=en&countries=in&categories={}".format(choice))
                    json_res = json.loads(res.text)
                    news = []
                    for i in json_res['data']:
                        if i['description']!="Subscribe now for your favourite magazines":
                            news.append(i['description'])
                    for i in range(3):
                        self.speak_s(news[i])

                    
                else:
                    results = model.predict([bag_of_words(inp, words)])
                    results_index = numpy.argmax(results)
                    tag = labels[results_index]
                    
                    for tg in data["intents"]:
                        if tg['intent'] == tag:

                            responses = tg['responses']

                            print(responses)
                            break
                    if responses in ["See you later","Have a nice day","Bye! `Come` back again soon."]:
                        os.remove('initial.txt')
                    
                    
                    
                    elif 'temperature' in responses or 'weather' in responses or 'weather report' in responses:
                        
                       # self.speak_s("which city's weather would you like to know?")
                        cities = ['mumbai','delhi','hyderabad','banglore','andhra pradesh']
                        
                        

                        api = "http://api.openweathermap.org/data/2.5/weather?q={}&appid=bd403e5f29e5d5809fe3b267b948ed09".format('hyderabad')
                        api_res = requests.get(api)
                        json_obj = json.loads(api_res.text)
                        tempk = int(json_obj['main']['temp'])
                        tempC = "{:.1f}".format(tempk-273.15)
                        self.speak_s("Weather in {} right now is {} degree celsius".format("hyderabad",tempC))
                    
                    else:
                        self.speak_s(random.choice(responses))
                    
            


startExecution = MainThread()
alarm = AlarmThread()
med = MedThread()


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Assistant()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui.pushButton.clicked.connect(self.close)
        self.startTask()
    
    def startTask(self):
        self.ui.movie = QtGui.QMovie("aaass.gif")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.label_2.setText("Listening...")
       
        startExecution.start()
        alarm.start()
        med.start()


    def change_text(self):
        self.ui.label_2.setStyleSheet("background-color: yellow;  border: 1px solid black;") 

    

   


app = QApplication(sys.argv)
assistant = Main()
assistant.show()
exit(app.exec_())

