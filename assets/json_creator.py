import json

def create_JSON (url, name): #Создает JSON file
    data = {
        "web-site": f"{url}",
        "doors": []
    }
    with open(f"results/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)    
    return

def add_to_JSON (name, price, feauters, photos_url, url, site_name): #Добавляет объект door в массив doors
    door_feauters = [{k:v} for k,v in feauters]
    door_photos = [{"local-url": local_value, "global-url": global_value} for local_value, global_value in photos_url]
    
    new_door = {
        "door-name": f"{name}",
        "door-price": f"{price}",
        "door-features": door_feauters,
        "door-photos": door_photos,
        "door-url": f"{url}"
    }


    with open(f"results/{site_name}.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data["doors"].append(new_door)

    with open(f"results/{site_name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return
