import json

def getIcons():
    with open('json/icons.json') as file:
        icons = json.load(file)
    file.close()

    return icons

def getUsers():
    with open('json/users.json') as file:
        users = json.load(file)
    file.close()
    
    return users

def saveUsers(users=None):
    with open('json/users.json', 'w') as file:
        file.write(json.dumps(users,indent=4))
    file.close()