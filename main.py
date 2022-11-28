from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from string import ascii_uppercase as alpha
from codecs import open as open_encoding
from time import sleep

# ------------------- #

START = "AA-001-AA"
END = "FF-999-ZZ"
SAVE = True

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


if __name__ == "__main__":
    options = webdriver.ChromeOptions()

    options.add_argument("headless")
    options.add_argument("window-size=1920x1080")
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome("chromedriver", options=options)
    openAndAcceptCookies(driver)

    for l1 in alpha[alpha.index(START[0]):alpha.index(END[0])]:
        for l2 in alpha[alpha.index(START[1]):alpha.index(END[1])]:
            for x in range(int(START[3]), int(END[3])):
                for y in range(int(START[4]), int(END[4])):
                    for z in range(int(START[5]), int(END[5])):
                        for l3 in alpha[alpha.index(START[7]):alpha.index(END[7])]:
                            for l4 in alpha[alpha.index(START[8]):alpha.index(END[8])]:
                                plate = f"{l1}{l2}-{x}{y}{z}-{l3}{l4}"
                                infos = searchPlate(driver, plate)

                                if infos != -1:
                                    log = f"[{plate}] Plaque trouvée : {infos}"
                                else:
                                    log = f"[{plate}] Plaque non attribuée"

                                if SAVE:
                                    with open_encoding("logs.txt", "a+", "utf-8") as f:
                                        f.write(log + "\n")

                                print(log)
