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
    str_tableÉtudiants = "CREATE TABLE etudiants" + \
      "(id integer primary key autoincrement, classeId int, nom text, prenom text, " + \
      "foreign key(classeId) references classes(id));"
    str_tableDevoirs = "CREATE TABLE devoir " + \
      "(id integer primary key autoincrement, classeId int, typeId int, numero int, date text, " + \
      "foreign key(typeId) references devoirType(id), foreign key(classeId) references classes(id));"
    str_tableQuestions = "CREATE TABLE questions " + \
      "(id integer primary key autoincrement, devoirId int, nom text, coefficient int, " + \
      "foreign key(devoirId) references devoir(id));"
    str_tableQuestionsCompétences = "CREATE TABLE questionsCompetences " + \
      "(id integer primary key autoincrement, questionsId int, competenceId int, " + \
      "foreign key(questionsId) references questions(id), foreign key(competenceId) references competence(id));"
    # lancement des requêtes
    c.execute(str_tablesimple('competenceType'))
    c.execute(str_tablesimple('competenceChapitre'))
    c.execute(str_tableCompetences)
    c.execute(str_tablesimple('classes'))
    c.execute(str_tableÉtudiants)
    c.execute(str_tablesimple('devoirType'))
    c.execute(str_tableDevoirs)
    c.execute(str_tableQuestions)
    c.execute(str_tableQuestionsCompétences)


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

def récupèreChamps(conn:s.Connection, table:str, champs:list, orderby:str = None) -> list:
    """
    Fonction qui renvoie l'ensemble des champs demandés pour lignes de la table demandée.
    """
    c = conn.cursor()
    str_chps = ""
    for ch in champs:
        str_chps += "{},".format(ch)
    str_sql = "select {} from {};".format(str_chps[:-1],table)
    if orderby is not None:
        str_sql = str_sql[:-1] + " order by {};".format(orderby)
    c.execute(str_sql)
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

ajoutClasse = lambda conn,nom: ajouteDansTable(conn,'classes',{'nom':nom})
retraitClasse = lambda conn,nom: retraitDeTable(conn,'classes',('nom',nom))
récupèreClasses = lambda conn: récupèreChamps(conn,'classes',['nom'])

ajoutÉtudiant = lambda conn,nom,prenom,classe: ajouteDansTable(conn,'etudiants', \
                                                         {'nom':nom,'prenom':prenom, \
                                                              'classeId':('classes','nom',classe)})
def ajoutListeÉtudiants(conn:s.Connection, liste:list, nomClasse:str) -> None:
    """
    Ajoute une liste complète d'étudiants dans la classe proposée. La liste contient des
    paires (nom,prenom)
    """
    for nom,prenom in liste:
        ajoutÉtudiant(conn,nom,prenom,nomClasse)

retraitÉtudiant = lambda conn,nom: retraitDeTable(conn,'etudiants',('nom',nom))
def récupèreÉtudiants(conn:s.Connection,classe:str) -> list:
    """ Fonction qui récupère l'ensemble des étudiants d'une classe """
    c = conn.cursor()
    sql_str = "select etudiants.nom,etudiants.prenom from etudiants join classes on classeId = classes.id " + \
      "where classes.nom like '{}' order by etudiants.nom;".format(classe)
    c.execute(sql_str)
    a = [ "{} {}".format(t[1],t[0]) for t in c.fetchall() ]
    return(a)

ajoutTypeDevoir = lambda conn,nom: ajouteDansTable(conn,'devoirType',{'nom':nom})
récupèreTypesDevoirs = lambda conn: récupèreChamps(conn,'devoirType',['nom'])
ajoutDevoir = lambda conn,typ,numero,date,classe: \
  ajouteDansTable(conn,'devoir',{'numero':numero,'date':date, \
                                     'typeId':('devoirType','nom',typ),'classeId':('classes','nom',classe)})
def récupèreDevoirs(conn:s.Connection) -> list:
    """ Fonction qui récupère l'ensemble des devoirs """
    c = conn.cursor()
    sql_str = "select devoir.numero,devoirType.nom,classes.nom,devoir.date from devoir " + \
      "join classes on classeId = classes.id join devoirType on classeId = classes.id " + \
      "order by devoir.date;"
    c.execute(sql_str)
    a = [ list(t)[1:] for t in c.fetchall() ]
    return(a)

def créerQuestions(conn:s.Connection, devoir:int, liste:list) -> None:
    """
    Prend en paramètre une liste de tuples (nomDeQuestion,coef,[compétences]).
    Le devoir est identifié par son numéro id.
    """
    c = conn.cursor()
    for q in liste:
        ajouteDansTable(conn,"questions",{'nom':q[0],'coefficient':q[1],'devoirId':devoir})
        c.execute("select id from questions where nom like '{}';".format(q[0]))
        q_id = c.fetchall()[0][0]
        for comp in q[2]:
            ajouteDansTable(conn,"questionsCompetences",{"questionsId":q_id,"competenceId":comp})
def récupérerQuestions(conn:s.Connection, devoir:int) -> list:
    """
    Prend en paramètre un id de devoir et renvoie la liste des questions, coefficients et compétences associées
    """
    c = conn.cursor()
    c.execute("select id,nom,coefficient from questions where devoirId = {};".format(devoir))
    l = [ list(t) for t in c.fetchall() ]
    for a in l:
        c.execute("select competenceId from questionsCompetences where questionsId = {};".format(a[0]))
        a.append([t[0] for t in c.fetchall()])
    return(l)

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
    # Tables des classes et des élèves
    print("\t=== Test de l'interface avec les classes et les étudiants ===")
    ajoutClasse(conn,"MPSI")
    ajoutClasse(conn,"MP")
    ajoutClasse(conn,"PSI")
    print("classes existantes :",récupèreClasses(conn))
    retraitClasse(conn,"PSI")
    print("classes existantes après retrait de la PSI :",récupèreClasses(conn))
    listeDépart = [('Alp','Selin'), ('Gourgues','Maxime'), ('Morceaux','Jérémy')]
    ajoutListeÉtudiants(conn,listeDépart,'MPSI')
    print("Étudiants dans la MPSI :",récupèreÉtudiants(conn,"MPSI"))
    ajoutÉtudiant(conn,"Bazin","Jérémy","MPSI")
    retraitÉtudiant(conn,"Gourgues")
    print("Nouveaux étudiants dans la MPSI :",récupèreÉtudiants(conn,"MPSI"))
    afficherSéparateur()
    # Tables des devoirs
    print("\t=== Test de l'interface avec les devoirs ===")
    ajoutTypeDevoir(conn,'DS')
    ajoutTypeDevoir(conn,'Interro')
    print("Les types de devoirs accessibles sont :", récupèreTypesDevoirs(conn))
    ajoutDevoir(conn,"DS",1,"20.09.2017","MPSI")
    ajoutDevoir(conn,"DS",2,"20.10.2017","MPSI")
    ajoutDevoir(conn,"Interro",1,"15.09.2017","MPSI")
    print("Liste des devoirs :", récupèreDevoirs(conn))
    questions = [('1.a',2,[1,3]),('1.b',1,[1,4]),('2',2,[1])]
    créerQuestions(conn,1,questions)
    print(récupérerQuestions(conn,1))
    afficherSéparateur()
    fermerDB(conn)
