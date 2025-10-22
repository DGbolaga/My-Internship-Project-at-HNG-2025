from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from operations import length, is_palindrome, unique_characters, word_count, sha256_hash, character_frequency_map, get_current_time
from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone
from sqlalchemy import Column, JSON
from models import StringRequest, filterRequest


class Hero(SQLModel, table=True):
    id: str = Field(primary_key=True)
    value: str = Field(index=True)
    length: int = Field(index=True)
    is_palindrome: bool = Field(index=True)
    unique_characters: int = Field(index=True)
    word_count: int = Field(index=True)
    sha256_hash: str = Field(index=True)
    character_frequency_map: dict | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()



# create string (POST)
@app.post("/strings")
async def create_string(request: StringRequest, session: SessionDep):
    """
        Recieves input string.
        Computes operation on string.
        Adds to database if not in database. 
        Raises error:   if string already in database (409 Conflict).
                        if invalid request body or missing value exist (400 Bad Request).
                        if value is not string (422 Unprocessable Entity).

    """
    value = request.value
    #check if value is of type string
    if type(value) != str:
        raise HTTPException(status_code=422, detail='Invalid data type for "value" (must be string)')
    
    #check if string is empty
    value = value.strip()
    print(value)
    if not value:
        raise HTTPException(status_code=400, detail='Invalid request body or missing "value" field')

    #check if string in system
    string_item_hash = sha256_hash(value)
    existing_item = session.exec(select(Hero).where(Hero.sha256_hash == string_item_hash)).first()
    if existing_item:
        raise HTTPException(status_code=409, detail='String already exists in the system')
   
    properties = {
        "length": length(value),
        "is_palindrome": is_palindrome(value),
        "unique_characters": unique_characters(value),
        "word_count": word_count(value),
        "sha256_hash": string_item_hash,
        "character_frequency_map": character_frequency_map(value)
    }

    # store current time as datetime object for easier manipulation later on
    hero = Hero(
        id = string_item_hash,
        value = value,
        length = properties["length"],
        is_palindrome = properties["is_palindrome"],
        unique_characters = properties["unique_characters"],
        word_count = properties["word_count"],
        sha256_hash = properties["sha256_hash"],
        character_frequency_map = properties["character_frequency_map"],
        created_at=get_current_time(),
    )

    session.add(hero)   
    session.commit()
    session.refresh(hero)
    
    return JSONResponse(
        content = {
            "id": hero.sha256_hash,
            "value": hero.value,
            "properties": {
                "length": hero.length,
                "is_palindrome": hero.is_palindrome,
                "unique_characters": hero.unique_characters,
                "word_count": hero.word_count,
                "sha256_hash": hero.sha256_hash,
                "character_frequency_map": hero.character_frequency_map,
            },
            # modify created_at to match specific format.
            "created_at": hero.created_at.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
        },
        status_code = status.HTTP_201_CREATED
    )

# get specific string (GET)
@app.get("/strings/{string_value}")
async def get_specific_string(string_value: str, session: SessionDep):
    """
        Returns string if in database - success response 200 OK
        Else - error response 404 Not Found
    """
    #check if string in system
    string_item_hash = sha256_hash(string_value)
    existing_item = session.exec(select(Hero).where(Hero.sha256_hash == string_item_hash)).first()
    if not existing_item:
        raise HTTPException(status_code=404, detail='String does not exist in the system')
   

    return JSONResponse(
        content = {
            "id": existing_item.sha256_hash,
            "value": existing_item.value,
            "properties": {
                "length": existing_item.length,
                "is_palindrome": existing_item.is_palindrome,
                "unique_characters": existing_item.unique_characters,
                "word_count": existing_item.word_count,
                "sha256_hash": existing_item.sha256_hash,
                "character_frequency_map": existing_item.character_frequency_map,
            },
            # modify created_at to match specific format.
            "created_at": existing_item.created_at.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
        },
        status_code = status.HTTP_200_OK
    )


# get all strings with filtering (GET)
@app.get("/strings")
async def get_string_by_filter(filter_requests: filterRequest):
    # is_palindrome: boolean (true/false)
    # min_length: integer (minimum string length)
    # max_length: integer (maximum string length)
    # word_count: integer (exact word count)
    # contains_character: string (single character to search for)
    """
        Fetches result based on filters. 
        returns formatted result if success (response 200 OK)
        else raises error (400 Bad Request) if it has invalid parameter values or type.
        
    """
    pass


# get all strings with filtering in natural language. (GET)
@app.get("/strings/filter-by-natural-language")
async def get_string_by_natural_lang_filter(query: str):
    """
        Takes natural language input as query.
        parses it into filtering parameters.
        returns formatted result if no error.
        else raises: 400 Bad Request - If unable to parse natural language query
                     422 Unprocessable Entity - If query parsed but resulted in conflicting filters
    """
    pass


# delete string (DELETE)
@app.delete("/strings/{string_value}")
async def delete_string(string_value: str, session: SessionDep):
    """
        deletes string from database if exist - success response 204
        else raises 404 Not Found - String does not exist in the system
    """
    #check if string in system
    string_item_hash = sha256_hash(string_value)
    existing_item = session.exec(select(Hero).where(Hero.sha256_hash == string_item_hash)).first()
    if not existing_item:
        raise HTTPException(status_code=404, detail='String does not exist in the system')
    
    session.delete(existing_item)
    session.commit()

    return JSONResponse(content={}, status_code=status.HTTP_204_NO_CONTENT)


