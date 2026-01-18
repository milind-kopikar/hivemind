import sys
import os
import random

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import SessionLocal
from app.models import Note, User

def test_rag_locally():
    db = SessionLocal()
    try:
        # 1. Ensure a test user exists
        user = db.query(User).filter_by(email="test@example.com").first()
        if not user:
            user = User(email="test@example.com", hashed_password="mock_password")
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Create a dummy embedding (768 dimensions for Gemini)
        mock_embedding = [random.uniform(-1, 1) for _ in range(768)]
        
        # 3. Save a note with the embedding
        print("Saving a note with a mock embedding...")
        new_note = Note(
            content="This is a test note about Photosynthesis.",
            user_id=user.id,
            embedding=mock_embedding
        )
        db.add(new_note)
        db.commit()

        # 4. Perform a similarity search
        print("Performing similarity search...")
        # L2 distance (<->), Cosine distance (<=>), or Inner product (<#>)
        # Here we use the Note.embedding.cosine_distance logic
        query_vector = mock_embedding # searching for itself should return it as #1
        
        results = db.scalars(
            select(Note)
            .order_by(Note.embedding.cosine_distance(query_vector))
            .limit(1)
        ).all()

        if results:
            print(f"Success! Found matching note: {results[0].content}")
        else:
            print("No results found.")

    except Exception as e:
        print(f"Testing failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_rag_locally()
