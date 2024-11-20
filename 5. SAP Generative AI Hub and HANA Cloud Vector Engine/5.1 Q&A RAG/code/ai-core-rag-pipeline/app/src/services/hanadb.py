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
    def run_vector_search(self, query: str, query_vector: str, metric="COSINE_SIMILARITY", k=4):
        cursor = self.con().cursor()
        if metric == 'L2DISTANCE':
            sort = 'ASC'
        else:
            sort = 'DESC'
        sql = '''SELECT TOP {k} "ID", "CONTENT"
            FROM "{tbl_name}"
            ORDER BY "{metric}"("VECTOR_STR", TO_REAL_VECTOR('{qv}')) {sort}'''.format(k=k, tbl_name=self.HANA_DB_TABLE_NAME, metric=metric, qv=query_vector, sort=sort)
        cursor.execute(sql)
        hdf = cursor.fetchall()
        return hdf[:k]