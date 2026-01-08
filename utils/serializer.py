from bson import ObjectId

def serialize_user(user):
    if not user:
        return None

    user["_id"] = str(user["_id"])
    return user
