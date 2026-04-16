#### test_wikipedia.py
#### Description : Fonctions pour Tests automatisés Selenium sur Wikipédia

# import
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException

######

def lire_keywords(fichier):
    # but : créer une liste de mot-clefs à partir fichiers texte
    # arguments : le fichier texte

    with open(fichier, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def rechercher_wikipedia(driver, keyword):
    # but : rechercher un mot clef dans la page wikipedia en utilisant la barre de recherche
    # arguments : page wikipedia et mot clef du fichier

    # On ouvre la page d'accueil Wikipédia
    driver.get("https://fr.wikipedia.org/wiki")

    try:
        ######HomePage
        # On utilise la méthode CSS selector pour trouver la barre de recherche
        # on attend le chargement pendant 3s.
        champ_recherche = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='search']"))
        )

        # On saisit le mot-clé dans le champ
        champ_recherche.send_keys(keyword)

        # On attend que le bouton de recherche soit disponible
        button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form#searchform button"))
        )

        # On clique sur le bouton pour lancer la recherche
        button.click()

        ######Page du mot clef
        # On attend que le H1 soit présent = page bien chargée
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1#firstHeading"))
        )

        # On retourne l'URL de la page résultat
        return driver.current_url

    except TimeoutException:
        # Si un élément n'apparaît pas dans le délai prévu
        raise Exception(f"Page non chargée pour : {keyword}")


def tester_h1(driver, keyword):
    ######Page du mot clef
    # but : vérifier la présence d'une balise H1 non vide + présence mot clef dedans.
    # arguments : page wikipedia et mot clef du fichier"
    # utilisation du retour anticipé si on a la réponse.
    # pas de try except - simplification - on suppose H1 tjs présent

    # On crée un dictionnaire pour stocker les résultats du test.
    r = {}
    r['result'] = 'KO'
    r['message'] = ''

    # on récupère la (ou les) balise H1 dans la page
    balises_h1 = driver.find_elements(By.TAG_NAME, "h1")

    # cas 1 : H1 vide
    if len(balises_h1) == 0:
        r['message'] = 'H1 absent'
        return r

    # cas 2 : plusieurs balises H1
    elif len(balises_h1) > 1:
        r['message'] = 'H1 existant et multiple'
        return r

    # cas 3 : une balise h1
    else:
        # on récupère le text de la balise H1 en enlevant les espaces "inutiles"
        contenu = balises_h1[0].text.strip()

        # On vérifie que le contenu de H1
        # cas 1 : h1 est vide
        if contenu == '':
            r['message'] = 'H1 existant, unique et contenu vide'
            return r

        # cas 2 : h1 ne contient pas le bon mot clef
        elif keyword.lower() not in contenu.lower():
            r['message'] = 'H1 existant, unique et absence mot clef'
            return r

        else:
            r['result'] = 'OK'
            r['message'] = 'H1 existant, unique et contient le mot clef'
            return r

def tester_image(driver):
    ######Page du mot clef
    # but : vérifier la présence d'une image d'illustration.
    # infobox Wikipedia : encadré à droite du résumé - structure des pages spécifiques
    # arguments : page wikipedia

    # On crée un dictionnaire pour stocker les résultats du test. KO par défaut
    r = {}
    r['result'] = 'KO'
    r['message'] = ''

    try:
        # On attend qu'une image soit disponible dans l'infobox.
        # Webdriverwait garantit existence au moins une image.
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".infobox img"))
        )

        # On récupère toutes les images de l'infobox
        images = driver.find_elements(By.CSS_SELECTOR, ".infobox img")

        # On prend la première image - choix délibéré pour simplifier
        image = images[0]

        # On récupère les attributs src, alt et aria_hidden
        # src : source image
        # alt : description image  - vide si image décorative
        # aria : ignoré ou lu par lecteur d'écran
        src = image.get_attribute("src")
        alt = image.get_attribute("alt")
        aria_hidden = image.get_attribute("aria-hidden") # retourne str

        #test fonctionnel
        # cas 1 : existence des 2 attributs obligatoires
        if src is None or alt is None :
            raise AssertionError("src ou alt inexistant")

        # cas 2 : src non vide
        assert src.strip() != '', "src vide"

        #test accessibilité
        # cas 3 : aria-hidden absent
        assert aria_hidden is not None, "aria-hidden absent"

        # cas 4 : image décrite correctement (avec description un peu étoffée) et cachée
        assert not (len(alt.strip()) > 3 and aria_hidden.lower() == "true"), "contradiction : image importante cachée"

        # cas 5 : image non décrite et visible
        assert not (alt.strip() == '' and aria_hidden.lower() == "false"), "contradiction : alt vide et aria-hidden fausse"


        # rapport
        r['result'] = 'OK'
        r['message'] = 'image présent avec bon attribut src - alt + aria-hidden cohérent '
        return r

    except AssertionError as e:
        # Image trouvée mais attributs invalides
        r['message'] = f'Assertion error: {(e)}'
        return r

    except TimeoutException:
        # Aucune image chargée dans l'infobox
        r['message'] = "temps dépassé - pas d'image trouvé dans infobox"
        return r
