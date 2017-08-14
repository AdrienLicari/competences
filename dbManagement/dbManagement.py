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


## Création du schéma si besoin est (généralement pour les tests)

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
    c.execute(str_tablesimple('competenceChapitre'))
    c.execute(str_tableCompetences)

## Ajout / retrait dans une table

def ajouteDansTable(conn:s.Connection, table:str, vals:dict) -> None:
    """
    Permet d'ajouter une ligne dans une table, éventuellement reliée à d'autres tables.
    Args:
        conn: l'objet sqlite3.Connection permettant d'accéder à la BDD
        table: str représentant le nom de la table
        vals: dictionnaire correspondant aux entrées ; la clé est le nom du champs, la valeur est
                la valeur à insérer OU un tuple (autreTable,champ,nom) permettant de récupérer un id
                relié en vue de jointures
    """
    c = conn.cursor()
    str_champs, str_valeurs = """(""","""("""
    for champ,valeur in vals.items():
        str_champs += """{},""".format(champ)
        if isinstance(valeur,tuple):  # cas où l'élément est en lien avec une autre table
            autreTable, autreChamp, autreValeur = valeur
            if isinstance(autreValeur,str):
                c.execute("""select id from {} where {} is "{}";""".format(autreTable,autreChamp,autreValeur))
            else:
                c.execute("""select id from {} where {} is {};""".format(autreTable,autreChamp,autreValeur))
            autreId = c.fetchall()[0][0]
            str_valeurs += """{},""".format(autreId)
        else:
            if isinstance(valeur,str):
                str_valeurs += """"{}",""".format(valeur)
            else:
                str_valeurs += """{},""".format(valeur)
    str_requete = """insert into {} """.format(table) + str_champs[:-1] + \
      """) values """ + str_valeurs[:-1] + """);"""
    c.execute(str_requete)
    conn.commit()

def retraitDeTable(conn:s.Connection, table:str, condition:tuple) -> None:
    """
    Retire des lignes dans une table. La condition SQL est une paire clé-valeur utilisée pour le retrait.
    """
    c = conn.cursor()
    c.execute("delete from {} where {} like '{}';".format(table,condition[0],condition[1]))
    conn.commit()

def récupèreChamps(conn:s.Connection, table:str, champs:list) -> list:
    """
    Fonction qui renvoie l'ensemble des champs demandés pour lignes de la table demandée.
    """
    c = conn.cursor()
    str_chps = ""
    for ch in champs:
        str_chps += "{},".format(ch)
    c.execute("select {} from {};".format(str_chps[:-1],table))
    a = [ t[0] for t in c.fetchall() ]
    return(a)


# Helpers
ajoutCompétenceType = lambda conn,nom: ajouteDansTable(conn,'competenceType',{'nom':nom})
retraitCompétenceType = lambda conn,nom: retraitDeTable(conn,'competenceType',('nom',nom))
récupèreCompétenceTypes = lambda conn: récupèreChamps(conn,'competenceType',['nom'])

ajoutCompétenceChapitre = lambda conn,nom: ajouteDansTable(conn,'competenceChapitre',{'nom':nom})
retraitCompétenceChapitre = lambda conn,nom: retraitDeTable(conn,'competenceChapitre',('nom',nom))
récupèreCompétenceChapitres = lambda conn: récupèreChamps(conn,'competenceChapitre',['nom'])

ajoutCompétence = lambda conn,nom,chap,typ: \
  ajouteDansTable(conn,'competence',\
                      {'nom':nom,\
                        'competenceTypeId':('competenceType','nom',typ),\
                        'competenceChapitreId':('competenceChapitre','nom',chap)})
retraitCompétence = lambda conn,nom: retraitDeTable(conn,'competence',('nom',nom))
récupèreCompétences = lambda conn: récupèreChamps(conn,'competence',['nom'])

def récupèreCompétencesComplet(conn:s.Connection) -> list:
    """
    Fonction qui renvoie les str correspondant aux compétences, avec à chaque fois leur type et chapitre
    associé
    """
    c = conn.cursor()
    sql_str = "select competence.nom,competenceType.nom,competenceChapitre.nom " + \
      "from competence join competenceType on competenceTypeId = competenceType.id " + \
      "join competenceChapitre on competenceChapitreId = competenceChapitre.id;"
    c.execute(sql_str)
    a = [ list(t) for t in c.fetchall()]
    return(a)



## Partie main pour tests

def afficherSéparateur() -> None:
    """ Fonction utilitaire pour l'affichage des tests """
    print("="*70)

if __name__ == '__main__':
    # test d'ouverture et affichage du schema
    afficherSéparateur()
    print("\t=== Nettoyage et initialisation de la base de tests ===")
    nom_db = 'competences_test.db'
    conn = ouvrirDB(nom_db)
    afficherSéparateur()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for tab in ['competence','competenceType','competenceChapitre']:
        try:
            c.execute("DROP table {};".format(tab))
        except:
            pass
    créerSchéma(conn)
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    a = c.fetchall()  # forme non simplement utilisable des noms des tables
    a = [ t[0] for t in a[1:] ]  # on enlève la table sqlite_sequence et on extrait les noms
    print("\t=== Liste des tables dans la DB ===\n", a)
    for tab in a:
        c.execute("pragma table_info({})".format(tab))
        cols = c.fetchall()
        print("** Liste des colonnes de la table {} :".format(tab))
        for col in cols:
            print("\t * {}".format(col))
    afficherSéparateur()
    # Test de gestion de la table des types de compétences
    print("\t=== Test de l'interface avec la table compétenceType ===")
    tab = ['technique','analyse','connaissance']
    print("lignes existantes :",récupèreCompétenceTypes(conn))
    for compTp in tab:
        ajoutCompétenceType(conn,compTp)
    print("lignes existantes :",récupèreCompétenceTypes(conn))
    retraitCompétenceType(conn,'technique')
    print("lignes existantes :",récupèreCompétenceTypes(conn))
    for t in récupèreCompétenceTypes(conn):
        retraitCompétenceType(conn,t)
    for compTp in tab:
        ajoutCompétenceType(conn,compTp)
    afficherSéparateur()
    # Test de gestion de la table des chapitres de compétences
    print("\t=== Test de l'interface avec la table compétenceChapitre ===")
    tab = ['généralités','mécanique','transformations chimiques']
    print("lignes existantes :",récupèreCompétenceChapitres(conn))
    for compTp in tab:
        ajoutCompétenceChapitre(conn,compTp)
    print("lignes existantes :",récupèreCompétenceChapitres(conn))
    retraitCompétenceChapitre(conn,'mécanique')
    print("lignes existantes :",récupèreCompétenceChapitres(conn))
    for t in récupèreCompétenceChapitres(conn):
        retraitCompétenceChapitre(conn,t)
    for compTp in tab:
        ajoutCompétenceChapitre(conn,compTp)
    afficherSéparateur()
    # Test de la table tableComplexeTest, uniquement pour tester indépendamment
    # la capacité à insérer sans lien avec d'autres tables
    print("\t=== Test de l'interface avec la table tableComplexeTest ===")
    try:
        str_tableComplexeTest = "create table tableComplexeTest (id integer primary key autoincrement, nom text, num int, chiffre real);"
        c.execute(str_tableComplexeTest)
    except Exception as ex:
        print("Info : Message d'exception reçu à la tentative de créer la table tableComplexeTest")
#        print('\t'+ex)
    tab = [{'nom':'pouet','num':3,'chiffre':42.0},\
               {'nom':'bidule','num':1,'chiffre':4.6},\
               {'nom':'truc','num':42,'chiffre':0.01}]
    for d in tab:
        ajouteDansTable(conn,'tableComplexeTest',d)
    conn.commit()
    c.execute("select * from tableComplexeTest;")
    print("Contenu de la table tableComplexeTest après ajouts :")
    for tu in c.fetchall():
        print(tu)
    c.execute("drop table tableComplexeTest;")
    afficherSéparateur()
    # Test des insertions avec liens entre tables
    print("\t=== Test de l'interface avec competences ===")
    ajoutCompétence(conn,"Vérifier l'homogénéité","généralités","technique")
    ajoutCompétence(conn,"Écrire la loi de Newton","mécanique","technique")
    ajoutCompétence(conn,"Interpréter une mouvement par principe d'inertie","mécanique","analyse")
    c.execute("select * from competence;")
    print("Contenu de la table competence après ajouts :")
    for tu in c.fetchall():
        print(tu)
    retraitCompétence(conn,"Écrire la loi de Newton")
    c.execute("select * from competence;")
    print("Contenu de la table competence après un retrait :")
    for tu in c.fetchall():
        print(tu)
    ajoutCompétence(conn,"Écrire la loi de Newton","mécanique","technique")
    try:
        ajoutCompétence(conn,"Vérifier l'homogénéité","généralités","pouet")
    except Exception as ex:
        print("Exception levée dans le cas d'une clé externe fantaisiste")
    print("lignes existantes :",récupèreCompétences(conn))
    print("récupération des infos liées:")
    for a in récupèreCompétencesComplet(conn):
        print(a)
    afficherSéparateur()
    fermerDB(conn)
