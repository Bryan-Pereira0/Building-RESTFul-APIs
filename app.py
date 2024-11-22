#I created a new table identical to the workoutsessions table I couldn't get it to work, here is the DDL for the new table.
'''
CREATE TABLE workout_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    session_date DATE NOT NULL,
    session_time TIME NOT NULL,
    activity VARCHAR(255) NOT NULL
);
'''
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError
import mysql.connector
from mysql.connector import Error
from password import my_password
from datetime import datetime, timedelta, time

app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)
    class Meta:
        fields = ("id", "name", "age")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

#timedelta to time to fix format error
def timedelta_to_time(td):
    return (datetime.min + td).time()

class WorkoutSessionSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.Time(required=True)
    activity = fields.String(required=True)
    session_id = fields.Integer()

    class Meta:
        fields = ('session_id', 'member_id', 'session_date', 'session_time', 'activity')

workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)


def get_db_connection():
    db_name = 'fitness_center'
    host = 'localhost'
    user = 'root'
    password = my_password
    
    try:
        conn = mysql.connector.connect(
            database=db_name,
            host=host, 
            user=user, 
            password=password
        )
        
        print("Connection to the MySQL DB successful")
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None


@app.route('/')
def home():
    return "Welcome to the Fitness Center!"
    
    
@app.route("/members", methods=["GET"])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify("Connection to the DB failed"), 500
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM members"
        
        cursor.execute(query)
        
        members = cursor.fetchall()
        
        
        return members_schema.jsonify(members)
    except Error as e:
        print(f"Error: {e}")
        return jsonify("Internal Server Error"), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
         
            
@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)  
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify("Connection to the DB failed"), 500
        cursor = conn.cursor()
    
        new_member = (
            member_data["id"],
            member_data["name"],
            member_data["age"]
        )
        
        query = "INSERT INTO members (id, name, age) VALUES (%s, %s, %s)"
        cursor.execute(query, new_member)
        conn.commit()
        
        return jsonify({"message": "Member added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify("Internal Server Error"), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
            
@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)  
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify("Connection to the DB failed"), 500
        cursor = conn.cursor()
        
        updated_member = (
            member_data["name"],
            member_data["age"],
            id
        )
        
        query = "UPDATE members SET name=%s, age=%s WHERE id=%s"
        
        cursor.execute(query, updated_member)
        conn.commit()
        
        return jsonify({"message": "Member updated successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify("Internal Server Error"), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
            
@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify("Connection to the DB failed"), 500
        cursor = conn.cursor()
        
        member_to_remove = (id, )
        
        cursor.execute("SELECT * FROM members WHERE id = %s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"message": "Member not found."}), 404
        
        query = "DELETE FROM members WHERE id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()
        
        return jsonify({"message": "Member deleted."}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify("Internal Server Error"), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            

@app.route("/workout_sessions", methods=["POST"])
def schedule_workout_session():
    try:
        session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify("Connection to the DB failed"), 500
        cursor = conn.cursor()

        new_session = (
            session_data["member_id"],
            session_data["session_date"],
            session_data["session_time"],
            session_data["activity"]
        )

        query = "INSERT INTO workout_sessions (member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, new_session)
        conn.commit()
        
        return jsonify({"message": "Workout session scheduled"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify("Internal Server Error"), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()   


@app.route("/workout_sessions/<int:id>", methods=["PUT"])
def update_workout_session(id):
    try:
        session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify("Connection to the DB failed"), 500
        cursor = conn.cursor()

        updated_session = (
            session_data["member_id"],
            session_data["session_date"],
            session_data["session_time"],
            session_data["activity"],
            id
        )

        query = "UPDATE workout_sessions SET member_id=%s, session_date=%s, session_time=%s, activity=%s WHERE session_id=%s"
        cursor.execute(query, updated_session)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Workout session not found"}), 404

        return jsonify({"message": "Workout session updated"}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify("Internal Server Error"), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
#all workouts
@app.route("/workout_sessions", methods=["GET"])
def get_workout_sessions():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify("Connection to the DB failed"), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM workout_sessions"
        cursor.execute(query)
        sessions = cursor.fetchall()

        #timedelta error fix
        for session in sessions:
            if isinstance(session['session_time'], timedelta):
                session['session_time'] = timedelta_to_time(session['session_time'])

        return workout_sessions_schema.jsonify(sessions)

    except Error as e:
        print(f"Error: {e}")
        return jsonify("Internal Server Error"), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#for 1 member
@app.route("/members/<int:member_id>/workout_sessions", methods=["GET"])
def get_member_workout_sessions(member_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify("Connection to the DB failed"), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM workout_sessions WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        sessions = cursor.fetchall()

        #timedelta error fix
        for session in sessions:
            if isinstance(session['session_time'], timedelta):
                session['session_time'] = timedelta_to_time(session['session_time'])

        return workout_sessions_schema.jsonify(sessions)

    except Error as e:
        print(f"Error: {e}")
        return jsonify("Internal Server Error"), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
            
if __name__ == '__main__':
    app.run(debug=True)