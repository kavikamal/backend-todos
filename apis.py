from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
api = Api(app)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('todos.log')
file_handler.setFormatter(formatter)
rotate_handler = RotatingFileHandler(
    'todos.log', maxBytes=2000, backupCount=5
)

logger.addHandler(file_handler)
logger.addHandler(rotate_handler)

todos = {
    "1": {
        "title": "Piano recital practice",
        "due_date": None,
        "completed": False,
        "completed_on": None,
        "created_on": "2018-12-30 12:47:46.264942",
        "last_updated_on": "2019-1-03 12:47:46.264942"
    },
    "2": {
        "title": "Swimming Lesson",
        "due_date": "soon",
        "completed": False,
        "completed_on": None,
        "created_on": "2019-1-2 10:31:29.264935",
        "last_updated_on": "2018-1-3 10:31:29.264935",
    },
}
parser = reqparse.RequestParser()
parser.add_argument('title', required=True, help="title is required!")
parser.add_argument('due_date')
parser.add_argument('completed')


# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):

    def get(self, todo_id):
        logger.info({'message': 'Single Todo: {}'.format(todos[todo_id])})
        if todo_id not in todos:
            abort(404,
                  message="Todo with id of {} doesn't exist".format(todo_id))
        return todos[todo_id]

    def delete(self, todo_id):
        """
            Deletes a todo based on id.
        """
        global todos
        if todo_id not in todos:
            abort(404,
                  message="Todo with id of {} doesn't exist".format(todo_id))
        logger.info('Recieved DELETE request for todo ID {}'.format(todo_id))
        del todos[todo_id]
        logger.info('Responded with success message')
        return {'success': 'Deleted todo with id %s' % (todo_id)}

    def put(self, todo_id):
        """
            Updates a todo based on id.
        """
        global todo
        args = parser.parse_args()
        if args['completed']:
            todos[todo_id].update(
                {
                    'completed': (
                        True if args['completed'].lower()
                        == 'true' else False
                    ),
                    'completion_date': (
                        str(datetime.now()) if args['completed'].lower(
                        ) == 'true' else None
                    )
                }
            )
        if args['due_date']:
            todos[todo_id].update({
                'due_date': args['due_date']
            })
        if args['title']:
            todos[todo_id].update({
                'title': args['title']
            })
        todos[todo_id].update({'last_updated_date': str(datetime.now())})
        logger.info('Recieved PUT request for ID {}:'.format(todo_id))
        return 'Recieved PUT request for ID {}:'.format(todo_id)


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        """
            Returns a list of all todos.
        """
        logger.info('Recieved GET request for all todos')
        logger.info('Returning all todos:')
        logger.info(todos)
        return todos

    def post(self):
        """
            Creates a new todo based off provided user data. A unique ID
            and certain timestamps are automatically assigned.
        """
        global todos
        args = parser.parse_args()
        parser.add_argument('title', required=True,
                            help="Title cannot be blank!")
        todo_id = int(max(todos.keys())) + 1 if todos else 1
        todo_id = str(todo_id)
        todos[todo_id] = Todo(
            args['title'],
            args['due_date'],
            args['completed']
        ).toJSON()
        logger.info('Recieved POST request for a new todo:')
        logger.info('Added todo and responded with newly created todo:')
        logger.info(todo)
        return 'Todo created: {}'.format(todos[todo_id])


"""
Actually setup the Api resource routing here
"""

api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')


if __name__ == '__main__':
    app.run(debug=True)
