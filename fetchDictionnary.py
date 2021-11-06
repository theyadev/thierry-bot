import requests
import json

def writeJSON(list, path: str = "./words.json") -> bool:
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(list, file) 
            return True
    except:
        return False

def fetch():
    data = requests.get("https://frenchwordsapi.herokuapp.com/api/Word").json()

    print("L'api a reussis a chargé (jure wallah)")

    words_list = []
    for word_obj in data:
        words_list.append(word_obj["WordName"])

    print("La liste s'est remplie !!!!")

    
    res = writeJSON(words_list)

    if res:
        print("Ecriture : Reussi")
    else:
        print("Ecriture : Erreur")
    

if __name__ == "__main__":
    fetch()