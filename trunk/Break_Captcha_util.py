#!coding: utf-8
from svm import *
import os, sys
import Image, time

import psyco
psyco.full()

from Preprocess import preprocess_captcha
from Preprocess import load_image

#AUTRES PARAMETRES A LA FIN DU FICHIER !
VERBOSE = 0
STARTING_POSITION_STEP = 1


def load_model(chemin, parent=None, fichier = ""):
    if not os.path.isfile(chemin):
        print 'The specified model file: \"'+chemin +'\" was not found. Aborting.'
        sys.exit(1)
    else:
        print "Loading model..."
        if parent:
            parent.path_model.SetLabel("Loading model...")
        model = svm_model(chemin)
        print "Model successfully loaded."
        if parent:
            parent.path_model.SetLabel(fichier)
            parent.model = model
            parent.model_selected = True
    return model


def preprocess_captcha_part(file, parent = None):
    #Fait l'extraction � partir de la starting position, sur une largeur length, et fait �ventuellement du preprocessing.
    
    dest = preprocess_captcha(file)
    
    data = Image.open(dest)
    data1 = data.point(lambda i: i /255.)
    
    if parent:
        w, h = data.size
        data = data.convert('RGB').resize((parent.zoom*w, parent.zoom*h))

    return data1, data
    
    

def predict(model, im, liste_probas):
    data = list(im.getdata())
    prediction = model.predict(data)
    probability = model.predict_probability(data)  
    
    print chr(65+int(prediction)), max(probability[1].values())
    liste_probas.append(probability[1])
    
    if VERBOSE:
        print probability
    
    return chr(65+int(prediction)), max(probability[1].values())
    
    
    
def break_captcha(model, captcha, size=38, parent = None):

    if not parent:
        print """
        ##############################################################################
        ############################    BREAKING CAPTCHA    ################################
        ##############################################################################
        """

    liste_probas = []
    
    for starting_pos in range(0, 127-31,STARTING_POSITION_STEP):
        if parent:
            if not parent.actif:
                return
        preprocessed_captcha_part = captcha.crop((starting_pos, 0, starting_pos+38, 31))
        preprocessed_captcha_part.load()
        
        for j in range(preprocessed_captcha_part.size[1]):
            for i in range((38-size)/2+1):
                preprocessed_captcha_part.putpixel((i,j), 1)
            for i in range(38 - (38-size)/2, 38):
                preprocessed_captcha_part.putpixel((i,j), 1)
        
        prediction, max_score = predict(model, preprocessed_captcha_part, liste_probas)

        if parent:
            w, h = preprocessed_captcha_part.size
            preprocessed_captcha_part = preprocessed_captcha_part.point(lambda e : e*255).convert('RGB').resize((parent.zoom*w, parent.zoom*h))
            parent.setResult(preprocessed_captcha_part, prediction, max_score)
            parent.Update()
            parent.Fit()
            time.sleep(0.5)



if __name__ == "__main__":
    MODEL_FILE = "model.svm"
    CAPTCHA_FILE = os.path.join("Captchas", 'Image011.jpg')
    LENGTH_CAPTCHA_PART = 31
    
    model = load_model(MODEL_FILE)
    
    captcha, beau_captcha = preprocess_captcha_part(CAPTCHA_FILE)
    break_captcha(model, captcha, size=38)
    raw_input()



