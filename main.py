from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from string import ascii_uppercase as alpha
from codecs import open as open_encoding
from time import sleep

# ------------------ [SETTINGS] ------------------ #

# Début/Fin
START = "AB-123-CD"
END   = "EF-456-GH"

# Rechercher une marque (laisser vide sinon)
SEARCH = "suzuki"

# Sauvegarder les résultats dans logs.txt
SAVE = False

# Cacher la fenêtre
HIDE = True

# Faire des statistiques après le scan
STATS = True

# ------------------------------------------------ #

URL = "https://www.piecesautosaintlaurent.com/categories-pieces"
TIMEOUT = 10


def openAndAcceptCookies(d):
    d.get(URL)
    d.maximize_window()
    WebDriverWait(d, TIMEOUT).until(EC.presence_of_element_located((By.ID, "acb-accept-all-button"))).click()
    sleep(1)


def searchPlate(d, p):
    WebDriverWait(d, TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, "p_immatriculation")))

    recherche = d.find_element(By.CLASS_NAME, "p_immatriculation")
    recherche.clear()
    recherche.send_keys(p)
    recherche.send_keys(Keys.ENTER)

    WebDriverWait(d, TIMEOUT).until(
        EC.any_of(
            EC.presence_of_element_located((By.CLASS_NAME, "cible")),
            EC.text_to_be_present_in_element((By.CLASS_NAME, "alert"), 'Nous n\'avons pas trouvé')
        )
    )

    if len(d.find_elements(By.CLASS_NAME, "cible")) > 0:
        modele = d.find_elements(By.CLASS_NAME, "cible")[0].text[22:]
        d.execute_script("var e = document.getElementsByClassName('cible')[0]; e.parentNode.removeChild(e);")

        if not modele.startswith("."):
            return modele

    return -1


def nextLetter(l):
    index = alpha.index(l)

    if index == 26:
        return alpha[1]

    return alpha[index + 1]


def nextNumber(n):
    n = int(n)

    if n == 9:
        return str(1)

    return str(n + 1)


def nextPlate(p):
    p = list(p)

    if p[8] != 'Z':
        p[8] = nextLetter(p[8])
    elif p[7] != 'Z':
        p[7], p[8] = nextLetter(p[7]), 'A'
    elif p[5] != '9':
        p[5], p[7], p[8] = nextNumber(p[5]), 'A', 'A'
    elif p[4] != '9':
        p[4], p[5], p[7], p[8] = nextNumber(p[4]), '0', 'A', 'A'
    elif p[3] != '9':
        p[3], p[4], p[5], p[7], p[8] = nextNumber(p[3]), '0', '0', 'A', 'A'
    elif p[1] != 'Z':
        p[1], p[3], p[4], p[5], p[7], p[8] = nextLetter(p[1]), '0', '0', '0', 'A', 'A'
    elif p[0] != 'Z':
        p[0], p[1], p[3], p[4], p[5], p[7], p[8] = nextLetter(p[0]), 'A', '0', '0', '0', 'A', 'A'

    return "".join(p)


if __name__ == "__main__":
    print("[SIV Scanner By Razen]\n----------------------------------------\n")

    options = webdriver.ChromeOptions()

    if HIDE:
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")

    driver = webdriver.Chrome("chromedriver", options=options)
    openAndAcceptCookies(driver)

    logs = []
    matches = []
    plate = START

    while plate != nextPlate(END):
        infos = searchPlate(driver, plate)

        if infos != -1:
            log = f"[{plate}] Plaque attribuée : {infos}"

            if SEARCH and SEARCH.lower() in infos.lower():
                matches.append((plate, infos))

        else:
            log = f"[{plate}] Plaque non attribuée"

        logs.append(log)
        print(log)

        plate = nextPlate(plate)

    if SAVE:
        with open_encoding("logs.txt", "w", "utf-8") as save:
            for log in logs:
                save.write(log + "\n")

    if STATS:
        print("\n[Statistiques]\n----------------------------------------\n")

        stats = dict()
        count = 0

        for log in logs:
            splitted = log.split()

            if splitted[2] != "non":
                marque = splitted[4]
                count += 1

                if marque not in stats:
                    stats[marque] = 1
                else:
                    stats[marque] = stats[marque] + 1

        sorted_stats = dict(reversed(sorted(stats.items(), key=lambda item: item[1])))

        for k, v in sorted_stats.items():
            print(f"\u2022  {round((v / count) * 100, 2)} %  {k} ({v})")

        print(f"\nTotal : {count} véhicules identifiés")

    if SEARCH:
        print("\n[Recherche]\n----------------------------------------\n")

        if not matches:
            print("Aucun résultat.")
        else:
            print(f"{len(matches)} résultats :\n")

            for match in matches:
                print(f"\u2022 [{match[0]}] {match[1]}")
