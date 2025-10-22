from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from utilities.operations import length, is_palindrome, unique_characters, word_count, sha256_hash, character_frequency_map, get_current_time
from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone
from sqlalchemy import Column, JSON
from utilities.models import StringRequest, filterRequest
from utilities.natural_language_parser import parse_natural_language_query
import os
from dotenv import load_dotenv


# Load environment variables 
load_dotenv()



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


# Configure Database Connection
# - Get URL from environment variable (for deploying on PostgreSQL)
# - Fallback to SQLite (to easily run locally)
database_url = os.getenv(
    "DATABASE_URL", 
    "sqlite:///database.db" # Default SQLite connection
)


connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}
engine = create_engine(database_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

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

    #pydantic handles type check (422 Unprocessable Entity)
    
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
        unique_characters = properties["unique_characters"] ,
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


# get all strings with filtering (GET)
@app.get("/strings")
async def get_string_by_filter(filter_requests: filterRequest = Depends(), session: Session = Depends(get_session)):

    """
        Fetches result based on filters. 
        returns formatted result if success (response 200 OK)
        raises error :(400 Bad Request) if it has invalid parameter values or type.
                      (400 Bad Request) if min_length > max_length
    """
    filters = {k: v for k, v in vars(filter_requests).items() if v is not None}
    
    # raise error if conflicting query: min length is greater than max length
    if (filters.get("min_length") and filters.get("max_length") and (filters.get("min_length") > filters.get("max_length"))):
        raise HTTPException(status_code=400, detail='min_length cannot be greater than max_length')

    query = select(Hero)
    # list filters
    if filters.get("is_palindrome") is not None:
        query = query.where(Hero.is_palindrome == filters["is_palindrome"])
    if filters.get("min_length") is not None:
        query = query.where(Hero.length >= filters["min_length"])
    if filters.get("max_length") is not None:
        query = query.where(Hero.length <= filters["max_length"])
    if filters.get("word_count") is not None:
        query = query.where(Hero.word_count == filters["word_count"])
    if filters.get("contains_character") is not None:
        query = query.where(Hero.value.contains(filters["contains_character"]))
   
    filtered_strings = session.exec(query).all()
    
    formatted_filtered_strings = []
    for hero in filtered_strings:
        formatted_filtered_strings.append({
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
        })

    return JSONResponse(
        content = {
            "data":formatted_filtered_strings,
            "count": len(formatted_filtered_strings),
            "filters_applied": filters,
        },
        status_code = status.HTTP_200_OK
    )


# get all strings with filtering in natural language. (GET)
@app.get("/strings/filter-by-natural-language")
async def get_string_by_natural_lang_filter(query: str = Query(...), session: Session = Depends(get_session)):
    """
        Takes natural language input as query.
        Parses it into filtering parameters using parsing logic.
        Returns formatted result if no error.
        Raises:
            400 Bad Request - If unable to parse natural language query
            422 Unprocessable Entity - If query parsed but resulted in conflicting filters
    """
    # Preserve the original text for output
    original_query = query
    filters = parse_natural_language_query(query)
    
    db_query = select(Hero)
    if filters.get("is_palindrome") is not None:
        db_query = db_query.where(Hero.is_palindrome == filters["is_palindrome"])
    if filters.get("min_length") is not None:
        db_query = db_query.where(Hero.length >= filters["min_length"])
    if filters.get("max_length") is not None:
        db_query = db_query.where(Hero.length <= filters["max_length"])
    if filters.get("word_count") is not None:
        db_query = db_query.where(Hero.word_count == filters["word_count"])
    if filters.get("contains_character") is not None:
        db_query = db_query.where(Hero.value.contains(filters["contains_character"]))

    filtered_strings = session.exec(db_query).all()
    
    formatted_filtered_strings = []
    for hero in filtered_strings:
        formatted_filtered_strings.append({
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
            "created_at": hero.created_at.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
        })

    return JSONResponse(
        content={
            "data": formatted_filtered_strings,
            "count": len(formatted_filtered_strings),
            "interpreted_query": {
                "original": original_query,
                "parsed_filters": filters
            }
        },
        status_code=status.HTTP_200_OK
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


# delete string (DELETE)
@app.delete("/strings/{string_value}")
async def delete_string(string_value: str, session: SessionDep):
    """
        deletes string from database if exist
        returns nothing - success response 204
        raises 404 Not Found - If string does not exist in the system
    """
    #check if string in system
    string_item_hash = sha256_hash(string_value)
    existing_item = session.exec(select(Hero).where(Hero.sha256_hash == string_item_hash)).first()
    if not existing_item:
        raise HTTPException(status_code=404, detail='String does not exist in the system')
    
    session.delete(existing_item)
    session.commit()

    return JSONResponse(content={}, status_code=status.HTTP_204_NO_CONTENT)

