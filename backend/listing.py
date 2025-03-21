import json
import redis
from database_connect import connect_database
from models import Listings


# Configure Redis client
redis_client = redis.Redis(host='database-1.cjm0e6m6u6vm.us-east-2.rds.amazonaws.com', port=5432, decode_responses=True)
CACHE_EXPIRATION = 600  # Cache expiration time

# Define the listing categories
ALLOWED_CATEGORIES = ['Academic Materials', 'Textbooks', 'Technology', 'Furniture'] # We may add more

# Show the listings for a given category using Redis caching
def get_listings_by_category(category):

    # Throw error if a category doesn't exist
    if category not in ALLOWED_CATEGORIES:
        raise ValueError("Invalid category")

    cache_key = f"listings:{category}"
    cached = redis_client.get(cache_key)
    if cached:
        # Return cached listings as a Python list
        return json.loads(cached)

    # Get a new database connection
    conn = connect_database()
    try:
        # Use a context manager to automatically close the cursor
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, user_id, category, description, image_url FROM listings WHERE category = %s",
                (category,)
            )
            rows = cur.fetchall()
    finally:
        # Always close the connection after use
        conn.close()

    # Convert rows from the database into a list of dictionaries
    listings = [
        {
            "id": row[0],
            "user_id": row[1],
            "category": row[2],
            "description": row[3],
            "image_url": row[4]
        }
        for row in rows
    ]

    # Cache the listings result in Redis
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(listings))
    return listings

# Report a given listing
def report_listing(listing_id, reason, reported_by):

    conn = connect_database()
    try:
        with conn.cursor() as cur:
            # Check if the listing exists in the database
            cur.execute("SELECT id FROM listings WHERE id = %s", (listing_id,))
            if not cur.fetchone():
                raise ValueError("Listing not found")

            # Insert the report record into the reports table
            cur.execute(
                "INSERT INTO reports (listing_id, reason, reported_by) VALUES (%s, %s, %s)",
                (listing_id, reason, reported_by)
            )
            conn.commit()
            return {"message": "Report submitted"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Add a new item listing into the database
def create_listing(user_id, category, description, image_url=None):

    # Throw error if a category doesn't exist
    if category not in ALLOWED_CATEGORIES:
        raise ValueError("Invalid category")
    
    conn = connect_database()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO listings (user_id, category, description, image_url) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, category, description, image_url)
            )
            listing_id = cur.fetchone()[0]
            conn.commit()
            # Delete Redis cache to refresh category
            redis_client.delete(f"listings:{category}")
            return {"message": "Listing created", "id": listing_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Allow listing owner to update an existing listing
def edit_listing(listing_id, user_id, new_description=None, new_image_url=None):

    conn = connect_database()
    try:
        with conn.cursor() as cur:
            # Verify listing existence and ownership
            cur.execute(
                "SELECT category FROM listings WHERE id = %s AND user_id = %s",
                (listing_id, user_id)
            )
            row = cur.fetchone()
            if not row:
                raise ValueError("Listing not found or unauthorized")
            category = row[0]

            # Update the listing's description if a new one is provided
            if new_description is not None:
                cur.execute("UPDATE listings SET description = %s WHERE id = %s", (new_description, listing_id))
            # Update the listing's image_url if a new one is provided
            if new_image_url is not None:
                cur.execute("UPDATE listings SET image_url = %s WHERE id = %s", (new_image_url, listing_id))
            conn.commit()
            # Delete Redis cache to refresh category
            redis_client.delete(f"listings:{category}")
            return {"message": "Listing updated"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Allow listing owner to delete a listing
def delete_listing(listing_id, user_id):

    conn = connect_database()
    try:
        with conn.cursor() as cur:
            # Retrieve the category for cache invalidation
            cur.execute("SELECT category FROM listings WHERE id = %s AND user_id = %s", (listing_id, user_id))
            row = cur.fetchone()
            if not row:
                raise ValueError("Listing not found or unauthorized")
            category = row[0]
            # Delete the listing record
            cur.execute("DELETE FROM listings WHERE id = %s", (listing_id,))
            conn.commit()
            # Delete Redis cache to refresh category
            redis_client.delete(f"listings:{category}")
            return {"message": "Listing removed"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Allow user to view all listings owned
def view_user_listings(user_id):

    conn = connect_database()
    try:
        with conn.cursor() as cur:
            # Retrieve all listings for the given user_id
            cur.execute(
                "SELECT id, category, description, image_url FROM listings WHERE user_id = %s",
                (user_id,)
            )
            rows = cur.fetchall()
            listings = [
                {
                    "id": row[0],
                    "category": row[1],
                    "description": row[2],
                    "image_url": row[3]
                }
                for row in rows
            ]
            listing_count = len(listings)

            # Retrieve claims for each listing
            claims = []
            for listing in listings:
                cur.execute("SELECT claimed_by, message FROM claims WHERE listing_id = %s", (listing["id"],))
                claim_rows = cur.fetchall()
                if claim_rows:
                    claims.append({
                        "listing_id": listing["id"],
                        "claims": [{"claimed_by": c[0], "message": c[1]} for c in claim_rows]
                    })
        return {"listings": listings, "listing_count": listing_count, "claims": claims}
    finally:
        conn.close()

# Add a claim to a listing
def add_claim(listing_id, claimed_by, message=""):

    conn = connect_database()
    try:
        with conn.cursor() as cur:
            # Check if the listing exists
            cur.execute("SELECT id FROM listings WHERE id = %s", (listing_id,))
            if not cur.fetchone():
                raise ValueError("Listing not found")
            # Insert the claim into the claims table
            cur.execute(
                "INSERT INTO claims (listing_id, claimed_by, message) VALUES (%s, %s, %s)",
                (listing_id, claimed_by, message)
            )
            conn.commit()
            return {"message": "Claim added"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
