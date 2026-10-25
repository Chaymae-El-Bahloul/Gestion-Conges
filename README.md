<div align="center">

# Gestion des Demandes de Congé

### Du formulaire papier à la signature numérique : le circuit des congés, simplifié.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Base_de_données-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

*Une application web pour déposer, valider et signer les demandes de congé du personnel,<br>calculer automatiquement les jours ouvrés et suivre les soldes en temps réel.*

<br>

![Aperçu de l'application](assets/apercu.png)

</div>

---

## Sommaire

- [Le point de départ](#le-point-de-départ)
- [Ce que vous pouvez faire](#ce-que-vous-pouvez-faire)
- [Circuit de validation](#circuit-de-validation)
- [Règles de gestion](#règles-de-gestion)
- [Démarrage rapide](#démarrage-rapide)
- [Comptes de démonstration](#comptes-de-démonstration)
- [Structure du projet](#structure-du-projet)
- [Technologies](#technologies)
- [Pistes d'amélioration](#pistes-damélioration)
- [Licence](#licence)
- [Auteure](#auteure)

---

## Le point de départ

Dans une administration, une demande de congé passe de main en main : formulaire papier, vérification du solde, visa du service des Ressources Humaines, signature du Directeur. Chaque étape prend du temps et le suivi est difficile.

Ce projet a été réalisé dans le cadre d'un **stage de découverte à la Commune d'El Kelaa des Sraghna**. Il numérise ce circuit et répond à quatre besoins concrets :

| Le besoin | Ce que l'application apporte |
|---|---|
| **Déposer une demande** | Un formulaire en ligne, avec calcul automatique de la durée en jours ouvrés |
| **Contrôler le solde** | Un refus automatique si la durée dépasse le solde restant |
| **Valider et signer** | Un circuit en deux étapes : RH puis Directeur |
| **Suivre l'activité** | Des indicateurs, un historique et la liste des agents en congé |

---

## Ce que vous pouvez faire

### Trois profils, trois interfaces

| Profil | Fonctionnalités |
|---|---|
| **Employé** | Déposer une demande (type de congé, dates, représentant), consulter son solde, suivre l'état de ses demandes, accéder à son historique |
| **Ressources Humaines** | Consulter toutes les demandes, valider ou refuser, transmettre au Directeur, gérer les jours fériés, consulter les congés en cours et à venir |
| **Directeur** | Signer ou refuser les demandes, gérer les jours fériés, consulter les congés en cours et à venir |

### Les quatre indicateurs du tableau de bord

| Indicateur | Ce qu'il mesure |
|---|---|
| **Total** | Le nombre de demandes |
| **En attente** | Les demandes non encore traitées |
| **Approuvées** | Les demandes validées ou signées |
| **Refusées** | Les demandes rejetées par le RH ou le Directeur |

---

## Circuit de validation

```
Employé      ->  dépose la demande          ->  En attente
RH           ->  valide la demande          ->  En attente signature
Directeur    ->  signe la demande           ->  Signée (solde mis à jour)

À chaque étape, un refus est possible       ->  Refusée par RH / Refusée par Directeur
```

---

## Règles de gestion

<details>
<summary><b>Voir les règles appliquées par l'application</b></summary>

<br>

| Règle | Détail |
|---|---|
| **Jours ouvrés** | Les samedis, dimanches et jours fériés ne sont pas décomptés |
| **Contrôle du solde** | Une demande dont la durée dépasse le solde restant est refusée à la saisie |
| **Mise à jour du solde** | Le solde est décrémenté uniquement à la signature du Directeur |
| **Jours fériés** | Les fêtes nationales fixes de 2024 et 2025 sont préchargées ; le RH et le Directeur peuvent en ajouter ou en supprimer |
| **Contrôle d'accès** | Chaque route est protégée par l'authentification et limitée aux rôles autorisés |
| **Mots de passe** | Stockés sous forme hachée, jamais en clair |

</details>

> Les fêtes religieuses, dont les dates varient selon le calendrier hégirien, ne sont pas préchargées. Elles doivent être ajoutées manuellement depuis la page de gestion des jours fériés.

---

## Démarrage rapide

Prérequis : Python 3.10 ou supérieur et Git.

```bash
# 1. Cloner le dépôt
git clone https://github.com/Chaymae-El-Bahloul/Gestion-Conges.git
cd Gestion-Conges

# 2. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python main.py
```

L'application s'ouvre sur **http://127.0.0.1:5001**.

Au premier lancement, la base de données, les comptes de démonstration et les jours fériés par défaut sont créés automatiquement.

---

## Comptes de démonstration

| Profil | Matricule | Mot de passe |
|---|---|---|
| Employé | `EMP001` | `123456` |
| Ressources Humaines | `RH001` | `123456` |
| Directeur | `DIR001` | `123456` |

> Ces comptes servent uniquement aux tests. Ils doivent être supprimés ou modifiés avant tout déploiement réel.

---

## Structure du projet

```
.
├── main.py                  # Application Flask : modèles, routes, logique métier
├── requirements.txt         # Dépendances Python
├── templates/               # Pages HTML (Jinja2)
│   ├── login.html
│   ├── dashboard.html
│   ├── history.html
│   ├── jours_feries.html
│   └── liste_conges.html
├── static/
│   └── css/style.css        # Feuille de style
├── interfaces/              # Notes de conception des interfaces
├── assets/                  # Captures d'écran
├── LICENSE                  # Licence MIT
└── README.md
```

La base SQLite (`instance/demandes.db`) est générée automatiquement et n'est pas versionnée.

**API disponible :** `GET /api/jours-feries` retourne la liste des jours fériés au format JSON.

---

## Technologies

| Outil | Rôle |
|---|---|
| **Python** | Langage principal |
| **Flask** | Framework web et routage |
| **Flask-SQLAlchemy** | Modèles de données et accès à la base |
| **Flask-Login** | Authentification et gestion des sessions |
| **Werkzeug** | Hachage et vérification des mots de passe |
| **SQLite** | Base de données embarquée |
| **Jinja2 / CSS** | Pages et mise en forme |

---

## Pistes d'amélioration

- [ ] Génération des décisions en PDF (décision administrative interne et décision remise à l'employé)
- [ ] Ajout d'une pièce justificative et d'un motif à la demande
- [ ] Commentaire du Directeur en cas de refus
- [ ] Gestion des utilisateurs depuis l'interface (création, modification, suppression)
- [ ] Clé secrète et configuration via des variables d'environnement
- [ ] Jours fériés religieux selon le calendrier hégirien
- [ ] Notifications par e-mail à chaque changement d'état
- [ ] Déploiement sur un serveur de la commune

Une idée en plus ? Ouvrez une *issue* ou proposez une *pull request*.

---

## Licence

Ce projet est distribué sous licence **MIT** : vous pouvez l'utiliser, le modifier et le redistribuer librement, à condition de conserver la mention de copyright. Voir le fichier [LICENSE](LICENSE) pour le texte complet.

---

<div align="center">

## Auteure

**Chaymae El Bahloul**
Stagiaire, Commune d'El Kelaa des Sraghna
Encadrant : **Soufiane Mouchtabih**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-chaymae--el--bahloul-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/chaymae-el-bahloul)
[![GitHub](https://img.shields.io/badge/GitHub-Chaymae--El--Bahloul-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Chaymae-El-Bahloul)

*Si ce projet vous a plu, laissez une étoile sur le dépôt.*

</div>
