from flask import(Flask,request,jsonify,abort)
from .models import db,setup_db,Estudiante,Curso,File
from flask_cors import CORS
from .utilities import allowed_file

import os
import sys

def create_app(test_config=None):
    app = Flask(__name__)
    with app.app_context():
        app.config['UPLOAD_FOLDER'] = 'static/estudiantes'
        setup_db(app, test_config['database_path'] if test_config else None)
        CORS(app, origins='*')


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type')
        response.headers.add('Access-Control-Allow-Methods','GET,PATCH,POST,DELETE,OPTIONS')
        response.headers.add('Acces-Control-Max-Age','10')
        return response

    @app.route('/estudiantes', methods=['POST'])
    def create_estudiante():
        returned_code = 201
        list_errors = [] 
        try:
            body = request.json

            if 'firstName' not in body:
                list_errors.append('firstname is required')
            else:
                firstName = body.get('firstname')

            if 'lastName' not in body:
                list_errors.append('lastname is requiered')
            else:
                lastName = body.get['lastname']

            if 'age' not in body:
                list_errors.append('age is required')
            else:
               age = body.get['age']

            if 'selectCurso' not in body:
                list_errors.append('curso is required')
            else:
                cursoId = body.get['selectCurso']

            if len(list_errors) > 0:
                returned_code = 400
            else:
                estudiante = Estudiante(firstName,lastName,age,cursoId)
                estudianteId = estudiante.id

        except expression as e:
                db.session.rollback()
                returned_code = 500
        finally:
            db.session.close()

        if returned_code == 400:
            return jsonify({'success':False,'message':'Error creating estudiante','errors':list_errors}), returned_code
        elif returned_code != 201:
           abort(returned_code)
        else:
            return jsonify({'id':estudianteId,'success':True,'message':'Estudiante created succesfully!'}),returned_code
        
    @app.route('/files',methods=['POST'])
    def upload_image():
        returned_code = 201
        list_errors = []
        try:
            if 'studentId' not in request.form:
                list_errors.append('studentId is required')
            else:
                studentId = request.form['studentId']

            if 'image' not in request.files:
                list_errors.append('image is required')
            else:
                file = request.files['image']

            if not allowed_file(file.filename):
                return jsonify({'success':False,'message':'Image format not allowed'}),400
            if len(list_errors) > 0:
                returned_code = 400
            else:
                cwd = os.getcwd()
                student_dir = os.path.join(app.config['UPLOAD_FOLDER'],studentId)
                
                os.makedirs(student_dir,exist_ok=True)
                upload_folder = os.path.join(cwd, student_dir)
                file.save(os.path.join(upload_folder,file.filename))
                file = File(file.filename,student_id)

                db.session.add(file)
                db.session.commit()

        except Exception as e:
            db.session.rollback()
            returned_code = 500
        finally:
            db.session.close()
            
        if returned_code == 400:
            return jsonify({'success':False,'message':'Error uploading file','errors':list_errors})
        elif returned_code != 201:
            abort(returned_code)
        else:
            return jsonify({'success':True,'message':'file upload successfully'}), returned_code
            
            
    @app.route('/cursos', methods=['POST'])
    def create_curso():
        returned_code = 201
        list_errors = []
        try:
            body = request.json
                
            if 'name' not in body:
                list_errors.append('name is required')
            else:
                name = request.json['name']

            if 'shortName' not in body:
                list_errors.append('short_name is required')
            else:
                shortName = request.json['shortName']

            if len(list_errors) > 0:
                returned_code = 400
            else:
                curso = Curso(name, shortName)
                db.session.add(curso)
                db.session.commit()
                cursoId = curso.id

        except Exception as e:
            db.session.rollback()
            returned_code = 500
            return jsonify({'success': False, 'message': str(e)})

        finally:
            db.session.close()

        if returned_code == 400:
            return jsonify({'success': False, 'message': "Error creating curso", 'errors': list_errors}), returned_code
        else:
            return jsonify({'id': cursoId, 'success': True, "message": "Curso created successfully"}), returned_code

    @app.route('/estudiantes',methods=['GET'])
    def get_estudiantes():
        returned_code = 200
        error_message = ''
        estudiante_list = []

        try:
            search_query = request.args.get('search',None)
            if search_query:
                estudiantes = Estudiante.query.filter(Estudiante.firstname.like('%{}%'.format(search_query))).all()
                    
                estudinate_list = [estudiante.serialize() for estudiante in estudiantes]
            else:
                estudiantes = Estudiante.query.all()
                estudiante_list = [estudiante.serialize() for estudiante in estudiantes]
                
            if not estudiante_list:
                returned_code = 404
                error_message = 'No employees'
        except Exception as e:
            returned_cpd = 500
            error_message = 'Error retrieving estudiantes'

        if returned_code !=200:
            return jsonify({'success':False,"message":error_message}),returned_code

        return jsonify({'success':True,'data':estudiante_list}),returned_code
            

    @app.route('/cursos-get',methods=['GET'])
    def get_curso():
        returned_code = 200
        curso_list=[]
        try:
            search_query = request.args.get('search',None)
            if search_query:
                cursos = Curso.query.filter(
                    db.or_(
                        Curso.name.like(f'%{search_query}%'),
                        Curso.shortName.like(f'%{search_query}%')
                    )
                ).all()
                curso_list = [curso.serialize() for curso in cursos]
            else:
                cursos = Curso.query.all()
                cursos_list = [curso.serialize() for curso in cursos]
            if not cursos_list:
                returned_code = 404
        except Exception as e:
            returned_code = 500
        if returned_code != 200:
            abort(returned_code)
        return jsonify({'success':True,'data':cursos_list})




    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'succes':False,'message':'method not allowed'}),405
        
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success':False,'message':'Resource not found'}),404
        
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'success':False,'message':'Internal Server error'}),500
                   
    return app
