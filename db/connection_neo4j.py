from neo4j import GraphDatabase


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        """
        Close the driver connection to the database.

        :return: None
        """
        if self.driver is not None:
            self.driver.close()

    def query(self, query, db=None):
        """
        Execute the query on the database and return the results.

        :param query: Cypher query string to execute
        :param db: Name of the database to use
        :return: List of records (dictionaries) returned by the query
        """
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            # Get a session to the database using the specified database name
            session = self.driver.session(database=db) if db is not None else self.driver.session()
            # Run the query and get the results
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            # Close the session to free up resources
            if session is not None:
                session.close()
        return response
