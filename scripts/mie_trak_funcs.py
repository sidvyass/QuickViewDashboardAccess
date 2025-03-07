import pyodbc
import functools
from datetime import datetime
from contextlib import closing
from typing import Dict, List, Callable
from base_logger import getlogger


LOGGER = getlogger("MT Funcs")
_DSN_SANDBOX = (
    "DRIVER={SQL Server};SERVER=ETZ-SQL;DATABASE=SANDBOX;Trusted_Connection=yes"
)
_DSN_LIVE = "DRIVER={SQL Server};SERVER=ETZ-SQL;DATABASE=ETEZAZIMIETrakLive;Trusted_Connection=yes"

DSN = _DSN_SANDBOX


def with_db_conn(commit: bool = False):
    """
    A decorator to manage database connections using pyodbc.

    This decorator automatically handles connection management, commits transactions
    if specified, and properly closes the cursor and connection. If an error occurs,
    it logs the error and propagates the exception to be handled at a higher level.

    :param commit: If True, commits the transaction after function execution.
    :type commit: bool
    :return: A wrapped function with database connection handling.
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                with pyodbc.connect(DSN) as conn:
                    with closing(conn.cursor()) as cursor:
                        result = func(cursor, *args, **kwargs)

                        if commit:
                            conn.commit()

                        return result
            except pyodbc.OperationalError as vpn_err:
                error_msg = (
                    f"VPN not connected. Could not connect to the database.\n{vpn_err}"
                )
                LOGGER.error(error_msg)
                raise RuntimeError(error_msg)
            except pyodbc.Error as db_err:
                error_msg = f"Database Error in {func.__name__}: {db_err}"
                LOGGER.error(error_msg)
                raise RuntimeError(error_msg)
            except Exception as e:
                error_msg = f"Unexpected Error in {func.__name__}: {e}"
                LOGGER.error(error_msg)
                raise RuntimeError(error_msg)

        return wrapper

    return decorator


@with_db_conn()
def get_all_quickviews(cursor) -> Dict[str, str]:
    """
    Fetches all QuickViews.

    Returns a dictionary mapping QuickView primary keys to their descriptions.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :return: Mapping of QuickViewPK to descriptions.
    :rtype: Dict[str, str]
    """
    query = "SELECT QuickViewPK, Description FROM QuickView"
    cursor.execute(query)
    results = cursor.fetchall()

    return {
        str(quickview_pk): description
        for quickview_pk, description in results
        if description
    }


@with_db_conn()
def get_all_dashboards(cursor) -> Dict[str, str]:
    """
    Fetches all dashboards.

    Returns a dictionary mapping Dashboard primary keys to their descriptions.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :return: Mapping of DashboardPK to descriptions.
    :rtype: Dict[str, str]
    """
    query = "SELECT DashboardPK, Description FROM Dashboard;"
    cursor.execute(query)
    results = cursor.fetchall()

    return {
        str(dashboard_pk): description
        for dashboard_pk, description in results
        if description
    }


@with_db_conn()
def get_all_document_groups(cursor) -> Dict[str, str]:
    query = "SELECT DocumentGroupPK, Code FROM DocumentGroup"
    cursor.execute(query)
    results = cursor.fetchall()

    return {str(documet_group_pk): code for documet_group_pk, code in results if code}


@with_db_conn()
def get_document_groups(cursor) -> Dict[str, str]:
    """
    Fetches all document groups.

    Returns a dictionary mapping DocumentGroup primary keys to their Code.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :return: Mapping of DocumentGroupPK to Code.
    :rtype: Dict[str, str]
    """
    query = "SELECT DocumentGroupPK, Code FROM DocumentGroup"
    cursor.execute(query)
    results = cursor.fetchall()

    return {str(doc_group_pk): code for doc_group_pk, code in results if code}


@with_db_conn()
def get_user_quick_view(cursor, userpk: int) -> Dict[str, str]:
    """
    Fetches QuickViews assigned to a user.

    Returns a dictionary mapping QuickView primary keys to their descriptions.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :param userpk: User's primary key.
    :type userpk: int
    :return: Mapping of QuickViewPK to descriptions.
    :rtype: Dict[str, str]
    """
    query = """
        SELECT q.QuickViewPK, q.Description
        FROM QuickViewUser qu
        JOIN QuickView q ON qu.QuickViewFK = q.QuickViewPK
        WHERE qu.UserFK = ?;
    """
    cursor.execute(query, (userpk,))
    results = cursor.fetchall()

    return {
        str(quickview_pk): description
        for quickview_pk, description in results
        if description
    }


@with_db_conn()
def get_user_dashboards(cursor, userpk: int) -> Dict[str, str]:
    """
    Fetches dashboards assigned to a user.

    Returns a dictionary mapping Dashboard primary keys to their descriptions.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :param userpk: User's primary key.
    :type userpk: int
    :return: Mapping of DashboardPK to descriptions.
    :rtype: Dict[str, str]
    """
    query = """
        SELECT d.DashboardPK, d.Description
        FROM DashboardUser du
        JOIN Dashboard d ON du.DashboardFK = d.DashboardPK
        WHERE du.UserFK = ?;
    """
    cursor.execute(query, (userpk,))
    results = cursor.fetchall()

    return {
        str(dashboard_pk): description
        for dashboard_pk, description in results
        if description
    }


@with_db_conn()
def get_user_document_groups(cursor, userpk: int) -> Dict[str, str]:
    query = """
        SELECT d.DocumentGroupPK, d.Code
        FROM DocumentGroupUsers du
        JOIN DocumentGroup d ON du.DocumentGroupFK = d.DocumentGroupPK
        WHERE du.UserFK = ?;
    """
    cursor.execute(query, (userpk,))
    results = cursor.fetchall()

    return {str(doc_group_pk): code for doc_group_pk, code in results if code}


@with_db_conn(commit=True)
def add_dashboard_to_user(cursor, dashboard_pk: str, user_fk: int) -> None:
    """
    Adds a dashboard-user relationship if it does not already exist.

    Checks if an entry with the given `dashboard_pk` and `user_fk` exists in the
    `DashboardUser` table. If it does, returns the existing primary key.
    Otherwise, inserts a new record and returns the generated primary key.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :param dashboard_pk: Primary key of the dashboard.
    :type dashboard_pk: str
    :param user_fk: Primary key of the user.
    :type user_fk: int
    :return: Primary key of the DashboardUser record.
    :rtype: int
    """
    query_check = """
        SELECT DashboardUserPK 
        FROM DashboardUser 
        WHERE DashboardFK = ? AND UserFK = ?;
    """
    cursor.execute(query_check, (dashboard_pk, user_fk))
    result = cursor.fetchone()

    if result:
        return result[0]  # Return existing primary key if found

    query_insert = """
        INSERT INTO DashboardUser (DashboardFK, UserFK) 
        VALUES (?, ?);
    """
    cursor.execute(query_insert, (dashboard_pk, user_fk))


@with_db_conn(commit=True)
def add_quickview_to_user(cursor, quickview_pk: str, user_fk: int) -> None:
    """
    Adds a QuickView-user relationship if it does not already exist.

    Checks if an entry with the given `quickview_pk` and `user_fk` exists in the
    `QuickViewUser` table. If it exists, returns the existing primary key.
    Otherwise, inserts a new record and returns the generated primary key.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :param quickview_pk: Primary key of the QuickView.
    :type quickview_pk: str
    :param user_fk: Primary key of the user.
    :type user_fk: int
    :return: Primary key of the QuickViewUser record.
    :rtype: int
    """
    query_check = """
        SELECT QuickViewUserPK 
        FROM QuickViewUser 
        WHERE QuickViewFK = ? AND UserFK = ?;
    """
    cursor.execute(query_check, (quickview_pk, user_fk))
    result = cursor.fetchone()

    # TODO: inform the user that this is already added.
    if result:
        return result[0]

    query_insert = """
        INSERT INTO QuickViewUser (QuickViewFK, UserFK) 
        VALUES (?, ?);
    """
    cursor.execute(query_insert, (quickview_pk, user_fk))


@with_db_conn(commit=True)
def add_document_group_to_user(cursor, doc_group_pk: str, user_pk: int) -> None:
    query_check = """
        SELECT DocumentGroupUsersPK 
        FROM DocumentGroupUsers 
        WHERE DocumentGroupFK = ? AND UserFK = ?;
    """
    cursor.execute(query_check, (doc_group_pk, user_pk))
    result = cursor.fetchone()

    # TODO: inform the user that this is already added.
    if result:
        return result[0]

    query_insert = """
        INSERT INTO DocumentGroupUsers (DocumentGroupFK, UserFK)
        VALUES (?, ?);
    """
    cursor.execute(query_insert, (doc_group_pk, user_pk))


@with_db_conn(commit=True)
def delete_dashboard_from_user(cursor, userpk: int, dashboardpk: int) -> None:
    """
    Revokes a user's access to a specific dashboard.

    This function removes the association between a user and a dashboard in
    the `DashboardUser` table, effectively revoking the user's access to it.

    :param cursor: Database cursor passed by the decorator.
    :type cursor: pyodbc.Cursor
    :param userpk: Primary key of the user whose access is being revoked.
    :type userpk: int
    :param dashboardpk: Primary key of the dashboard to be removed from the user's access.
    :type dashboardpk: int
    :return: None
    """
    query = "DELETE FROM DashboardUser WHERE UserFK = ? AND DashboardFK = ?;"
    cursor.execute(query, (userpk, dashboardpk))


@with_db_conn(commit=True)
def delete_quickview_from_user(cursor, userpk: int, quickviewpk: int) -> None:
    """
    Revokes a user's access to a specific QuickView.

    This function removes the association between a user and a QuickView in
    the `QuickViewUser` table, preventing the user from accessing it.

    :param cursor: Database cursor passed by the decorator.
    :type cursor: pyodbc.Cursor
    :param userpk: Primary key of the user whose QuickView access is being revoked.
    :type userpk: int
    :param quickviewpk: Primary key of the QuickView to be removed from the user's access.
    :type quickviewpk: int
    :return: None
    """
    query = "DELETE FROM QuickViewUser WHERE UserFK = ? AND QuickViewFK = ?;"
    cursor.execute(query, (userpk, quickviewpk))


@with_db_conn(commit=True)
def delete_document_group_from_user(
    cursor, userpk: int, document_group_pk: int
) -> None:
    """
    [TODO:description]

    :param cursor [TODO:type]: [TODO:description]
    :param userpk: [TODO:description]
    :param document_group_pk: [TODO:description]
    """
    query = "DELETE FROM DocumentGroupUsers WHERE UserFK = ? AND DocumentGroupFK = ?"
    cursor.execute(query, (userpk, document_group_pk))


@with_db_conn(commit=True)
def create_document_group(cursor, code: str, name: str):
    query = """
    INSERT INTO DocumentGroup (Code, Name)
    OUTPUT INSERTED.DocumentGroupPK
    VALUES (?, ?);
    """
    cursor.execute(query, (code, name))
    inserted_pk = cursor.fetchone()[0]
    LOGGER.info(f"Created document group:\nPK: {inserted_pk} CODE: {code} NAME: {name}")
    return inserted_pk


# USER
@with_db_conn()
def get_user_data(cursor, enabled: bool = True) -> Dict[int, List[str]]:
    """
    Retrieves user data filtered by enabled status.

    Returns a dictionary mapping user IDs to their first and last names.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :param enabled: Whether to fetch only enabled users.
    :type enabled: bool
    :return: Mapping of UserPK to [FirstName, LastName].
    :rtype: Dict[int, List[str]]
    :raises ValueError: If no users are found.
    """
    query = "SELECT UserPK, FirstName, LastName FROM [User] WHERE Enabled=?"

    user_dict = {}
    cursor.execute(query, (1 if enabled else 0,))
    users = cursor.fetchall()

    if not users:
        raise ValueError("Mie Trak did not return any values. Check last query.")

    for x in users:
        if x:
            user_dict[x[0]] = [x[1], x[2]]

    return user_dict


@with_db_conn()
def get_user_first_last(cursor, userpk: int) -> List[str]:
    """
    Retrieves the first and last name of a user given their primary key.

    :param cursor: A database cursor used to execute the query.
    :param userpk: The primary key of the user.
    :return: A list containing the user's first name and last name.
    :raises ValueError: If no user with the given primary key is found.
    """
    query = "SELECT FirstName, LastName FROM [User] WHERE UserPK = ?"
    cursor.execute(query, (userpk,))
    result = cursor.fetchone()

    if not result:
        raise ValueError("Database did not return any value")

    return [result[0], result[1]]


@with_db_conn()
def login_user(cursor, username: str, password: str) -> bool:
    query = "SELECT Code, Password FROM [User] WHERE Code = ?"
    cursor.execute(query, (username,))
    results = cursor.fetchall()

    if not results:
        raise ValueError("Database did not return anything")

    for _, mt_password in results:
        if password.casefold() == mt_password.casefold():
            return True

    return False


# DEPARTMENT
@with_db_conn()
def get_all_departments(cursor) -> Dict[int, str]:
    """
    Fetches all departments.

    Returns a dictionary mapping department IDs to department names.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :return: Mapping of DepartmentPK to department names.
    :rtype: Dict[int, str]
    """
    query = "SELECT DepartmentPK, Name FROM Department"

    cursor.execute(query)
    departments = cursor.fetchall()

    department_dict = {}
    if departments:
        for x in departments:
            if x[1]:
                department_dict[x[0]] = x[1]

    return department_dict


@with_db_conn()
def get_department_name(cursor, departmentpk: int) -> str:
    """
    Retrieves the name of a department given its primary key.

    :param cursor: A database cursor used to execute the query.
    :param departmentpk: The primary key of the department.
    :return: The name of the department.
    :raises ValueError: If no department with the given primary key is found.
    """
    query = "SELECT Name FROM Department WHERE DepartmentPK = ?"

    cursor.execute(query, (departmentpk,))
    result = cursor.fetchone()

    if not result:
        raise ValueError("Database did not return any value")

    return result[0]


@with_db_conn()
def get_users_in_department(cursor, departmentpk: int) -> Dict[int, tuple[str, str]]:
    query_users = (
        "SELECT UserPK, FirstName, LastName FROM [User] WHERE DepartmentFK = ?"
    )
    cursor.execute(query_users, (departmentpk,))
    department_users = cursor.fetchall()

    return {
        userpk: (firstname, lastname)
        for userpk, firstname, lastname in department_users
    }


# VACATION REQUESTS


@with_db_conn()
def get_all_vacation_requests(cursor) -> List:
    """
    Fetch all pending vacation requests by joining the User table.

    This function retrieves all vacation requests that are not yet approved,
    including employee details such as first name and last name.

    :param cursor: Database cursor passed by the decorator.
    :type cursor: pyodbc.Cursor
    :return: A formatted list of vacation request records.
    :rtype: List
    :raises ValueError: If no records are returned from the query.
    """
    query = """
        SELECT v.VacationRequestPK, u.firstname, u.lastname, v.FromDate, v.ToDate, 
               v.StartTime, v.Hours, v.Reason, v.Approved
        FROM VacationRequest v
        JOIN [User] u ON v.EmployeeFK = u.UserPK 
        WHERE v.Approved = 0
        ORDER BY v.VacationRequestPK DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    if not results:
        LOGGER.error(f"MT did not return anything for: \n{query}")
        raise ValueError("Mie Trak did not return anything. Check Query.")

    return _format_results(results)


def _format_results(data):
    """
    Formats raw database query results into a structured list of dictionaries.

    Each dictionary represents a vacation request with properly formatted dates,
    times, and employee details.

    :param data: List of tuples containing raw database results.
    :type data: List[Tuple]
    :return: A list of formatted vacation request records.
    :rtype: List[Dict[str, Any]]
    """
    formatted_data = []
    for row in data:
        (
            vacation_id,
            first_name,
            last_name,
            from_date,
            to_date,
            start_time,
            hours,
            reason,
            approved,
        ) = row
        formatted_row = {
            "Vacation ID": vacation_id,
            "Employee": f"{first_name} {last_name}",
            "From Date": from_date.strftime("%Y-%m-%d") if from_date else "N/A",
            "To Date": to_date.strftime("%Y-%m-%d") if to_date else "N/A",
            "Start Time": datetime.strptime(start_time[:15], "%H:%M:%S.%f").strftime(
                "%I:%M %p"
            )
            if start_time
            else "N/A",
            "Hours": float(hours) if hours else "N/A",
            "Reason": reason,
            "Approved": approved,
        }
        formatted_data.append(formatted_row)
    return formatted_data


@with_db_conn(commit=True)
def approve_vacation_request(cursor, request_pk: int) -> None:
    """
    Marks a vacation request as approved.

    Updates the `Approved` field of the `VacationRequest` table for the given request.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :param request_pk: Primary key of the vacation request to approve.
    :type request_pk: int
    :return: None
    """
    query = """
        UPDATE VacationRequest
        SET Approved = 1
        WHERE VacationRequestPK = ?
    """
    cursor.execute(query, (request_pk,))


@with_db_conn(commit=True)
def update_vacation_request_reason(cursor, vacation_request_pk: int, reason: str):
    """
    Adds a note to the vacation request.

    Appends the `Reason` field of the `VacationRequest` table with the reason string.
    Usually done when we want to keep track of what was disapproved in mie trak.

    NOTE: Reason should have a timestamp. For reasoning formatting see VacationRequestPK = 3;

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :param vacation_request_pk: Primary key of the vacation request to update.
    :type vacation_request_pk: int
    :param reason: The note to update the vacation request with.
    :type reason: str
    :raises RuntimeError: If parameters are None.
    """
    query = """
    UPDATE VacationRequest
    SET Reason = reason + CHAR(13) + CHAR(14) + CHAR(13) + CHAR(14) + ?
    WHERE VacationRequestPK = ?
    """
    cursor.execute(query, (reason, vacation_request_pk))


@with_db_conn()
def get_user_email_from_vacation_pk(cursor, pk: int) -> str:
    """
    Retrieves the email of the user associated with a given vacation request.

    :param cursor: Database cursor.
    :type cursor: pyodbc.Cursor
    :param pk: Primary key of the vacation request.
    :type pk: int
    :return: Email address of the user.
    :rtype: str
    :raises ValueError: If no matching record is found.
    """
    query = """
        SELECT u.Email
        FROM VacationRequest v
        JOIN [User] u ON v.EmployeeFK = u.UserPK
        WHERE v.VacationRequestPK = ?;
    """

    cursor.execute(query, (pk,))
    result = cursor.fetchone()

    if not result:
        LOGGER.error("Database did not return anything")
        raise ValueError("Database did not return anything")

    return result[0]


@with_db_conn()
def get_entry_from_table(cursor, table_name: str, pk: int) -> Dict[str, str]:
    """
    Retrieves dashboard information as a dictionary.

    :param cursor: A database cursor used to execute the query.
    :param dashboardpk: The primary key of the dashboard.
    :return: A dictionary containing dashboard information with column names as keys.
    :raises ValueError: If no dashboard with the given primary key is found.
    """
    query = f"SELECT * FROM {table_name} WHERE {table_name}PK = ?"
    cursor.execute(query, (pk,))
    row = cursor.fetchone()

    if not row:
        raise ValueError(f"No entry found in {table_name}PK:  {pk}")

    column_names = [desc[0] for desc in cursor.description]

    return dict(zip(column_names, row))
