#!/usr/bin/ipython3

"""
Module permettant de communiquer avec la base de données gérée en SQLite.
Les fonctions fournies par ce module sont adaptées aux besoins du code général.
"""

## imports
import sqlite3 as s


## Classe gestionnaire de la base de données.
class BaseDeDonnées(object):
    """
    Classe gérant la base de données.
    """
    def __init__(self, filename:str):
        """
        Constructeur. Prend en paramètre le nom du fichier à utiliser.

        Assure la configuration souhaitée de SQLite :
        - support des foreign keys
        """
        self.conn = s.connect(filename)
        c = self.conn.cursor()
        c.execute("pragma foreign_keys = on;")
        self.conn.commit()

    def fermerDB(self) -> None:
        """
        Fonction qui ferme la base de données en fin de programme.
        Il n'est a priori pas nécessaire de l'appeler manuellement, fournie en cas de besoin.
        """
        self.conn.close()

    def créerSchéma(self) -> None:
        """
        Fonction qui permet de créer intégralement un schéma adapté au suivi des compétences.
        """
        c = self.conn.cursor()
        # création des requêtes SQL
        str_tablesimple = lambda nom: "create table {}".format(nom) + \
                          "(id integer primary key autoincrement, nom text);"
        str_tableCompetences = "CREATE TABLE competence" + \
                               "(id integer primary key autoincrement, nom text, " + \
                               "competenceTypeId int, competenceChapitreId int," + \
                               "foreign key(competenceTypeId) references competenceType(id), " + \
                               "foreign key(competenceChapitreId) references competenceChapitre(id));"
        str_tableÉtudiants = "CREATE TABLE etudiants" + \
                             "(id integer primary key autoincrement, classeId int, nom text, prenom text, " + \
                             "foreign key(classeId) references classes(id));"
        str_tableDevoirs = "CREATE TABLE devoir " + \
                           "(id integer primary key autoincrement, classeId int, " + \
                           "typeId int, numero int, date text, nvxAcq int," + \
                           "foreign key(typeId) references devoirType(id), " + \
                           "foreign key(classeId) references classes(id));"
        str_tableQuestions = "CREATE TABLE questions " + \
                             "(id integer primary key autoincrement, devoirId int, nom text, " + \
                             "foreign key(devoirId) references devoir(id));"
        str_tableQuestionsCompétences = "CREATE TABLE questionsCompetences " + \
                                        "(id integer primary key autoincrement, questionsId int, " + \
                                        "competenceId int, coefficient int," + \
                                        "foreign key(questionsId) references questions(id), " + \
                                        "foreign key(competenceId) references competence(id));"
        str_tableModificateursDevoir = "CREATE TABLE modificateursDevoir " + \
                                       "(id integer primary key autoincrement, devoirId int, " + \
                                       "typesModificateursÉvaluationId int, valeur float, nom text," + \
                                       "foreign key(devoirId) references devoir(id), " + \
                                       "foreign key(typesModificateursÉvaluationId) references " + \
                                       "typesModificateursÉvaluation(id));"
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
        c.execute(str_tablesimple("typesModificateursÉvaluation"))
        c.execute(str_tableModificateursDevoir)

    def ajouteDansTable(self, table:str, vals:dict) -> None:
        """
        Permet d'ajouter une ligne dans une table, éventuellement reliée à d'autres tables.
        Args:
        conn: l'objet sqlite3.Connection permettant d'accéder à la BDD
        table: str représentant le nom de la table
        vals: dictionnaire correspondant aux entrées ; la clé est le nom du champs, la valeur est
                la valeur à insérer OU un tuple (autreTable,champ,nom) permettant de récupérer un id
                relié en vue de jointures
        """
        c = self.conn.cursor()
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
        self.conn.commit()

    def retraitDeTable(self, table:str, conditions:dict) -> None:
        """
        Retire des lignes dans une table. La condition SQL est un dictionnaire contenant les paires
        clé-valeur utilisées pour choisir le retrait.
        """
        c = self.conn.cursor()
        str_retrait = "delete from {} where ".format(table)
        for key,val in conditions.items():
            if type(val) == str and "select" not in val:
                str_retrait += "{} like '{}' and ".format(key,val)
            else:
                str_retrait += "{} = {} and ".format(key,val)
        str_retrait = str_retrait[:-4] + ";"
        c.execute(str_retrait)
        self.conn.commit()

    def récupèreChamps(self, table:str, champs:list, orderby:str = None) -> list:
        """
        Fonction qui renvoie l'ensemble des champs demandés pour lignes de la table demandée.
        """
        c = self.conn.cursor()
        str_chps = ""
        for ch in champs:
            str_chps += "{},".format(ch)
        str_sql = "select {} from {};".format(str_chps[:-1],table)
        if orderby is not None:
            str_sql = str_sql[:-1] + " order by {};".format(orderby)
        c.execute(str_sql)
        a = [ {b:t for (b,t) in zip(champs,ligne)} for ligne in c.fetchall() ]
        return(a)

    def récupèreId(self, table:str, conditions:dict) -> int:
        """
        Renvoie l'id et le nom d'une entrée identifiée par un ensemble de conditions.
        """
        c = self.conn.cursor()
        str_récup = """select id from {} where """.format(table)
        for key,val in conditions.items():
            if type(val) == int:
                str_récup += "{} = {} and ".format(key,val)
            elif type(val) == str:
                str_récup += """{} like "{}" and """.format(key,val)
        str_récup = str_récup[:-4] + ";"
        c.execute(str_récup)
        return(c.fetchall()[0][0])

    # Une série de fonctions courtes pour les cas courants
    def ajoutCompétenceType(self, nom:str) -> None:
        self.ajouteDansTable('competenceType',{'nom':nom})

    def retraitCompétenceType(self, nom:str) -> None:
        self.retraitDeTable('competenceType',{'nom':nom})

    def récupèreCompétenceTypes(self) -> list:
        return(self.récupèreChamps('competenceType',['nom']))

    def ajoutCompétenceChapitre(self, nom:str) -> None:
        self.ajouteDansTable('competenceChapitre',{'nom':nom})

    def retraitCompétenceChapitre(self, nom:str) -> None:
        self.retraitDeTable('competenceChapitre',{'nom':nom})

    def récupèreCompétenceChapitres(self) -> list:
        return(self.récupèreChamps('competenceChapitre',['nom']))

    def ajoutCompétence(self, nom:str, chap:str, typ:str) -> None:
        vals = {'nom':nom, 'competenceTypeId':('competenceType','nom',typ), \
                  'competenceChapitreId':('competenceChapitre','nom',chap)}
        self.ajouteDansTable('competence', vals)

    def retraitCompétence(self, nom:str) -> None:
        self.retraitDeTable('competence',{'nom':nom})

    def récupèreCompétencesListe(self) -> list:
        """
        Fonction qui renvoie les str correspondant aux noms des compétences
        """
        return(self.récupèreChamps('competence',['nom']))

    def récupèreCompétencesComplet(self) -> list:
        """
        Fonction qui renvoie les str correspondant aux compétences, avec à chaque fois leur type et chapitre
        associés
        """
        c = self.conn.cursor()
        sql_str = "select competence.nom,competenceType.nom,competenceChapitre.nom " + \
                  "from competence join competenceType on competenceTypeId = competenceType.id " + \
                  "join competenceChapitre on competenceChapitreId = competenceChapitre.id;"
        c.execute(sql_str)
        a = [ {'nom':t[0],'type':t[1],'chapitre':t[2]} for t in c.fetchall()]
        return(a)

    def ajoutClasse(self, nom:str) -> None:
        self.ajouteDansTable('classes',{'nom':nom})

    def retraitClasse(self, nom:str) -> None:
        self.retraitDeTable('classes',{'nom':nom})

    def récupèreClasses(self) -> list:
        return(self.récupèreChamps('classes',['nom']))

    def ajoutÉtudiant(self, nom:str, prenom:str, classe:str) -> None:
        self.ajouteDansTable('etudiants', {'nom':nom,'prenom':prenom, 'classeId':('classes','nom',classe)})

    def ajoutListeÉtudiants(self, liste:list, nomClasse:str) -> None:
        """
        Ajoute une liste complète d'étudiants dans la classe proposée. La liste contient des
        paires (nom,prenom)
        """
        for nom,prenom in liste:
            self.ajoutÉtudiant(nom,prenom,nomClasse)

    def retraitÉtudiant(self, nom:str, prénom:str) -> None:
        self.retraitDeTable('etudiants',{'nom':nom, 'prenom':prénom})

    def récupèreÉtudiants(self, classe:str) -> list:
        """ Fonction qui récupère l'ensemble des étudiants d'une classe """
        c = self.conn.cursor()
        sql_str = "select etudiants.nom,etudiants.prenom from etudiants " + \
                  "join classes on classeId = classes.id " + \
                  "where classes.nom like '{}' order by etudiants.nom;".format(classe)
        c.execute(sql_str)
        a = [ {'nom':t[0], 'prenom':t[1]} for t in c.fetchall() ]
        return(a)

    def ajoutTypeDevoir(self, nom:str) -> None:
        self.ajouteDansTable('devoirType',{'nom':nom})

    def retraitTypeDevoir(self, nom:str) -> None:
        self.retraitDeTable('devoirType',{'nom':nom})

    def récupèreTypesDevoirs(self) -> list:
        return(self.récupèreChamps('devoirType',['nom']))

    def ajoutDevoir(self, typ:str, numero:int, date:str, classe:str, niveauxAcquisition:int=2) -> None:
        """
        Noter que la valeur par défaut des niveaux d'acquisition testés est 2 (acquis / non acquis)
        """
        self.ajouteDansTable('devoir',{'numero':numero, 'date':date, 'nvxAcq':niveauxAcquisition, \
                                       'typeId':('devoirType','nom',typ), 'classeId':('classes','nom',classe)})

    def retraitDevoir(self, idDevoir:int) -> None:
        self.retraitDeTable('devoir',{'id':idDevoir})

    def récupèreDevoirs(self) -> list:
        """ Fonction qui récupère l'ensemble des devoirs """
        c = self.conn.cursor()
        sql_str = "select devoir.id,classes.nom,devoirType.nom,devoir.numero,devoir.date,devoir.nvxAcq " + \
                  "from devoir join classes on classeId = classes.id " + \
                  "join devoirType on typeId = devoirType.id " + \
                  "order by devoir.date;"
        c.execute(sql_str)
        a = [ {'id':t[0],'classe':t[1],'type':t[2],'numéro':t[3],'date':t[4],'nvxAcq':t[5]} for t in c.fetchall() ]
        return(a)

    def créerQuestions(self, devoir:int, liste:list) -> None:
        """
        Prend en paramètre une liste de tuples (nomDeQuestion,[(compétence,coeff)]).
        Le devoir est identifié par son numéro id.
        """
        c = self.conn.cursor()
        for q in liste:
            self.ajouteDansTable("questions",{'nom':q[0],'devoirId':devoir})
            q_id = self.récupèreId("questions",{'nom':q[0]})
            for comp in q[1]:
                c_id = self.récupèreId("competence",{'nom':comp[0]})
                self.ajouteDansTable("questionsCompetences", \
                                     {"questionsId":q_id,"competenceId":c_id,"coefficient":comp[1]})

    def retraitQuestion(self, devoir:int, nomQuestion:str) -> None:
        """
        Cette fonction commence par vider toutes les lignes de questionsCompetences associées à la question.
        """
        c = self.conn.cursor()
        c.execute("select id from questions where nom like '{}';".format(nomQuestion))
        i = [ a for a in c.fetchall() ][0][0]
        self.retraitDeTable('questionsCompetences', {'questionsId':i})
        self.retraitDeTable('questions',{'devoirId':devoir,'nom':nomQuestion})

    def récupérerQuestions(self, devoir:int) -> list:
        """
        Prend en paramètre un id de devoir et renvoie la liste des questions, coefficients et compétences associées
        """
        c = self.conn.cursor()
        c.execute("select id,nom from questions where devoirId = {};".format(devoir))
        l = [ {'id':t[0],'nom':t[1],'competences':[]} for t in c.fetchall() ]
        for a in l:
            str_sql = "select competence.nom,questionsCompetences.coefficient from questionsCompetences " + \
                      "join competence on questionsCompetences.competenceId = competence.id " + \
                      "where questionsCompetences.questionsId = {};".format(a['id'])
            c.execute(str_sql)
            for t  in c.fetchall():
                a['competences'].append({'nom':t[0],'coefficient':t[1]})
        return(l)

    def ajoutTypeModificateur(self, nom:str) -> None:
        self.ajouteDansTable("typesModificateursÉvaluation", {"nom":nom})

    def retraitTypeModificateur(self, nom:str) -> None:
        self.retraitDeTable("typesModificateursÉvaluation",{"nom":nom})

    def récupèreTypesModificateur(self) -> list:
        return(self.récupèreChamps("typesModificateursÉvaluation",["nom"]))

    def ajoutModificateur(self, typ:str, devoir:int, nom:str, valeur:float) -> None:
        """ Le devoir est identifié par son id """
        vals = {"nom":nom, "typesModificateursÉvaluationId":("typesModificateursÉvaluation","nom",typ), \
                "devoirId":devoir, "valeur":valeur}
        self.ajouteDansTable("modificateursDevoir", vals)

    def retraitModificateur(self, nom:str, devoir:int) -> None:
        conds = {"nom":nom, "devoirId":devoir}
        self.retraitDeTable("modificateursDevoir", conds)

    def récupèreModificateurs(self, devoir:int) -> list:
        c = self.conn.cursor()
        str_sql = "select typesModificateursÉvaluation.nom, modificateursDevoir.nom, modificateursDevoir.valeur " + \
                  "from typesModificateursÉvaluation join modificateursDevoir " + \
                  "on typesModificateursÉvaluation.id = modificateursDevoir.typesModificateursÉvaluationId " + \
                  "where modificateursDevoir.devoirId = {};".format(devoir)
        c.execute(str_sql)
        liste = [ {'type':a[0], 'nom':a[1], 'valeur':a[2]} for a in c.fetchall() ]
        return(liste)


## Partie main pour tests

def afficherSéparateur() -> None:
    """ Fonction utilitaire pour l'affichage des tests """
    print("="*70)

def afficherSection(sec:str) -> None:
   """ Fonction utilitaire pour l'affichage des tests """
   afficherSéparateur()
   print("\t=== {} ===".format(sec))

def afficherAction(sec:str) -> None:
   """ Fonction utilitaire pour l'affichage des tests """
   print("## {}".format(sec))

def afficherRetour(sec:str) -> None:
   """ Fonction utilitaire pour l'affichage des tests """
   print(" * {}".format(sec))

def afficherLigne(sec:str) -> None:
   """ Fonction utilitaire pour l'affichage des tests """
   print("\t* {}".format(sec))

if __name__ == '__main__':
    # test d'ouverture et affichage du schema
    afficherSection("Nettoyage et initialisation de la base de tests")
    nom_db = 'competences_test.db'
    bdd = BaseDeDonnées(nom_db)
    c = bdd.conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for tab in ['competence','competenceType','competenceChapitre']:
        try:
            c.execute("DROP table {};".format(tab))
        except:
            pass
    bdd.créerSchéma()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    a = c.fetchall()  # forme non simplement utilisable des noms des tables
    a = [ t[0] for t in a[1:] ]  # on enlève la table sqlite_sequence et on extrait les noms

    afficherSection("Contenu de la DB")
    afficherRetour("Liste des tables dans la DB")
    afficherLigne(str(a))
    for tab in a:
        c.execute("pragma table_info({})".format(tab))
        cols = c.fetchall()
        afficherRetour("Détail des champs de la table {} :".format(tab))
        [afficherLigne("{}".format(col)) for col in cols]

    # Test de gestion de la table des types de compétences
    afficherSection("Test de l'interface avec la table compétenceType")
    tab = ['technique','analyse','connaissance']
    afficherAction("Récupération des types de compétence :")
    afficherRetour(bdd.récupèreCompétenceTypes())
    [ bdd.ajoutCompétenceType(compTp) for compTp in tab ]
    afficherAction("Peuplement... Récupération des types de compétence :")
    afficherRetour(bdd.récupèreCompétenceTypes())
    bdd.retraitCompétenceType('technique')
    afficherAction("Retrait de 'technique'... Récupération des types de compétence :")
    afficherRetour(bdd.récupèreCompétenceTypes())
    [ bdd.retraitCompétenceType(t['nom']) for t in bdd.récupèreCompétenceTypes() ]
    [ bdd.ajoutCompétenceType(compTp) for compTp in tab ]
    afficherAction("Repeuplement correct de la base")

    # Test de gestion de la table des chapitres de compétences
    afficherSection("Test de l'interface avec la table compétenceChapitre")
    tab = ['généralités','mécanique','transformations chimiques']
    afficherAction("Récupération des chapitres existants :")
    afficherRetour(bdd.récupèreCompétenceChapitres())
    [ bdd.ajoutCompétenceChapitre(compTp) for compTp in tab ]
    afficherAction("Peuplement... Récupération des chapitres existants :")
    afficherRetour(bdd.récupèreCompétenceChapitres())
    bdd.retraitCompétenceChapitre('mécanique')
    afficherAction("Retrait de 'mécanique'... Récupération des chapitres existants :")
    afficherRetour(bdd.récupèreCompétenceChapitres())
    [ bdd.retraitCompétenceChapitre(t['nom']) for t in bdd.récupèreCompétenceChapitres() ]
    [ bdd.ajoutCompétenceChapitre(compTp) for compTp in tab ]
    afficherAction("Repeuplement correct de la base")

    # Test des insertions avec liens entre tables
    afficherSection("Test de l'interface avec competences")
    bdd.ajoutCompétence("Vérifier l'homogénéité","généralités","technique")
    bdd.ajoutCompétence("Écrire la loi de Newton","mécanique","technique")
    bdd.ajoutCompétence("Interpréter une mouvement par principe d'inertie","mécanique","analyse")
    c.execute("select * from competence;")
    afficherAction("Peuplement... Contenu de la table competence après ajouts :")
    [ afficherLigne(tu) for tu in c.fetchall() ]
    bdd.retraitCompétence("Écrire la loi de Newton")
    c.execute("select * from competence;")
    afficherAction("Retrait de 'Écrire la loi de Newton'... Contenu de la table competence après retrait :")
    [ afficherLigne(tu) for tu in c.fetchall() ]
    bdd.ajoutCompétence("Écrire la loi de Newton","mécanique","technique")
    afficherAction("Test d'ajout avec une clé externe fantaisiste :")
    try:
        bdd.ajoutCompétence("Vérifier l'homogénéité","généralités","pouet")
    except Exception as ex:
        afficherRetour("Exception levée -> ok")
    afficherAction("Récupération des noms de compétences existantes :")
    [ afficherLigne(l) for l in bdd.récupèreCompétencesListe() ]
    afficherAction("Récupération complète des infos de compétences existantes :")
    [ afficherLigne(a) for a in bdd.récupèreCompétencesComplet() ]

    # Tables des classes et des élèves
    afficherSection("Test de l'interface avec les classes et les étudiants")
    bdd.ajoutClasse("MPSI")
    bdd.ajoutClasse("MP")
    bdd.ajoutClasse("PSI")
    afficherAction("Peuplement de la base... Récupération des classes :")
    afficherRetour(bdd.récupèreClasses())
    bdd.retraitClasse("PSI")
    afficherAction("Retrait de la classe 'PSI'... Récupération des classes :")
    afficherRetour(bdd.récupèreClasses())
    listeDépart = [('Alp','Selin'), ('Gourgues','Maxime'), ('Morceaux','Jérémy')]
    bdd.ajoutListeÉtudiants(listeDépart,'MPSI')
    afficherAction("Peuplement de la MPSI... Récupération des classes :")
    [ afficherLigne(l) for l in bdd.récupèreÉtudiants("MPSI") ]
    bdd.ajoutÉtudiant("Bazin","Jérémy","MPSI")
    bdd.retraitÉtudiant("Gourgues", "Maxime")
    afficherAction("Modification de la MPSI... Récupération des classes :")
    [ afficherLigne(l) for l in bdd.récupèreÉtudiants("MPSI") ]

    # Tables des devoirs
    afficherSection("Test de l'interface avec les devoirs")
    bdd.ajoutTypeDevoir('DS')
    bdd.ajoutTypeDevoir('Interro')
    bdd.ajoutTypeDevoir('DM')
    afficherAction("Peuplement des types de devoirs... Récupération des types :")
    afficherRetour(bdd.récupèreTypesDevoirs())
    bdd.retraitTypeDevoir('DM')
    afficherAction("Retrait du type de devoirs 'DM'... Récupération des types :")
    afficherRetour(bdd.récupèreTypesDevoirs())
    bdd.ajoutDevoir("DS",1,"20.09.2017","MPSI")
    bdd.ajoutDevoir("DS",2,"20.10.2017","MPSI",3)
    bdd.ajoutDevoir("Interro",1,"15.09.2017","MPSI")
    afficherAction("Peuplement des devoirs... Récupération des devoirs :")
    [ afficherLigne(l) for l in bdd.récupèreDevoirs() ]
    bdd.retraitDevoir(2)
    afficherAction("Retrait du devoirs n°2... Récupération des devoirs :")
    [ afficherLigne(l) for l in bdd.récupèreDevoirs() ]
    questions = [('1.a',[("Vérifier l'homogénéité",1),("Interpréter une mouvement par principe d'inertie",2)]), \
                 ('1.b',[("Vérifier l'homogénéité",1),('Écrire la loi de Newton',2)]), \
                 ('2',  [('Écrire la loi de Newton',3)])]
    bdd.créerQuestions(1,questions)
    afficherAction("Peuplement des questions du devoir 1... Récupération des questions :")
    [ afficherLigne(l) for l in bdd.récupérerQuestions(1) ]
    bdd.retraitQuestion(1,'1.b')
    afficherAction("Retrait de la question 1.b du devoir 1... Récupération des questions :")
    [ afficherLigne(l) for l in bdd.récupérerQuestions(1) ]
    bdd.ajoutTypeModificateur('pointsFixes')
    bdd.ajoutTypeModificateur('bonusMalus')
    afficherAction("Peuplement des types de modificateurs... Récupération des types :")
    afficherRetour(bdd.récupèreTypesModificateur())
    bdd.retraitTypeModificateur("bonusMalus")
    afficherAction("Retrait du type 'bonusMalus'... Récupération des types :")
    afficherRetour(bdd.récupèreTypesModificateur())
    bdd.ajoutModificateur('pointsFixes',1,'Présentation',2)
    bdd.ajoutModificateur('pointsFixes',1,'Homogénéité',3)
    afficherAction("Création d'un modificateur... Récupération des modificateurs du devoir 1 :")
    [ afficherLigne(a) for a in bdd.récupèreModificateurs(1) ]
    bdd.retraitModificateur('Présentation',1)
    afficherAction("Retrait du modificateur 'Présentation'... Récupération des modificateurs du devoir 1 :")
    [ afficherLigne(a) for a in bdd.récupèreModificateurs(1) ]

    afficherSéparateur()
    bdd.fermerDB()
