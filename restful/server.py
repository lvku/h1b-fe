import sqlite3
import setting
from flask import g, Flask
from flask_restful import Resource, Api, reqparse
app = Flask(__name__)
api = Api(app)

DATABASE = setting.DATABASE

SQL = '''
CREATE TABLE h1b_case(
   case_id TEXT PRIMARY KEY NOT NULL,
   email TEXT NOT NULL,
   interval INT DEFAULT 86400,
   add_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO h1b_case(case_id, email) VALUES('123', '456');
curl http://localhost:5000/cases -d "case_id=123&email=tt@tt.com" -X POST
CREATE TABLE h1b_case_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    status TEXT NOT NULL,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO h1b_case_history(case_id, status) VALUES('123', 'Approved!');
'''

INSERT_CASE_SQL = '''
INSERT INTO h1b_case(case_id, email) VALUES(?, ?);
'''
TOTAL_SQL = '''
SELECT
    COUNT(*) AS total
FROM
    h1b_case
'''
STATUS_DISTRIBUTION = '''
SELECT
    status, COUNT(status) AS cnt
FROM (
    SELECT
        case_id, status
    FROM
        h1b_case_history
    GROUP BY case_id, status
)
'''
CHECK_INTERVAL_DISTRIBUTION = '''
SELECT
    interval, COUNT(interval) AS cnt
FROM
    h1b_case
'''
H1B_CASE_SQL = '''
SELECT
    *
FROM
    h1b_case
WHERE
    case_id = ?
'''
H1B_CASE_HISTORY_SQL = '''
SELECT
    *
FROM
    h1b_case_history
WHERE
    case_id = ?
ORDER BY
    last_check DESC
LIMIT
    15
'''

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    get_db().row_factory = make_dicts
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    get_db().cursor().execute(query, args)
    get_db().commit()


class Case(Resource):
    def get(self, case_id):
        case = query_db(H1B_CASE_SQL, [case_id], one=True)
        case_history = query_db(H1B_CASE_HISTORY_SQL, [case_id])
        index = case['email'].find('@')
        if index != -1:
            email_bytes = list(case['email'])
            for i in range(2, index):
                email_bytes[i] = '*'
            case['email'] = ''.join(email_bytes)
        return {
            'case': case,
            'case_history': case_history
        }
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('case_id')
        parser.add_argument('email')
        args = parser.parse_args()
        case_id = args['case_id']
        email = args['email']
        case = query_db(H1B_CASE_SQL, [case_id], one=True)
        if case:
            return {
                'result': 'Already exists!',
                'case' : case
            }
        insert_db(INSERT_CASE_SQL,[case_id, email])
        return {
            'result': 'OK',
        }

class Status(Resource):
    def get(self):
        total = query_db(TOTAL_SQL, one=True)
        status_distribution = query_db(STATUS_DISTRIBUTION)
        interval_distribution = query_db(CHECK_INTERVAL_DISTRIBUTION)
        return {
            'total': total,
            'status_distribution': status_distribution,
            'interval_distribution': interval_distribution
        }

api.add_resource(Case, '/api/cases', '/api/cases/<string:case_id>')
api.add_resource(Status, '/api/status')

@app.route("/")
def hello():
    return "Hello World!"
