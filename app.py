from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

#inscripciones a los cursos
inscripciones = db.Table('inscripciones',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('curso_id', db.Integer, db.ForeignKey('curso.id'), primary_key=True)
)

#Modelos de Usuarios

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(60), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    profesion = db.Column(db.String(50), nullable=False)
    cursos = db.relationship('Curso', backref='alumno', lazy=True)
    #inscripciones
    cursos_inscritos = db.relationship('Curso', secondary=inscripciones, backref=db.backref('alumnos', lazy=True))

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tema = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    video_link = db.Column(db.String(200), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)







#Agregar curso Formulario

@app.route('/agregar_curso_form/<int:usuario_id>', methods=['GET', 'POST'])
def agregar_curso_form(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == 'POST':
        tema = request.form['tema']
        descripcion = request.form['descripcion']
        video_link = request.form['video_link']

        nuevo_curso = Curso(tema=tema, descripcion=descripcion, video_link=video_link, usuario_id=usuario.id)
        db.session.add(nuevo_curso)
        db.session.commit()

        return redirect(url_for('cursos', usuario_id=usuario.id))

    return render_template('agregar_curso.html', usuario=usuario)

#Homepage

@app.route('/')
def home():
    return render_template('home.html')

#Formulario de registro

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        contrasena = request.form['contrasena']
        edad = request.form['edad']
        telefono = request.form['telefono']
        profesion = request.form['profesion']

        nuevo_usuario = Usuario(nombre=nombre, apellido=apellido, email=email, contrasena=contrasena,
                                edad=edad, telefono=telefono, profesion=profesion)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('registro.html')

#Formulario de Login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']

        usuario = Usuario.query.filter_by(email=email, contrasena=contrasena).first()

        if usuario:
            return redirect(url_for('cursos', usuario_id=usuario.id))
        else:
            return "Credenciales inválidas. Inténtalo de nuevo."

    return render_template('login.html')



#Pagina de cursos
@app.route('/curso')
def cursos():
    return render_template('curso.html')


#Perfil formulario para modificar los datos del usuario

@app.route('/perfil/<int:usuario_id>', methods=['GET', 'POST'])
def perfil(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.apellido = request.form['apellido']
        usuario.email = request.form['email']
        usuario.contrasena = request.form['contrasena']
        usuario.edad = request.form['edad']
        usuario.telefono = request.form['telefono']
        usuario.profesion = request.form['profesion']
        db.session.commit()
        return redirect(url_for('cursos', usuario_id=usuario.id))

    return render_template('perfil.html', usuario=usuario)



#Pagina para ver los usuarios

@app.route("/usuarios", methods = ['GET'])
def usuarios():
    usuarios = db.session.execute(db.select(Usuario).order_by(Usuario.nombre)).scalars()
    print(usuarios)
    return render_template("usuarios.html", usuarios = usuarios)

#Pagina para ver los mentores
@app.route('/mentores', methods=['GET'])
def mentores():
    usuarios = db.session.execute(db.select(Usuario).order_by(Usuario.nombre)).scalars()
    print(usuarios)
    return render_template("mentores.html", usuarios = usuarios)

#Eliminar datos de la base de datos
@app.route("/eliminar/<int:id>", methods = ["GET" , "POST"])
def eliminar(id):
    if request.method == "POST":
        user = db.get_or_404(Usuario, id)
        db.session.delete(user)
        db.session.commit()
      #  db.session.delete()
    return redirect(url_for('usuarios'))




@app.route('/ver_detalles_curso/<int:curso_id>', methods=['GET', 'POST'])
def ver_detalles_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        usuario = Usuario.query.get(usuario_id)

        if usuario:
            usuario.cursos_inscritos.append(curso)
            db.session.commit()
            return redirect(url_for('cursos', usuario_id=usuario.id))
        else:
            return "Usuario no encontrado."

    return render_template('detalles_curso.html', curso=curso)

@app.route('/inscribirse_curso/<int:curso_id>', methods=['POST'])
def inscribirse_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    usuario_id = request.form['usuario_id']
    usuario = Usuario.query.get(usuario_id)

    if usuario:
        usuario.cursos_inscritos.append(curso)
        db.session.commit()
        return redirect(url_for('cursos', usuario_id=usuario.id))
    else:
        return "Usuario no encontrado."




#creamos la base de datos
with app.app_context():
    db.create_all()


#breakpoint
if __name__ == '__main__':
    app.run(debug=True, port=5500)