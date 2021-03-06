import re
from flask_jwt import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Resource, reqparse

from app import db
from app.models.admin import Admin, AdminSchema
from app.utils import send_message, rollback

schema = AdminSchema()


def check_args(args):
	check = all(args.values())
	if check:
		email_re = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
		check = False if not re.findall(email_re, args["email"]) else True
	return check


def get_args(edit=False):
	parser = reqparse.RequestParser()

	parser.add_argument("nome", type=str, location="json")
	parser.add_argument("email", type=str, location="json")
	parser.add_argument("password", type=str, location="json")
	args = parser.parse_args(strict=True)

	return args if check_args(args) else False


class AdminResource(Resource):
	@jwt_required()
	def get(self, id):
		admin = Admin.query.get(id)
		if not admin:
			return send_message("O administrador {} não existe".format(id), 404)
		return schema.dump(admin).data, 200

	@jwt_required()
	def put(self, id):
		args = get_args()

		if not args:
			return send_message("Parâmetros inválidos!", 422)

		admin = Admin.query.get(id)

		if not admin:
			return send_message("O administrador {} não existe".format(id), 404)

		if admin.nome != args["nome"]:
			admin.nome = args["nome"]

		if admin.email != args["email"]:
			check_email = Admin.query.filter(Admin.email == args["email"]).all()
			if not check_email:
				admin.email = args["email"]
			else:
				return send_message("Este email já existe".format(id), 409)

		admin.hash_password(args["password"])
		admin.update()
		return schema.dump(admin).data, 200

	@jwt_required()
	def delete(self, id):
		adms = Admin.query.all()
		if len(adms) == 1:
			return send_message("Há apenas um administrador", 403)
		try:
			admin = Admin.query.get(id)
			if not admin:
				return send_message("O administrador {} não existe".format(id), 404)
			admin.delete(admin)
		except SQLAlchemyError as e:
			return rollback(e, db)
		else:
			return None, 204


class AdminListResource(Resource):
	# @jwt_required()
	def get(self):
		admins = Admin.query.all()
		return schema.dump(admins, many=True).data, 200

	@jwt_required()
	def post(self):
		args = get_args()
		if not args:
			return send_message("Parâmetros inválidos!", 422)

		try:
			admin = Admin(args["nome"], args["email"], args["password"])
			admin.add(admin)
			query = Admin.query.get(admin.id)
		except SQLAlchemyError as e:
			return rollback(e, db)
		else:
			return schema.dump(query).data, 201
