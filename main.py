from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import io, json
from typing import List
from pydantic import BaseModel
import hashlib
import uuid
admin_level = 1
def hash_password(password):
        h = hashlib.new("sha3_512")
        h.update(password.encode("utf-8"))
        return h.hexdigest()
class User:
        Id: int
        Username: str
        Password: str 
        Uuid: str    
        Level: int

        def __init__(self, id, username, password, uuid, level):
                self.Id = id
                self.Username = username
                self.Password = password
                self.Uuid = uuid
                self.Level = level
class SafeUser:
        Id: int
        Username: str
        Level: int

        def __init__(self, id, username, level):
                self.Id = id
                self.Username = username
                self.Level = level
class UpdateUser(BaseModel):
        Password: str
class Admin(BaseModel):
        Id: int
        Username: str
        Level: int

class NewUser(BaseModel):
        Username: str
        Password: str
        Level: int = 0

app = FastAPI()

@app.get("/user")
def read_root():
        users = getSafeUsersFromJson()
        json_compatible_item_data = jsonable_encoder(users)
        return JSONResponse(content=json_compatible_item_data)               


@app.post("/login")
def login(loginuser: NewUser):
        users = getUsersFromJson()
        for user in users:
                if user.Username == loginuser.Username and user.Password == hash_password(loginuser.Password + user.Uuid):
                        return JSONResponse(user.Id)
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/user/admin")
def read_admin():
        users = getSafeUsersFromJson()

        for user in users:
                if user.Level == admin_level:
                        json_compatible_item_data = jsonable_encoder(user)
                        return JSONResponse(content=json_compatible_item_data)
        raise HTTPException(status_code=404, detail="Admin not found")

@app.get("/user/{user_id}")
def read_root(user_id: int):
        users = getSafeUsersFromJson()
        
        for user in users:
                if (user.Id == user_id):
                        json_compatible_item_data = jsonable_encoder(user)
                        return JSONResponse(content=json_compatible_item_data)                

        raise HTTPException(status_code=404, detail="Item not found")

@app.put("/user/{user_id}")
def update_user(user_id: int, updateUser: UpdateUser):
        users = getUsersFromJson()

        for user in users:
                if (user.Id == user_id):
                        if user.Password == hash_password(updateUser.Password + user.Uuid):
                                raise HTTPException(status_code=400, detail="Password is the same")
                        else:
                                user.Password = hash_password(updateUser.Password + user.Uuid)

                        writeUsersToJson(users)
                        return JSONResponse("")

        raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/user/{user_id}")
def delete_user(user_id: int):
        users = getUsersFromJson()

        for user in users:
                if (user.Id == user_id):
                        users.remove(user)
                        writeUsersToJson(users)
                        return JSONResponse("")
        raise HTTPException(status_code=404, detail="Item not found")
        

        

@app.post("/user")
def write_root(newuser: NewUser):
        users = getUsersFromJson()
        for user in users:
                if user.Username == newuser.Username:
                        raise HTTPException(status_code=404, detail="Username already exists")
        new_id = max([user.Id for user in users], default=0) + 1
        user_uuid = str(uuid.uuid4())
        newuser.Password = newuser.Password + user_uuid
        newuser.Password = hash_password(newuser.Password)
        if newuser.Username == "admin":
                newuser.Level = 1
        else:
                newuser.Level = 0
        users.append(User(new_id,newuser.Username,newuser.Password,user_uuid,newuser.Level))
        writeUsersToJson(users)
        return JSONResponse("")


def getUsersFromJson():
        with io.open('data.txt', 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

        users: List[User] = []
        for entry in data:
                users.append(User(entry["Id"], entry["Username"], entry["Password"], entry["Uuid"], entry["Level"]))

        return users

def getSafeUsersFromJson():
        with io.open('data.txt', 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
        
        users: List[SafeUser] = []
        for entry in data:
                users.append(SafeUser(entry["Id"], entry["Username"], entry["Level"]))
        return users                             

def writeUsersToJson(users):
        json_compatible_item_data = jsonable_encoder(users)
        with io.open('data.txt', 'w', encoding='utf-8') as f:
                f.write(str(json_compatible_item_data).replace("'", '"'))

        return json_compatible_item_data
