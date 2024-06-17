import json
import jwt
from datetime import datetime, timedelta
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError
import openai
from dotenv import load_dotenv
import os
class MyApiController(http.Controller):


    secret_key = "5f04d9faedcd087e0fd39da321676e258a0196be2e6f314922752ea72b0eaaad" 

    # API PARA INICIAR SESION
    @http.route('/api/login', type='http', auth="none",
                methods=['POST'], csrf=False, save_session=False, cors="*")
    def get_token(self):
        byte_string = request.httprequest.data
        data = json.loads(byte_string.decode('utf-8'))
        email = data['email']
        password = data['password']
        fcm_token = data.get('fcm_token')  # Obtener el token FCM del payload

        try:
            # Autenticar al usuario
            user_id = request.session.authenticate(request.db, email, password)
            if not user_id:
                return json.dumps({"error": "Invalid email or Password."})

            # Obtener el entorno del usuario autenticado
            env = request.env(user=request.env.user.browse(user_id))

            # Obtener el usuario
            user = env['res.users'].browse(user_id)

            # Guardar el token FCM en el usuario
            user.sudo().write({'fcm_token': fcm_token})

            # Determinar el modelo asociado al usuario usando sudo() para evitar problemas de permisos
            model_name = None
            user_name = None
            if env['academic.student'].sudo().search([('user_id', '=', user.id)]):
                model_name = 'academic.student'
                user_name = env['academic.student'].sudo().search([('user_id', '=', user.id)]).name
            elif env['academic.apoderado'].sudo().search([('user_id', '=', user.id)]):
                model_name = 'academic.apoderado'
                user_name = env['academic.apoderado'].sudo().search([('user_id', '=', user.id)]).name
            elif env['hr.employee'].sudo().search([('user_id', '=', user.id)]):
                model_name = 'hr.employee'
                user_name = env['hr.employee'].sudo().search([('user_id', '=', user.id)]).name

            # Generar el token JWT
            payload = {
                'user_id': user_id,
                'email': email,
                'model_name': model_name,
                'exp': datetime.utcnow() + timedelta(hours=1)  # Token expira en 1 hora
            }
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')

            # Crear el payload de respuesta directamente sin el envoltorio "data"
            response_payload = {
                'user_id': user_id,
                'email': email,
                'token': token,
                'model_name': model_name,
                'user_name': user_name,
                "responsedetail": {
                    "messages": "UserValidated",
                    "messagestype": 1,
                    "responsecode": 200
                }
            }

            # Responder en formato JSON
            return json.dumps(response_payload)

        except AccessDenied:
            return json.dumps({"error": "Invalid email or Password."})
        except Exception as e:
            return json.dumps({"error": str(e)})

        
    # API PARA CERRAR SESION
    @http.route('/api/logout', type='http', auth="none",
                methods=['POST'], csrf=False, save_session=False, cors="*")
    def logout(self):
        try:
            # Obtener el token del encabezado de la solicitud
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header:
                return json.dumps({"error": "Token is missing!"})
            
            token = auth_header.split(" ")[1]

            # Decodificar el token JWT para obtener el user_id

            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload['user_id']

            # Cerrar la sesión del usuario
            request.session.logout()

            # Responder con un mensaje de éxito
            response_payload = {
                "responsedetail": {
                    "messages": "UserLoggedOut",
                    "messagestype": 1,
                    "responsecode": 200
                }
            }

            return json.dumps(response_payload)

        except jwt.ExpiredSignatureError:
            return json.dumps({"error": "Token has expired!"})
        except jwt.InvalidTokenError:
            return json.dumps({"error": "Invalid token!"})
        except Exception as e:
            return json.dumps({"error": str(e)})
        

    @http.route('/api/courses/<int:user_id>', type='http', auth="none",
                methods=['GET'], csrf=False, cors="*")
    def get_cursos_por_profesor(self, user_id):
        try:
            # Obtener el token del encabezado de la solicitud
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header:
                return json.dumps({"error": "Token is missing!"})
            
            token = auth_header.split(" ")[1]

            # Decodificar el token JWT para obtener el user_id
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            token_user_id = payload['user_id']

            # Obtener el entorno del usuario autenticado
            env = request.env(user=request.env.user.browse(token_user_id))

            # Buscar el empleado asociado al user_id
            empleado = env['hr.employee'].sudo().search([('user_id', '=', int(user_id))], limit=1)
            if not empleado:
                return json.dumps({"error": "Empleado no encontrado para el user_id proporcionado"})

            # Buscar todos los cursos asociados al profesor
            cursos = env['academic.curso.materia'].sudo().search([('profesor_id', '=', empleado.id)])

            # Preparar la respuesta
            cursos_data = []
            for curso in cursos:
                cursos_data.append({
                    'curso_materia_id': curso.id,
                    'curso_id': curso.curso_id.id,
                    'curso_name': curso.curso_id.name,
                    'materia_id': curso.materia_id.id,
                    'materia_name': curso.materia_id.name,
                    'schedule': curso.schedule,
                    'aula_id': curso.aula_id.id,
                    'aula_name': curso.aula_id.name,
                })

            response_payload = {
                'profesor_id': empleado.id,
                'profesor_name': empleado.name,
                'cursos': cursos_data,
                "responsedetail": {
                    "messages": "CursosObtenidos",
                    "messagestype": 1,
                    "responsecode": 200
                }
            }

            # Responder en formato JSON
            return json.dumps(response_payload)

        except jwt.ExpiredSignatureError:
            return json.dumps({"error": "Token has expired!"})
        except jwt.InvalidTokenError:
            return json.dumps({"error": "Invalid token!"})
        except Exception as e:
            return json.dumps({"error": str(e)})
        

     # API PARA CREAR UNA NOTICIA
    @http.route('/api/notice/create', type='json', auth="none", methods=['POST'], csrf=False, cors="*")
    def create_notice(self):
        try:
            # Obtener el token del encabezado de la solicitud
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header:
                return {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": 401,
                        "message": "Token is missing!",
                        "data": {}
                    }
                }
            
            token = auth_header.split(" ")[1]

            # Decodificar el token JWT para obtener el user_id
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload['user_id']

            # Obtener los datos de la solicitud
            data = json.loads(request.httprequest.data)
            title = data.get('title')
            description = data.get('description')
            curso_materia_id = data.get('curso_materia_id')
            fecha_inicio = data.get('fecha_inicio')
            fecha_fin = data.get('fecha_fin')

            # Validar los datos
            if not title or not curso_materia_id:
                raise UserError("Title and Curso Materia ID are required.")

            # Crear la noticia
            notice = request.env['academic.notice'].sudo().create({
                'title': title,
                'description': description,
                'curso_materia_id': curso_materia_id,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
            })

            # Responder con un mensaje de éxito
            response_payload = {
                "jsonrpc": "2.0",
                "id": None,
                "result": {
                    "notice_id": notice.id,
                    "title": notice.title,
                    "description": notice.description,
                    "curso_materia_id": notice.curso_materia_id.id,
                    "fecha_inicio": notice.fecha_inicio.isoformat() if notice.fecha_inicio else None,
                    "fecha_fin": notice.fecha_fin.isoformat() if notice.fecha_fin else None,
                    "responsedetail": {
                        "messages": "NoticeCreated",
                        "messagestype": 1,
                        "responsecode": 200
                    }
                }
            }

            return response_payload

        except jwt.ExpiredSignatureError:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": 401,
                    "message": "Token has expired!",
                    "data": {}
                }
            }
        except jwt.InvalidTokenError:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": 401,
                    "message": "Invalid token!",
                    "data": {}
                }
            }
        except UserError as e:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": 400,
                    "message": str(e),
                    "data": {}
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": 500,
                    "message": "Internal server error!",
                    "data": str(e)
                }
            }
        
    # API para obtener todas las noticias relacionadas a un curso_materia
    @http.route('/api/notices/<int:curso_materia_id>', type='http', auth="none", methods=['GET'], csrf=False, cors="*")
    def get_notices(self, curso_materia_id):
        try:
            # Obtener el token del encabezado de la solicitud
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header:
                return request.make_response(json.dumps({
                    "error": {
                        "code": 401,
                        "message": "Token is missing!"
                    }
                }), headers={'Content-Type': 'application/json'})

            token = auth_header.split(" ")[1]

            # Decodificar el token JWT para obtener el user_id
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            
            notices = request.env['academic.notice'].sudo().search([
                ('curso_materia_id', '=', curso_materia_id)
            ])

            notices_data = []
            for notice in notices:
                notices_data.append({
                    'title': notice.title,
                    'description': notice.description,
                    'curso_materia_id': notice.curso_materia_id.id,
                    'fecha_inicio': notice.fecha_inicio.isoformat() if notice.fecha_inicio else None,
                    'fecha_fin': notice.fecha_fin.isoformat() if notice.fecha_fin else None,
                    'profesor': notice.profesor,
                    'curso': notice.curso,
                    'materia': notice.materia,
                })

            return request.make_response(json.dumps(notices_data), headers={'Content-Type': 'application/json'})

        except jwt.ExpiredSignatureError:
            return request.make_response(json.dumps({
                "error": {
                    "code": 401,
                    "message": "Token has expired!"
                }
            }), headers={'Content-Type': 'application/json'})
        except jwt.InvalidTokenError:
            return request.make_response(json.dumps({
                "error": {
                    "code": 401,
                    "message": "Invalid token!"
                }
            }), headers={'Content-Type': 'application/json'})
        except Exception as e:
            return request.make_response(json.dumps({
                "error": {
                    "code": 500,
                    "message": "Internal server error!",
                    "data": str(e)
                }
            }), headers={'Content-Type': 'application/json'})
        

    # API para obtener todas las noticias relacionadas a un estudiante
    @http.route('/api/notices/student/<int:user_id>', type='http', auth="none", methods=['GET'], csrf=False, cors="*")
    def get_student_notices(self, user_id):
        try:
            # Buscar al estudiante asociado al user_id
            student = request.env['academic.student'].sudo().search([('user_id', '=', user_id)], limit=1)
            if not student:
                return request.make_response(json.dumps({
                    "error": {
                        "code": 404,
                        "message": "Student not found!"
                    }
                }), headers={'Content-Type': 'application/json'})

            # Buscar inscripciones del estudiante
            inscripciones = request.env['academic.inscripcion'].sudo().search([('student_id', '=', student.id)])
            course_ids = inscripciones.mapped('course_id.id')

            # Buscar curso_materia relacionados a los cursos
            curso_materias = request.env['academic.curso.materia'].sudo().search([('curso_id', 'in', course_ids)])
            curso_materia_ids = curso_materias.mapped('id')

            # Buscar noticias relacionadas a los curso_materia
            notices = request.env['academic.notice'].sudo().search([
                ('curso_materia_id', 'in', curso_materia_ids)
            ])

            notices_data = []
            for notice in notices:
                notices_data.append({
                    'title': notice.title,
                    'description': notice.description,
                    'curso_materia_id': notice.curso_materia_id.id,
                    'fecha_inicio': notice.fecha_inicio.isoformat() if notice.fecha_inicio else None,
                    'fecha_fin': notice.fecha_fin.isoformat() if notice.fecha_fin else None,
                    'profesor': notice.profesor,
                    'curso': notice.curso,
                    'materia': notice.materia,
                })

            return request.make_response(json.dumps(notices_data), headers={'Content-Type': 'application/json'})

        except Exception as e:
            return request.make_response(json.dumps({
                "error": {
                    "code": 500,
                    "message": "Internal server error!",
                    "data": str(e)
                }
            }), headers={'Content-Type': 'application/json'})
        
    # Api para obtener los estudiantes asociados a un apoderado
    @http.route('/api/apoderado/students/<int:apoderado_id>', type='http', auth="none", methods=['GET'], csrf=False, cors="*")
    def get_apoderado_students(self, apoderado_id):
        try:
            # Obtener el token del encabezado de la solicitud
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header:
                return request.make_response(json.dumps({
                    "error": {
                        "code": 401,
                        "message": "Token is missing!"
                    }
                }), headers={'Content-Type': 'application/json'})

            token = auth_header.split(" ")[1]

            # Decodificar el token JWT para obtener el user_id
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload['user_id']

            # Buscar el apoderado
            apoderado = request.env['academic.apoderado'].sudo().search([('user_id', '=', apoderado_id)], limit=1)
            if not apoderado:
                return request.make_response(json.dumps({
                    "error": {
                        "code": 404,
                        "message": "Apoderado not found!"
                    }
                }), headers={'Content-Type': 'application/json'})

            students_data = []
            for student in apoderado.student_ids:
                # Buscar la inscripción del estudiante
                enrollment = request.env['academic.inscripcion'].sudo().search([('student_id', '=', student.id)], limit=1)
                if enrollment:
                    course = enrollment.course_id.name if enrollment.course_id else "N/A"
                    students_data.append({
                        'student_name': student.name,
                        'course_name': course,
                        'user_id': student.user_id.id if student.user_id else None
                    })

            return request.make_response(json.dumps(students_data), headers={'Content-Type': 'application/json'})

        except jwt.ExpiredSignatureError:
            return request.make_response(json.dumps({
                "error": {
                    "code": 401,
                    "message": "Token has expired!"
                }
            }), headers={'Content-Type': 'application/json'})
        except jwt.InvalidTokenError:
            return request.make_response(json.dumps({
                "error": {
                    "code": 401,
                    "message": "Invalid token!"
                }
            }), headers={'Content-Type': 'application/json'})
        except Exception as e:
            return request.make_response(json.dumps({
                "error": {
                    "code": 500,
                    "message": "Internal server error!",
                    "data": str(e)
                }
            }), headers={'Content-Type': 'application/json'})


    # API para obtener el boletín de un estudiante
    @http.route('/api/boletin/<int:user_id>', type='http', auth="none", methods=['GET'], csrf=False, cors="*")
    def get_boletin(self, user_id):
        try:
            # Buscar al estudiante asociado al user_id
            student = request.env['academic.student'].sudo().search([('user_id', '=', user_id)], limit=1)
            if not student:
                return request.make_response(json.dumps([]), headers={'Content-Type': 'application/json'})

            # Buscar los boletines relacionados al student_id
            boletines = request.env['academic.boletin'].sudo().search([('student_id', '=', student.id)])
            if not boletines:
                return request.make_response(json.dumps([]), headers={'Content-Type': 'application/json'})

            # Preparar los datos de los boletines
            boletines_data = []
            for boletin in boletines:
                boletin_info = {
                    'boletin_id': boletin.id,
                    'curso_id': boletin.curso_id.id,
                    'curso_name': boletin.curso_id.name,
                    'nro_bimestre': boletin.nro_bimestre,
                    'student_id': boletin.student_id.id,
                    'fecha': boletin.fecha.isoformat(),
                    'nota_total': boletin.nota_total,
                    'notas': []
                }

                # Incluir las notas del boletín
                for nota in boletin.nota_ids:
                    boletin_info['notas'].append({
                        'curso_id': nota.curso_id.id,
                        'curso_name': nota.curso_id.name,
                        'materia_id': nota.materia_id.id,
                        'materia_name': nota.materia_id.name,
                        'nro_bimestre': nota.nro_bimestre,
                        'nota': nota.nota
                    })

                boletines_data.append(boletin_info)

            # Responder en formato JSON
            return request.make_response(json.dumps(boletines_data), headers={'Content-Type': 'application/json'})

        except Exception as e:
            return request.make_response(json.dumps([]), headers={'Content-Type': 'application/json'})

    @http.route('/api/chatgpt', type='json', auth="none", methods=['POST'], csrf=False, cors="*")
    def chatgpt_query(self):
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            
            # Obtener los datos del cuerpo de la solicitud
            data = json.loads(request.httprequest.data)
            tema = data.get('tema', '')
            materia = data.get('materia', '')
            descripcion = data.get('descripcion', '')

            # Componer el prompt para OpenAI
            prompt = (
                f"Como docente, quiero generar una tarea para mis estudiantes. "
                f"Tema: {tema}. "
                f"Materia: {materia}. "
                f"Descripción adicional: {descripcion}. "
                f"Por favor, genera una tarea detallada y apropiada para mis estudiantes que abarque estos puntos. "
                f"Esta tarea debe ser clara, completa y educativa. Gracias."
            )

            # Configurar la API de OpenAI
            openai.api_key = api_key

            # Enviar el prompt a OpenAI y obtener la respuesta
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Asegúrate de usar el modelo más reciente disponible
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extraer la respuesta generada
            answer = response.choices[0].message['content']

            # Responder en formato JSON
            return {
                "jsonrpc": "2.0",
                "id": None,
                "result": {
                    "prompt": prompt,
                    "answer": answer,
                    "responsedetail": {
                        "messages": "Successful query to OpenAI",
                        "messagestype": 1,
                        "responsecode": 1000
                    }
                }
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": 500,
                    "message": "Internal server error!",
                    "data": str(e)
                }
            }
