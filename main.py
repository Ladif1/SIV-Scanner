from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from string import ascii_uppercase as alpha
from codecs import open as open_encoding
from time import sleep

# ------------------- #

# Début/Fin
START = "FF-123-ZX"
END   = "FF-124-AB"

# Sauvegarder les résultats dans logs.txt
SAVE = True

# Cacher la fenêtre
HIDE = True

# ------------------- #

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
    options = webdriver.ChromeOptions()

    if HIDE:
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")

    driver = webdriver.Chrome("chromedriver", options=options)
    openAndAcceptCookies(driver)

    plate = START

    while plate != nextPlate(END):
        infos = searchPlate(driver, plate)

        if infos != -1:
            log = f"[{plate}] Plaque trouvée : {infos}"
        else:
            log = f"[{plate}] Plaque non attribuée"

        if SAVE:
            with open_encoding("logs.txt", "a+", "utf-8") as f:
                f.write(log + "\n")

        plate = nextPlate(plate)

        print(log)
