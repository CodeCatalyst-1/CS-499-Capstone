import logging
from pymongo import MongoClient, ASCENDING, errors as pymongo_errors
from pymongo.errors import PyMongoError, BulkWriteError
from urllib.parse import quote_plus
from typing import Any

# Module-level logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class AnimalShelter:
    """
    CRUD interface for the Austin Animal Center (AAC) MongoDB collection.

    Enhancements (Milestone Four - Databases):
      - Indexes are created at startup on the fields most queried by the
        dashboard (animal_type, breed, sex_upon_outcome,
        age_upon_outcome_in_weeks).  Compound indexes support the rescue
        filter queries directly, reducing full-collection scans.
      - aggregate_outcomes() exposes a MongoDB aggregation pipeline so the
        dashboard can obtain grouped counts without pulling every document
        into Python.
      - get_distinct() returns unique values for a given field, useful for
        populating dropdown menus from live database content.
      - bulk_import() inserts many documents at once with ordered=False so a
        single duplicate does not abort the entire batch; the method reports
        how many records were inserted versus skipped.
    """

    # Fields indexed individually for single-field queries
    SINGLE_INDEXES = [
        "animal_type",
        "breed",
        "sex_upon_outcome",
        "age_upon_outcome_in_weeks",
        "outcome_type",
    ]

    # Compound indexes that mirror the dashboard rescue filter queries
    COMPOUND_INDEXES = [
        [("animal_type", ASCENDING), ("breed", ASCENDING), ("sex_upon_outcome", ASCENDING)],
        [("animal_type", ASCENDING), ("age_upon_outcome_in_weeks", ASCENDING)],
    ]

    def __init__(
        self,
        user: str,
        passwd: str,
        host: str = "nv-desktop-services.apporto.com",
        port: int = 30091,
        db: str = "AAC",
        collection: str = "animals",
    ) -> None:
        """
        Connect to MongoDB and initialise the collection.
        Indexes are created (or verified) immediately after a successful
        connection so every subsequent query benefits from them.
        """
        try:
            user_enc = quote_plus(user)
            passwd_enc = quote_plus(passwd)
            uri = (
                f"mongodb://{user_enc}:{passwd_enc}"
                f"@{host}:{port}/{db}?authSource=admin"
            )
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            # Verify the connection is alive before proceeding
            self.client.admin.command("ismaster")
            self.database = self.client[db]
            self.collection = self.database[collection]
            logger.info("Connected to MongoDB as user '%s'.", user)
            self._ensure_indexes()
        except PyMongoError as e:
            logger.error("Connection or authentication failed: %s", e)
            self.client = None

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def _ensure_indexes(self) -> None:
        """
        Create single-field and compound indexes if they do not already exist.
        Using create_index() with background=True means the operation does not
        block reads or writes while the index is being built.
        """
        if not self.client:
            return
        try:
            for field in self.SINGLE_INDEXES:
                self.collection.create_index(
                    [(field, ASCENDING)],
                    name=f"idx_{field}",
                    background=True,
                )
                logger.info("Index ensured: idx_%s", field)

            for i, key_list in enumerate(self.COMPOUND_INDEXES):
                index_name = "idx_compound_" + "_".join(k for k, _ in key_list)
                self.collection.create_index(
                    key_list,
                    name=index_name,
                    background=True,
                )
                logger.info("Compound index ensured: %s", index_name)

        except PyMongoError as e:
            logger.error("Index creation failed: %s", e)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, data: dict) -> bool:
        """
        Insert a single document.  Returns True when the write is acknowledged.
        """
        if not self.client:
            logger.warning("create() called but client is not connected.")
            return False
        if not isinstance(data, dict) or not data:
            logger.error("create() requires a non-empty dict.")
            return False
        try:
            result = self.collection.insert_one(data)
            return result.acknowledged
        except PyMongoError as e:
            logger.error("create() failed: %s", e)
            return False

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def read(self, query: dict, projection: dict | None = None) -> list:
        """
        Return documents matching query.  An optional projection dict can
        limit which fields are returned, reducing network transfer.
        """
        if not self.client:
            logger.warning("read() called but client is not connected.")
            return []
        if not isinstance(query, dict):
            logger.error("read() requires a dict query.")
            return []
        try:
            cursor = self.collection.find(query, projection)
            return list(cursor)
        except PyMongoError as e:
            logger.error("read() failed: %s", e)
            return []

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, query: dict, update_data: dict) -> int:
        """
        Apply $set update to all documents matching query.
        Returns the number of documents modified.
        """
        if not self.client:
            logger.warning("update() called but client is not connected.")
            return 0
        if not isinstance(query, dict) or not isinstance(update_data, dict):
            logger.error("update() requires dict arguments.")
            return 0
        try:
            result = self.collection.update_many(query, {"$set": update_data})
            return result.modified_count
        except PyMongoError as e:
            logger.error("update() failed: %s", e)
            return 0

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, query: dict) -> int:
        """
        Delete all documents matching query.
        Returns the number of documents deleted.
        """
        if not self.client:
            logger.warning("delete() called but client is not connected.")
            return 0
        if not isinstance(query, dict):
            logger.error("delete() requires a dict query.")
            return 0
        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as e:
            logger.error("delete() failed: %s", e)
            return 0

    # ------------------------------------------------------------------
    # Aggregation pipeline
    # ------------------------------------------------------------------

    def aggregate_outcomes(self, match: dict | None = None) -> list:
        """
        Run an aggregation pipeline that groups documents by outcome_type and
        counts each group.  An optional match stage filters documents before
        grouping, which keeps the pipeline efficient because MongoDB can apply
        an index on the match fields before touching any other data.

        Returns a list of dicts with keys 'outcome_type' and 'count'.

        Example:
            shelter.aggregate_outcomes({"animal_type": "Dog"})
            # [{"outcome_type": "Adoption", "count": 1423}, ...]
        """
        if not self.client:
            logger.warning("aggregate_outcomes() called but client is not connected.")
            return []
        pipeline: list[dict] = []
        if match:
            pipeline.append({"$match": match})
        pipeline += [
            {"$group": {"_id": "$outcome_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$project": {"_id": 0, "outcome_type": "$_id", "count": 1}},
        ]
        try:
            return list(self.collection.aggregate(pipeline))
        except PyMongoError as e:
            logger.error("aggregate_outcomes() failed: %s", e)
            return []

    # ------------------------------------------------------------------
    # Distinct values
    # ------------------------------------------------------------------

    def get_distinct(self, field: str, query: dict | None = None) -> list:
        """
        Return the sorted list of unique values for field, optionally
        filtered by query.  Useful for populating dropdown menus directly
        from live database content rather than hard-coding options.

        Example:
            shelter.get_distinct("animal_type")
            # ['Bird', 'Cat', 'Dog', 'Livestock', 'Other']
        """
        if not self.client:
            logger.warning("get_distinct() called but client is not connected.")
            return []
        if not field or not isinstance(field, str):
            logger.error("get_distinct() requires a non-empty string field name.")
            return []
        try:
            values = self.collection.distinct(field, query or {})
            return sorted(v for v in values if v is not None)
        except PyMongoError as e:
            logger.error("get_distinct() failed: %s", e)
            return []

    # ------------------------------------------------------------------
    # Bulk import
    # ------------------------------------------------------------------

    def bulk_import(self, documents: list[dict]) -> dict:
        """
        Insert multiple documents in a single batch operation.

        ordered=False tells MongoDB to continue inserting remaining documents
        even when a duplicate-key error is encountered, so a single duplicate
        animal_id does not abort the entire import.  The method catches
        BulkWriteError and reports inserted vs. skipped counts.

        Returns:
            {
                "inserted": <int>,  # documents successfully inserted
                "skipped":  <int>,  # duplicates or other write errors skipped
                "errors":   <list>  # error details for skipped documents
            }
        """
        if not self.client:
            logger.warning("bulk_import() called but client is not connected.")
            return {"inserted": 0, "skipped": 0, "errors": []}
        if not isinstance(documents, list) or not documents:
            logger.error("bulk_import() requires a non-empty list of dicts.")
            return {"inserted": 0, "skipped": 0, "errors": []}

        try:
            result = self.collection.insert_many(documents, ordered=False)
            inserted = len(result.inserted_ids)
            logger.info("bulk_import(): inserted %d documents.", inserted)
            return {"inserted": inserted, "skipped": 0, "errors": []}

        except BulkWriteError as bwe:
            inserted = bwe.details.get("nInserted", 0)
            write_errors = bwe.details.get("writeErrors", [])
            skipped = len(write_errors)
            logger.warning(
                "bulk_import(): inserted %d, skipped %d duplicates/errors.",
                inserted,
                skipped,
            )
            return {
                "inserted": inserted,
                "skipped": skipped,
                "errors": [
                    {"index": e.get("index"), "code": e.get("code"), "msg": e.get("errmsg")}
                    for e in write_errors
                ],
            }
        except PyMongoError as e:
            logger.error("bulk_import() failed: %s", e)
            return {"inserted": 0, "skipped": 0, "errors": [str(e)]}
