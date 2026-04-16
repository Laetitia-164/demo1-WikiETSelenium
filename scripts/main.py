####  main.py
#### Description : Fonctions pour Tests automatisés Selenium sur Wikipédia
#### rapport = liste de dicos → pandas DataFrame → CSV

# import
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os

# mes fonctions
from test_wikipedia import lire_keywords, rechercher_wikipedia, tester_h1, tester_image

# mes chemins
# Chemin vers keywords.txt dans le dossier données/
FICHIER_KEYWORDS = os.path.join(os.path.dirname(__file__), '..', 'données', 'keywords.txt')
# Chemin vers le dossier résultats/
DOSSIER_RESULTATS = os.path.join(os.path.dirname(__file__), '..', 'résultats')

######

def main():

    # Lecture des mots-clés
    keywords = lire_keywords(FICHIER_KEYWORDS)
    print(f"Il y a {len(keywords)} mots-clés chargés qui sont : {keywords}")

    # Lancement du navigateur
    # Au besoin, j'installe le driver, je l'ouvre et j'agrandis la fenêtre au max (voir barre recherche)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Initiation du rapport :
    # Une liste de dictionnaires → un dico = une ligne CSV
    # Compteur test_id — numéro unique par ligne pour indexer résultats
    rapport = []
    test_id = 1

    # lancement du test
    # pour chaque mot clef de la liste
    for keyword in keywords:

        # Cadençage anti-détection bot
        time.sleep(2)

        print(f"\n Recherche : {keyword}")

        ########## Navigation Web
        # try catch ds fn : erreur technique / ds main gestion flux
        try:
            url = rechercher_wikipedia(driver, keyword)
            result = 'OK'
            message = 'Page chargée'
            print(f"   URL : {url}")

        except Exception as e:
            # échec navigation
            url = 'non trouvé'
            result = 'KO'
            message = f"Navigation échouée : {e}"
            print(message, file=sys.stderr) #erreur std, sort ne rouge sur console

        # rapport test navigation
        rapport.append({
            'test_id': test_id,
            'keyword': keyword,
            'url': url,
            'test_type': 'Navigation',
            'test_name': 'chargement de la page internet',
            'result': result,
            'message': message
        })

        #passage itération suivante
        test_id += 1
        if result == 'KO': # si pb je passe au suivant
            continue

        ########## H1
        # "test h1"
        resultat_h1 = tester_h1(driver, keyword)

        # rapport H1
        # Puis on l'accroche au grand rapport — exactement comme ton cours
        r_h1 = {}
        r_h1['test_id'] = test_id
        r_h1['keyword'] = keyword
        r_h1['url'] = url
        r_h1['test_type'] = 'H1'
        r_h1['test_name'] = 'H1 précence ou absence'
        r_h1['result'] = resultat_h1['result']
        r_h1['message'] = resultat_h1['message']
        rapport.append(r_h1)

        print(f"   H1 -> {resultat_h1['result']}, {resultat_h1['message']}")
        test_id += 1

        # "test image"
        resultat_image = tester_image(driver)

        r_img = {}
        r_img['test_id'] = test_id
        r_img['keyword'] = keyword
        r_img['url'] = url
        r_img['test_type'] = 'image'
        r_img['test_name'] = "validation de l'image"
        r_img['result'] = resultat_image['result']
        r_img['message'] = resultat_image['message']
        rapport.append(r_img)

        print(f"   IMAGE -> {resultat_image['result']}, {resultat_image['message']}")
        test_id += 1

        time.sleep(2)

    #Fermeture navigateur
    driver.quit()

    # Génération CSV avec pandas
    # liste de dicos → DataFrame → CSV
    df = pd.DataFrame(data=rapport)

    # Nom du fichier avec horodatage
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nom_csv = f"resultats_{date_str}.csv"
    chemin_csv = os.path.join(DOSSIER_RESULTATS, nom_csv)

    df.to_csv(chemin_csv, index=False, encoding='utf-8-sig')

    print(f"\n Tests terminés.")
    print(f" Résultats : {chemin_csv}")


########### LANCEMENT
if __name__ == '__main__':
    main()