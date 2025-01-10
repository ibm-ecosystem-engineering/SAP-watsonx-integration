# Establish a secure connection to an SAP HANA database using hdbcli 
import hdbcli
from hdbcli import dbapi

class HanaDB:
    def __init__(self,
                 HANA_DB_HOST,
                 HANA_DB_USER,
                 HANA_DB_PASSWORD,
                 HANA_DB_TABLE_NAME   
                 ) -> None:
        self.HANA_DB_HOST = HANA_DB_HOST
        self.HANA_DB_USER = HANA_DB_USER
        self.HANA_DB_PASSWORD = HANA_DB_PASSWORD
        self.HANA_DB_TABLE_NAME = HANA_DB_TABLE_NAME

    def con(self):
        cc = dbapi.connect(
            address=self.HANA_DB_HOST,
            port='443',
            user=self.HANA_DB_USER,
            password=self.HANA_DB_PASSWORD,
            encrypt=True
        )
        return cc
    
    # Perform a vector search on the table using the specified metric and return the top k results
    def run_vector_search(self, query_vector: str, metric="COSINE_SIMILARITY", k=4):
        """
        Performs vector search on indexed documents.
        """
        try:
            cursor = self.con().cursor()
            if not query_vector:
                    raise ValueError("Failed to generate query embedding.")
            
            sort_order = "DESC" if metric != "L2DISTANCE" else "ASC"
            sql_query = f"""
                SELECT TOP {k} ID, PAGE_NUMBER, TEXT
                FROM {self.HANA_DB_TABLE_NAME}
                ORDER BY {metric}(VECTOR_STR, TO_REAL_VECTOR('{query_vector}')) {sort_order}
                """
            cursor.execute(sql_query)
            hdf = cursor.fetchall()
            print("*"*100)
            print(hdf)
            print("*"*100)
            return hdf[:k]
        except Exception as e:
            print(f"Error during vector search: {e}")
            return []
        
