from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import io, json
from typing import List
from pydantic import BaseModel
import hashlib
import uuid

def hash_password(password):
        h = hashlib.new("sha3_512")
        h.update(password.encode("utf-8"))
        return h.hexdigest()
class User:
        Id: int
        Username: str
        Password: str 
        Uuid: str    

        def __init__(self, id, username, password, uuid):
                self.Id = id
                self.Username = username
                self.Password = password
                self.Uuid = uuid

class UpdateUser(BaseModel):
        Password: str

class NewUser(BaseModel):
        Username: str
        Password: str

app = FastAPI()

@app.get("/user")
def read_root():
        users = getUsersFromJson()
        json_compatible_item_data = jsonable_encoder(users)
        return JSONResponse(content=json_compatible_item_data)               


@app.post("/login")
def login(loginuser: NewUser):
        users = getUsersFromJson()
        for user in users:
                if user.Username == loginuser.Username and user.Password == hash_password(loginuser.Password + user.Uuid):
                        return JSONResponse(user.Id)
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/user/{user_id}")
def read_root(user_id: int):
        users = getUsersFromJson()
        
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
        users.append(User(new_id,newuser.Username,newuser.Password,user_uuid))
        writeUsersToJson(users)
        return JSONResponse("")


def getUsersFromJson():
        with io.open('data.txt', 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

        users: List[User] = []
        for entry in data:
                users.append(User(entry["Id"], entry["Username"], entry["Password"], entry["Uuid"]))

        return users

def writeUsersToJson(users):
        json_compatible_item_data = jsonable_encoder(users)
        with io.open('data.txt', 'w', encoding='utf-8') as f:
                f.write(str(json_compatible_item_data).replace("'", '"'))

        return json_compatible_item_data
