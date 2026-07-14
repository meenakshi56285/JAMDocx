import sqlite3
from datetime import datetime


DATABASE = "history.db"



def create_table():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            file1 TEXT,

            file2 TEXT,

            similarity REAL,

            differences INTEGER,

            date TEXT

        )
        """
    )


    conn.commit()

    conn.close()





def save_history(file1, file2, similarity, differences):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO history
        (
            file1,
            file2,
            similarity,
            differences,
            date
        )

        VALUES(?,?,?,?,?)

        """,
        (
            file1,
            file2,
            similarity,
            differences,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        )
    )


    conn.commit()

    conn.close()





def get_history(search="", filter_value="all"):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()



    query = """
        SELECT *
        FROM history
        WHERE 1=1
    """


    params = []



    if search:


        query += """
        AND (
            file1 LIKE ?
            OR
            file2 LIKE ?
        )
        """


        params.append("%" + search + "%")

        params.append("%" + search + "%")





    if filter_value == "90":


        query += " AND similarity >= 90"



    elif filter_value == "70":


        query += " AND similarity BETWEEN 70 AND 89"



    elif filter_value == "low":


        query += " AND similarity < 70"





    query += """

        ORDER BY id DESC

    """



    cursor.execute(

        query,

        params

    )



    records = cursor.fetchall()


    conn.close()


    return records







def delete_history(record_id):


    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()



    cursor.execute(

        """

        DELETE FROM history

        WHERE id=?

        """,

        (record_id,)

    )



    conn.commit()

    conn.close()







def get_dashboard_data():


    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()



    # Total comparisons

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM history

        """

    )


    total = cursor.fetchone()[0]





    # Average similarity

    cursor.execute(

        """

        SELECT AVG(similarity)

        FROM history

        """

    )


    avg = cursor.fetchone()[0]



    if avg is None:

        avg = 0





    # Similarity distribution

    cursor.execute(

        """

        SELECT

        CASE

            WHEN similarity >= 90 THEN '90%+'

            WHEN similarity >= 70 THEN '70-90%'

            ELSE 'Below 70%'

        END,

        COUNT(*)

        FROM history

        GROUP BY 1

        """

    )


    distribution = cursor.fetchall()



    conn.close()



    return {


        "total": total,


        "average": round(avg,2),


        "distribution": distribution


    }
def get_dashboard_data():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    # Total comparisons
    cursor.execute(
        "SELECT COUNT(*) FROM history"
    )

    total = cursor.fetchone()[0]


    # Average similarity
    cursor.execute(
        "SELECT AVG(similarity) FROM history"
    )

    avg = cursor.fetchone()[0]

    if avg is None:
        avg = 0



    # Similarity distribution

    cursor.execute(
        """
        SELECT
        CASE
            WHEN similarity >= 90 THEN 'Excellent Match'
            WHEN similarity >= 70 THEN 'Moderate Changes'
            ELSE 'Major Changes'
        END,
        COUNT(*)
        FROM history
        GROUP BY
        CASE
            WHEN similarity >= 90 THEN 'Excellent Match'
            WHEN similarity >= 70 THEN 'Moderate Changes'
            ELSE 'Major Changes'
        END
        """
    )


    distribution = cursor.fetchall()



    conn.close()



    return {

        "total": total,

        "average": round(avg,2),

        "distribution": distribution

    }