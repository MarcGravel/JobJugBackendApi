import mariadb
import dbcreds
from flask import Response

def db_fetchone_index(query, args):
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        cursor.execute(query, args)
        response = cursor.fetchone()[0]

    except mariadb.DataError:
        print("Something is wrong with the data - db_fetchone_index")
        return Response("Something is wrong with the data", mimetype='text/plain', status=404)
    except mariadb.OperationalError:
        print("Something is wrong with your connection - db_fetchone_index")
        return Response("Something is wrong with the connection", mimetype='text/plain', status=500)
    except:
        print("Something went wrong - db_fetchone_index")
        return Response("Something went wrong", status=500)
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()

    return response

def db_fetchone_index_noArgs(query):
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        cursor.execute(query)
        response = cursor.fetchone()[0]

    except mariadb.DataError:
        print("Something is wrong with the data - db_fetchone_index")
        return Response("Something is wrong with the data", mimetype='text/plain', status=404)
    except mariadb.OperationalError:
        print("Something is wrong with your connection - db_fetchone_index")
        return Response("Something is wrong with the connection", mimetype='text/plain', status=500)
    except:
        print("Something went wrong - db_fetchone_index")
        return Response("Something went wrong", status=500)
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()

    return response

def db_fetchone(query, args):
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        cursor.execute(query, args)
        response = cursor.fetchone()

    except mariadb.DataError:
        print("Something is wrong with the data - db_fetchone")
        return Response("Something is wrong with the data", mimetype='text/plain', status=404)
    except mariadb.OperationalError:
        print("Something is wrong with your connection - db_fetchone")
        return Response("Something is wrong with the connection", mimetype='text/plain', status=500)
    except:
        print("Something went wrong - db_fetchone")
        return Response("Something went wrong", status=500)
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()

    return response

def db_fetchall(query):
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        cursor.execute(query)
        response = cursor.fetchall()

    except mariadb.DataError:
        print("Something is wrong with the data - db_fetchall")
        return Response("Something is wrong with the data", mimetype='text/plain', status=404)
    except mariadb.OperationalError:
        print("Something is wrong with your connection - db_fetchall")
        return Response("Something is wrong with the connection", mimetype='text/plain', status=500)
    except:
        print("Something went wrong - db_fetchall")
        return Response("Something went wrong", status=500)
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()

    return response

def db_fetchall_args(query, args):
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        cursor.execute(query, args)
        response = cursor.fetchall()

    except mariadb.DataError:
        print("Something is wrong with the data - db_fetchall_args")
        return Response("Something is wrong with the data", mimetype='text/plain', status=404)
    except mariadb.OperationalError:
        print("Something is wrong with your connection - db_fetchall_args")
        return Response("Something is wrong with the connection", mimetype='text/plain', status=500)
    except:
        print("Something went wrong - db_fetchall_args")
        return Response("Something went wrong", status=500)
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()

    return response

def db_commit(query, args):
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        cursor.execute(query, args)
        conn.commit()

    except mariadb.DataError:
        print("Something is wrong with the data - db_commit")
        return Response("Something is wrong with the data", mimetype='text/plain', status=404)
    except mariadb.OperationalError:
        print("Incorrect date value - db_commit")
        return Response("Incorrect date value", mimetype='text/plain', status=500)
    except:
        print("Something went wrong - db_commit")
        return Response("Something went wrong", status=500)
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()