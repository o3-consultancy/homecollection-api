from app.db.mongo import MongoClientWrapper

_db = None


def get_db() -> MongoClientWrapper:
    global _db
    if _db is None:
        _db = MongoClientWrapper()
    return _db
