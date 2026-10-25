from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.secret_key = "vraiment-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demandes.db'
db = SQLAlchemy(app)

# Jours fériés marocains (exemple, à compléter)
JOURS_FERIES = [
    date(2024, 1, 1),  # Nouvel an
    date(2024, 5, 1),  # Fête du travail
    # ... autres jours fériés marocains
]

def jours_ouvres(date_debut, date_fin):
    jours = 0
    current = date_debut
    # Récupérer les jours fériés depuis la base de données
    jours_feries_db = [jf.date for jf in JourFerie.query.all()]
    while current <= date_fin:
        if current.weekday() not in (5, 6) and current not in jours_feries_db:
            jours += 1
        current += timedelta(days=1)
    return jours

# Modèles
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(100))
    echell = db.Column(db.String(20))
    rang = db.Column(db.String(20))
    telephone = db.Column(db.String(20))
    solde_conges = db.Column(db.Integer, default=30)
    
    # Relation avec les demandes de congé
    demandes = relationship("DemandeConge", backref="user", lazy="dynamic")

class DemandeConge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    jours = db.Column(db.Integer, nullable=False)
    etat = db.Column(db.String(50), default="En attente")
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    type_conge = db.Column(db.String(50), default="Annuel")
    representant = db.Column(db.String(100))

class JourFerie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialisation de la base (à faire une seule fois)
def create_tables():
    db.create_all()
    # Comptes de test (à ne faire qu'une fois)
    if not User.query.filter_by(matricule="EMP001").first():
        db.session.add(User(
            matricule="EMP001",
            password=generate_password_hash("123456"),
            role="employe",
            name="Salma Benali",
            service="Service Administratif",
            echell="10",
            rang="9",
            telephone="0612345678",
            solde_conges=22
        ))
        db.session.add(User(
            matricule="RH001",
            password=generate_password_hash("123456"),
            role="rh",
            name="Marie Dupont",
            service="Ressources Humaines",
            echell="11",
            rang="Chef de service",
            telephone="0623456789"
        ))
        db.session.add(User(
            matricule="DIR001",
            password=generate_password_hash("123456"),
            role="directeur",
            name="Jean Martin",
            service="Direction Générale",
            echell="12",
            rang="Directeur",
            telephone="0634567890"
        ))
        
        # Ajouter quelques jours fériés marocains par défaut
        jours_feries_defaut = [
            (date(2024, 1, 1), "Nouvel an"),
            (date(2024, 1, 11), "Manifeste de l'indépendance"),
            (date(2024, 5, 1), "Fête du travail"),
            (date(2024, 7, 30), "Fête du trône"),
            (date(2024, 8, 14), "Oued Ed-Dahab"),
            (date(2024, 8, 20), "Révolution du roi et du peuple"),
            (date(2024, 8, 21), "Fête de la jeunesse"),
            (date(2024, 11, 6), "Marche verte"),
            (date(2024, 11, 18), "Fête de l'indépendance"),
            (date(2025, 1, 1), "Nouvel an"),
            (date(2025, 1, 11), "Manifeste de l'indépendance"),
            (date(2025, 5, 1), "Fête du travail"),
            (date(2025, 7, 30), "Fête du trône"),
            (date(2025, 8, 14), "Oued Ed-Dahab"),
            (date(2025, 8, 20), "Révolution du roi et du peuple"),
            (date(2025, 8, 21), "Fête de la jeunesse"),
            (date(2025, 11, 6), "Marche verte"),
            (date(2025, 11, 18), "Fête de l'indépendance"),
        ]
        
        for date_jf, description in jours_feries_defaut:
            if not JourFerie.query.filter_by(date=date_jf).first():
                db.session.add(JourFerie(date=date_jf, description=description))
        
        db.session.commit()

# Appel de l'initialisation au démarrage
with app.app_context():
    create_tables()

@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        matricule = request.form["matricule"]
        password = request.form["password"]
        user = User.query.filter_by(matricule=matricule).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session["role"] = user.role
            session["name"] = user.name
            return redirect(url_for("dashboard"))
        else:
            error = "Matricule ou mot de passe incorrect."
    return render_template("login.html", error=error)

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    role = session["role"]
    user = current_user
    user_name = session.get("name", "")
    if role == "employe":
        demandes = DemandeConge.query.filter_by(user_id=user.id).all()
        solde = user.solde_conges
    else:
        # Pour RH et Directeur, charger toutes les demandes avec les utilisateurs
        demandes = DemandeConge.query.all()
        solde = None
    
    stats = {
        "total": len(demandes),
        "en_attente": sum(1 for d in demandes if d.etat == "En attente"),
        "approuvees": sum(1 for d in demandes if "Validée" in d.etat or "Signée" in d.etat),
        "refusees": sum(1 for d in demandes if "Refusée" in d.etat),
    }
    return render_template("dashboard.html", role=role, user_name=user_name, stats=stats, demandes=demandes, solde=solde)

@app.route("/demande", methods=["POST"])
@login_required
def demande():
    if session["role"] != "employe":
        return redirect(url_for("login"))
    user = current_user
    nb_jours_souhaites = int(request.form.get("nb_jours", 0))
    date_debut_str = request.form["date_debut"]
    date_fin_str = request.form["date_fin"]
    type_conge = request.form.get("type_conge", "Annuel")
    date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
    date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()
    duree = jours_ouvres(date_debut, date_fin)
    if duree > user.solde_conges:
        role = session["role"]
        user_name = session.get("name", "")
        demandes = DemandeConge.query.filter_by(user_id=user.id).all()
        stats = {
            "total": len(demandes),
            "en_attente": sum(1 for d in demandes if d.etat == "En attente"),
            "approuvees": sum(1 for d in demandes if "Validée" in d.etat or "Signée" in d.etat),
            "refusees": sum(1 for d in demandes if "Refusée" in d.etat),
        }
        error = "Vous ne pouvez pas demander plus de jours que votre solde restant."
        return render_template("dashboard.html", role=role, user_name=user_name, stats=stats, demandes=demandes, solde=user.solde_conges, error=error)
    if user and duree > 0:
        representant = request.form.get("representant", "")
        new_demande = DemandeConge(
            user_id=user.id,
            jours=duree,
            etat="En attente",
            date_debut=date_debut,
            date_fin=date_fin,
            type_conge=type_conge,
            representant=representant
        )
        db.session.add(new_demande)
        db.session.commit()
    role = session["role"]
    user_name = session.get("name", "")
    demandes = DemandeConge.query.filter_by(user_id=user.id).all()
    stats = {
        "total": len(demandes),
        "en_attente": sum(1 for d in demandes if d.etat == "En attente"),
        "approuvees": sum(1 for d in demandes if "Validée" in d.etat or "Signée" in d.etat),
        "refusees": sum(1 for d in demandes if "Refusée" in d.etat),
    }
    return render_template("dashboard.html", role=role, user_name=user_name, stats=stats, demandes=demandes, duree=duree, nb_jours_souhaites=nb_jours_souhaites)

@app.route("/valider", methods=["POST"])
@login_required
def valider():
    if session["role"] not in ["rh", "directeur"]:
        return redirect(url_for("login"))
    
    try:
        matricule = request.form["matricule"]
        jours = int(request.form["jours"])
        action = request.form["action"]
        
        user = User.query.filter_by(matricule=matricule).first()
        if user:
            # Chercher la demande la plus récente de cet utilisateur avec ce nombre de jours
            demande = DemandeConge.query.filter_by(
                user_id=user.id, 
                jours=jours
            ).order_by(DemandeConge.date_creation.desc()).first()
            
            if demande:
                if action == "valider":
                    if session["role"] == "rh" and demande.etat == "En attente":
                        demande.etat = "En attente signature"
                    elif session["role"] == "directeur":
                        if demande.etat == "En attente":
                            demande.etat = "Signée"
                            # Décrémenter le solde de congés
                            if user.solde_conges is not None:
                                user.solde_conges = max(0, user.solde_conges - demande.jours)
                        elif demande.etat == "En attente signature":
                            demande.etat = "Signée"
                            if user.solde_conges is not None:
                                user.solde_conges = max(0, user.solde_conges - demande.jours)
                else:
                    demande.etat = f"Refusée par {session['role'].capitalize()}"
                db.session.commit()
    except Exception as e:
        print(f"Erreur lors de la validation: {e}")
    
    return redirect(url_for("dashboard"))

@app.route("/history")
@login_required
def history():
    user = current_user
    demandes = DemandeConge.query.filter_by(user_id=user.id).order_by(DemandeConge.date_creation.desc()).all()
    return render_template("history.html", demandes=demandes)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("login"))

@app.route("/jours-feries")
@login_required
def jours_feries():
    if session["role"] not in ["rh", "directeur"]:
        return redirect(url_for("dashboard"))
    jours_feries_list = JourFerie.query.order_by(JourFerie.date).all()
    return render_template("jours_feries.html", jours_feries=jours_feries_list)

@app.route("/ajouter-jour-ferie", methods=["POST"])
@login_required
def ajouter_jour_ferie():
    if session["role"] not in ["rh", "directeur"]:
        return redirect(url_for("dashboard"))
    date_str = request.form["date"]
    description = request.form["description"]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    nouveau_jour = JourFerie(date=date_obj, description=description)
    db.session.add(nouveau_jour)
    db.session.commit()
    return redirect(url_for("jours_feries"))

@app.route("/supprimer-jour-ferie/<int:id>")
@login_required
def supprimer_jour_ferie(id):
    if session["role"] not in ["rh", "directeur"]:
        return redirect(url_for("dashboard"))
    jour = JourFerie.query.get_or_404(id)
    db.session.delete(jour)
    db.session.commit()
    return redirect(url_for("jours_feries"))

@app.route("/liste-conges")
@login_required
def liste_conges():
    """Afficher la liste des employés en congé"""
    if session["role"] not in ["rh", "directeur"]:
        return redirect(url_for("dashboard"))
    
    # Récupérer toutes les demandes approuvées (Signée)
    demandes_approuvees = DemandeConge.query.filter(
        DemandeConge.etat == "Signée"
    ).join(User).order_by(DemandeConge.date_debut).all()
    
    # Filtrer les congés en cours (date actuelle entre début et fin)
    aujourd_hui = date.today()
    congés_en_cours = []
    congés_futurs = []
    
    for demande in demandes_approuvees:
        if demande.date_debut <= aujourd_hui <= demande.date_fin:
            congés_en_cours.append(demande)
        elif demande.date_debut > aujourd_hui:
            congés_futurs.append(demande)
    
    return render_template("liste_conges.html", 
                         congés_en_cours=congés_en_cours,
                         congés_futurs=congés_futurs,
                         aujourd_hui=aujourd_hui)

@app.route("/api/jours-feries")
def api_jours_feries():
    """API pour récupérer les jours fériés en JSON"""
    jours_feries = JourFerie.query.all()
    return {
        "jours_feries": [
            {
                "date": jf.date.strftime("%Y-%m-%d"),
                "description": jf.description
            }
            for jf in jours_feries
        ]
    }

if __name__ == "__main__":
    app.run(debug=True, port=5001)