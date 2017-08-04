#!/usr/bin/ipython3

"""
Module permettant de communiquer avec la base de données gérée en SQLite.
Les fonctions fournies par ce module sont adaptées aux besoins du code général.
"""

## imports
import sqlite3 as s


## Fonction d'ouverture / fermeture

def ouvrirDB(filename:str) -> s.Connection:
    """
    Fonction qui ouvre la base de données et renvoie un connecteur.
    Assure la configuration souhaitée de SQLite :
    - support des foreign keys
    """
    conn = s.connect(filename)
    c = conn.cursor()
    c.execute("pragma foreign_keys = on;")
    conn.commit()
    return(conn)

def fermerDB(conn:s.Connection) -> None:
    """
    Fonction qui ferme la base de données en fin de programme.
    Il n'est a priori pas nécessaire de l'appeler manuellement, fournie en cas de besoin.
    """
    conn.close()


## Création du schéma si besoin est

def créerSchéma(conn:s.Connection) -> None:
    """
    Fonction qui permet de créer intégralement un schéma adapté au suivi des compétences.
    """
    c = conn.cursor()
    # création des requêtes SQL
    str_tablesimple = lambda nom: "create table {}".format(nom) + \
      "(id integer primary key autoincrement, nom text);"
    str_tableCompetences = "CREATE TABLE competence" + \
      "(id integer primary key autoincrement, nom text, competenceTypeId int, competenceChapitreId int," + \
      "foreign key(competenceTypeId) references competenceType(id), foreign key(competenceChapitreId) references competenceChapitre(id));"
    # lancement des requêtes
    c.execute(str_tablesimple('competenceType'))
    c.execute(str_tablesimple('competenceCahpitre'))
    c.execute(str_tableCompetences)

## Ajout / retrait / lecture dans les tables simples (juste une liste avec des noms) :
#      competenceType
#      competenceChapitre
#      classes
#      devoirType

def ajoutSimpleTable(conn:s.Connection, table:str, nom:str) -> None:
    """
    Fonction pour ajouter des entrées
    """
    c = conn.cursor()
    c.execute("insert into {} (nom) values ('{}');".format(table,nom))
    conn.commit()

def retraitSimpleTable(conn:s.Connection, table:str, nom:str) -> None:
    """
    Fonction pour retirer des types de compétences
    """
    c = conn.cursor()
    c.execute("delete from {} where nom like '{}';".format(table,nom))
    conn.commit()

def récupèreSimpleTable(conn:s.Connection, table:str) -> list:
    """
    Fonction qui renvoie l'ensemble des types de compétences dans une liste de str
    """
    c = conn.cursor()
    c.execute("select nom from {};".format(table))
    a = [ t[0] for t in c.fetchall() ]
    return(a)

# Helpers
ajoutCompétenceType = lambda conn,nom: ajoutSimpleTable(conn,'competenceType',nom)
retraitCompétenceType = lambda conn,nom: retraitSimpleTable(conn,'competenceType',nom)
récupèreCompétenceTypes = lambda conn: récupèreSimpleTable(conn,'competenceType')


## Partie main pour tests

def afficherSéparateur() -> None:
    """ Fonction utilitaire pour l'affichage des tests """
    print("="*70)

if __name__ == '__main__':
    # test d'ouverture et affichage du schema
    nom_db = 'competences_test.db'
    conn = ouvrirDB(nom_db)
    créerSchéma(conn)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    a = c.fetchall()  # forme non simplement utilisable des noms des tables
    a = [ t[0] for t in a[1:] ]  # on enlève la table sqlite_sequence et on extrait les noms
    afficherSéparateur()
    print("Liste des tables dans la DB :\n", a)
    afficherSéparateur()
    for tab in a:
        c.execute("pragma table_info({})".format(tab))
        cols = c.fetchall()
        print("** Liste des colonnes de la table {} :".format(tab))
        for col in cols:
            print("\t * {}".format(col))
    afficherSéparateur()
    # Test de gestion de la table des types de compétences
    print("Test de l'interface avec la table connaissanceType")
    tab = ['technique','analyse','connaissance']
    print("lignes existantes :",récupèreCompétenceTypes(conn))
    for compTp in tab:
        ajoutCompétenceType(conn,compTp)
    print("lignes existantes :",récupèreCompétenceTypes(conn))
    retraitCompétenceType(conn,'technique')
    print("lignes existantes :",récupèreCompétenceTypes(conn))
    for t in récupèreCompétenceTypes(conn):
        retraitCompétenceType(conn,t)
    afficherSéparateur()
    fermerDB(conn)
