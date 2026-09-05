from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
socketio = SocketIO()
csrf = CSRFProtect()
migrate = Migrate()
