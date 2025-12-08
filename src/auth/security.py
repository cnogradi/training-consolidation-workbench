import os
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from neo4j import GraphDatabase
from pydantic import BaseModel
from typing import Optional, List

# Configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_REALM_URL", "http://localhost:8080/realms/workbench")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{KEYCLOAK_URL}/protocol/openid-connect/token")

class User(BaseModel):
    id: str
    email: str
    roles: List[str] = []

def get_db_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        # 1. Validate Token via JWKS
        jwks_url = f"{KEYCLOAK_URL}/protocol/openid-connect/certs"
        jwks_client = PyJWKClient(jwks_url)
        print(f"DEBUG: Validating token against JWKS: {jwks_url}")
        
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # DEBUG: Print token headers
        unverified_header = jwt.get_unverified_header(token)
        print(f"DEBUG: Token Header: {unverified_header}")

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience="account", # Default audience for Keycloak, adjust if needed
            options={"verify_aud": False} # Relax audience check for now if client ID varies
        )
        print(f"DEBUG: Token decoded successfully. User: {payload.get('sub')}")
        
        user_id = payload.get("sub")
        email = payload.get("email")
        realm_access = payload.get("realm_access", {})
        roles = realm_access.get("roles", [])
        
        if not user_id or not email:
            print("DEBUG: Missing user_id or email in payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user = User(id=user_id, email=email, roles=roles)
        
        # 2. Sync User to Neo4j
        sync_user_to_neo4j(user)
        
        return user
        
    except jwt.ExpiredSignatureError:
        print("DEBUG: Token Expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e:
        print(f"DEBUG: PyJWT Validation Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Auth Error (General): {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

def sync_user_to_neo4j(user: User):
    """
    Ensures the user exists in Neo4j.
    """
    driver = get_db_driver()
    try:
        with driver.session() as session:
            session.run(
                """
                MERGE (u:User {id: $id})
                SET u.email = $email,
                    u.last_login = datetime()
                """,
                id=user.id,
                email=user.email
            )
    except Exception as e:
        print(f"Failed to sync user to Neo4j: {e}")
    finally:
        driver.close()
