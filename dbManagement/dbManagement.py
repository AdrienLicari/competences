#!/usr/bin/ipython3

"""
Module permettant de communiquer avec la base de données gérée en SQLite.
Les fonctions fournies par ce module sont adaptées aux besoins du code général.
"""

## imports
import sqlite3 as s
import time

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
        str_tablesimple = lambda nom: "create table IF NOT EXISTS {}".format(nom) + \
                          "(id integer primary key autoincrement, nom text);"
        str_tableCompetences = "CREATE TABLE IF NOT EXISTS competence" + \
                               "(id integer primary key autoincrement, nom text, " + \
                               "competenceTypeId int, competenceChapitreId int," + \
                               "foreign key(competenceTypeId) references competenceType(id), " + \
                               "foreign key(competenceChapitreId) references competenceChapitre(id));"
        str_tableÉtudiants = "CREATE TABLE IF NOT EXISTS etudiants" + \
                             "(id integer primary key autoincrement, classeId int, nom text, prenom text, " + \
                             "foreign key(classeId) references classes(id));"
        str_tableDevoirs = "CREATE TABLE IF NOT EXISTS devoir " + \
                           "(id integer primary key autoincrement, classeId int, " + \
                           "typeId int, numero int, date text, noteMax int default 20, nvxAcq int default 2," + \
                           "foreign key(typeId) references devoirType(id), " + \
                           "foreign key(classeId) references classes(id));"
        str_tableQuestions = "CREATE TABLE IF NOT EXISTS questions " + \
                             "(id integer primary key autoincrement, devoirId int, nom text, " + \
                             "foreign key(devoirId) references devoir(id));"
        str_tableQuestionsCompétences = "CREATE TABLE IF NOT EXISTS questionsCompetences " + \
                                        "(id integer primary key autoincrement, questionsId int, " + \
                                        "competenceId int, coefficient int," + \
                                        "foreign key(questionsId) references questions(id), " + \
                                        "foreign key(competenceId) references competence(id));"
        str_tableModificateursDevoir = "CREATE TABLE IF NOT EXISTS modificateursDevoir " + \
                                       "(id integer primary key autoincrement, devoirId int, " + \
                                       "typesModificateursÉvaluationId int, valeur float, nom text," + \
                                       "foreign key(devoirId) references devoir(id), " + \
                                       "foreign key(typesModificateursÉvaluationId) references " + \
                                       "typesModificateursÉvaluation(id));"
        str_tableEtudiantsEvaluationCompetences = "CREATE TABLE IF NOT EXISTS etudiantsEvaluationCompetence " + \
                                       "(id integer primary key autoincrement, etudiantsId int, " + \
                                       "questionsCompetencesId int, evaluation int, " + \
                                       "foreign key(etudiantsId) references etudiants(id), " + \
                                       "foreign key(questionsCompetencesId) references questionsCompetences(id));"
        str_tableEtudiantsEvaluationModificateurs = "CREATE TABLE IF NOT EXISTS etudiantsEvaluationModificateurs " + \
                                       "(id integer primary key autoincrement, etudiantsId int, " + \
                                       "modificateursDevoirId int, evaluation float," + \
                                       "foreign key(etudiantsId) references etudiants(id), " + \
                                       "foreign key(modificateursDevoirId) references modificateursDevoir(id));"
        str_tableEtudiantsPresenceDevoir = "CREATE TABLE IF NOT EXISTS etudiantsPresenceDevoir " + \
                                           "(id integer primary key autoincrement, devoirId int, " + \
                                           "etudiantsId int, presence boolean, " + \
                                           "foreign key(devoirId) references devoir(id), " + \
                                           "foreign key(etudiantsId) references etudiants(id));"
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
        c.execute(str_tableEtudiantsEvaluationCompetences)
        c.execute(str_tableEtudiantsEvaluationModificateurs)
        c.execute(str_tableEtudiantsPresenceDevoir)
        self.conn.commit()

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
                elif isinstance(valeur,bool):
                    str_valeurs += """{},""".format(int(valeur))
                else:
                    str_valeurs += """{},""".format(valeur)
        str_requete = """replace into {} """.format(table) + str_champs[:-1] + \
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
                str_retrait += """{} like "{}" and """.format(key,val)
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

    def récupèreIds(self, table:str, conditions:dict) -> list:
        """
        Renvoie les id des entrées identifiées par un ensemble de conditions.
        """
        c = self.conn.cursor()
        str_récup = """select id from {} where """.format(table)
        for key,val in conditions.items():
            if type(val) == str and "(select " not in val:
                str_récup += """{} like "{}" and """.format(key,val)
            else:
                str_récup += "{} = {} and ".format(key,val)
        str_récup = str_récup[:-4] + ";"
        c.execute(str_récup)
        a = [ b[0] for b in c.fetchall() ]
        return(a)

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
        sql_str = "select etudiants.nom,etudiants.prenom,etudiants.id from etudiants " + \
                  "join classes on classeId = classes.id " + \
                  "where classes.nom like '{}' order by etudiants.nom;".format(classe)
        c.execute(sql_str)
        a = [ {'id':t[2], 'nom':t[0], 'prenom':t[1]} for t in c.fetchall() ]
        return(a)

    def ajoutTypeDevoir(self, nom:str) -> None:
        self.ajouteDansTable('devoirType',{'nom':nom})

    def retraitTypeDevoir(self, nom:str) -> None:
        self.retraitDeTable('devoirType',{'nom':nom})

    def récupèreTypesDevoirs(self) -> list:
        return(self.récupèreChamps('devoirType',['nom']))

    def ajoutDevoir(self, classe:str, typ:str, numero:int, date:str, \
                    noteMax:int=20, niveauxAcquisition:int=2) -> None:
        """
        Noter que la valeur par défaut des niveaux d'acquisition testés est 2 (acquis / non acquis)
        """
        clId = self.récupèreIds("classes",{'nom':classe})[0]
        tyId = self.récupèreIds("devoirType",{'nom':typ})[0]
        self.ajouteDansTable('devoir',{'numero':numero, 'date':date, 'nvxAcq':niveauxAcquisition, \
                                       'noteMax':noteMax, 'typeId':tyId, 'classeId':clId})
        dvId = self.récupèreIds("devoir",{'numero':numero,'typeId':tyId, 'classeId':clId})[0]
        étsId = self.récupèreIds("etudiants",{"classeId":clId})
        for i in étsId:
            self.ajouteDansTable("etudiantsPresenceDevoirs",{"etudiantsId":i,"devoirId":dvId,"presence":True})

    def retraitDevoir(self, dvId:int) -> None:
        list_str = lambda l: "{}".format(l)[1:-1]
        c = self.conn.cursor()
        quId = self.récupèreIds("questions",{"devoirId":dvId})
        cpId = []
        for i in quId :
            cpId += self.récupèreIds("questionsCompetences",{"questionsId":i})
        mdId = self.récupèreIds("modificateursDevoir",{"devoirId":dvId})
        str_sql = ["delete from etudiantsPresenceDevoirs where devoirId = {};".format(dvId)]
        str_sql += ["delete from etudiantsEvaluationCompetence " + \
                   "where questionsCompetencesId in ({});".format(list_str(cpId))]
        str_sql += ["delete from questionsCompetences where questionsId in ({});".format(list_str(quId))]
        str_sql += ["delete from questions where devoirId = {};".format(dvId)]
        str_sql += ["delete from etudiantsEvaluationModificateurs " + \
                   "where modificateursDevoirId in ({});".format(list_str(mdId))]
        str_sql += ["delete from modificateursDevoir where devoirId = {};".format(dvId)]
        str_sql += ["delete from devoir where id = {};".format(dvId)]
        [ c.execute(s) for s in str_sql ]
        self.conn.commit()

    def récupèreDevoirs(self) -> list:
        """ Fonction qui récupère l'ensemble des devoirs """
        c = self.conn.cursor()
        sql_str = "select devoir.id,classes.nom,devoirType.nom,devoir.numero,devoir.date,devoir.nvxAcq," + \
                  "devoir.noteMax from devoir join classes on classeId = classes.id " + \
                  "join devoirType on typeId = devoirType.id " + \
                  "order by devoir.date;"
        c.execute(sql_str)
        a = [ {'id':t[0],'classe':t[1],'type':t[2],'numéro':t[3],'date':t[4],'nvxAcq':t[5],'noteMax':t[6]} \
              for t in c.fetchall() ]
        return(a)

    def modifieNoteEtNiveauxDevoir(self, idDevoir:int, noteMax:int, nvxAcq:int) -> None:
        c = self.conn.cursor()
        c.execute("update devoir set noteMax = {}, nvxAcq = {} where id = {};".format(noteMax,nvxAcq,idDevoir))
        self.conn.commit()

    def créerQuestions(self, devoir:int, liste:list) -> None:
        """
        Prend en paramètre une liste de tuples (nomDeQuestion,[(compétence,coeff)]).
        Le devoir est identifié par son numéro id.
        """
        c = self.conn.cursor()
        for q in liste:
            self.ajouteDansTable("questions",{'nom':q[0],'devoirId':devoir})
            q_id = self.récupèreIds("questions",{'nom':q[0], 'devoirId':devoir})[0]
            vals = [ """({},(select id from competence where nom like "{}"),{});""".format(q_id,comp[0],comp[1]) \
                     for comp in q[1] ]
            sql_str = "insert into questionsCompetences(questionsId,competenceId,coefficient) values "
            for a in vals:
                c.execute(sql_str + a)

    def retraitQuestion(self, devoir:int, nomQuestion:str) -> None:
        """
        Cette fonction commence par vider toutes les lignes de questionsCompetences associées à la question.
        """
        c = self.conn.cursor()
        c.execute("select id from questions where nom like '{}' and devoirId = {};".format(nomQuestion,devoir))
        i = [ a for a in c.fetchall() ][0][0]
        c.execute("delete from etudiantsEvaluationCompetence where " + \
                  "questionsCompetencesId = (select id from questionsCompetences where questionsId = {});".format(i))
        self.retraitDeTable('questionsCompetences', {'questionsId':i})
        self.retraitDeTable('questions',{'devoirId':devoir,'nom':nomQuestion})

    def récupérerQuestions(self, devoir:int) -> list:
        """
        Prend en paramètre un id de devoir et renvoie la liste des questions, coefficients et compétences associées
        """
        c = self.conn.cursor()
        c.execute("select id,nom from questions where devoirId = {};".format(devoir))
        l = [ [t[0],t[1]] for t in c.fetchall() ]
        for a in l:
            str_sql = "select competence.nom,questionsCompetences.coefficient from questionsCompetences " + \
                      "join competence on questionsCompetences.competenceId = competence.id " + \
                      "where questionsCompetences.questionsId = {};".format(a[0])
            c.execute(str_sql)
            for t in c.fetchall():
                a += [t[0],t[1]]
            a.pop(0)
        return(l)

    def ajoutTypeModificateur(self, nom:str) -> None:
        self.ajouteDansTable("typesModificateursÉvaluation", {"nom":nom})

    def retraitTypeModificateur(self, nom:str) -> None:
        self.retraitDeTable("typesModificateursÉvaluation",{"nom":nom})

    def récupèreTypesModificateur(self) -> list:
        return(self.récupèreChamps("typesModificateursÉvaluation",["nom"]))

    def ajoutModificateur(self, devoir:int, typ:str, nom:str, valeur:float) -> None:
        """ Le devoir est identifié par son id """
        vals = {"nom":nom, "typesModificateursÉvaluationId":("typesModificateursÉvaluation","nom",typ), \
                "devoirId":devoir, "valeur":valeur}
        self.ajouteDansTable("modificateursDevoir", vals)

    def retraitModificateur(self, devoir:int, nom:str) -> None:
        conds = {"nom":nom, "devoirId":devoir}
        self.retraitDeTable("modificateursDevoir", conds)

    def récupèreModificateurs(self, devoir:int) -> list:
        c = self.conn.cursor()
        str_sql = "select typesModificateursÉvaluation.nom, modificateursDevoir.nom, modificateursDevoir.valeur " + \
                  "from typesModificateursÉvaluation join modificateursDevoir " + \
                  "on typesModificateursÉvaluation.id = modificateursDevoir.typesModificateursÉvaluationId " + \
                  "where modificateursDevoir.devoirId = {};".format(devoir)
        c.execute(str_sql)
        liste = [ (a[0],a[1],a[2]) for a in c.fetchall() ]
        return(liste)

    def sauverDevoir(self, infos:dict) -> None:
        """
        Met à jour la BDD avec les évaluations. Le dictionnaire doit avoir les entrées suivantes :
        - classe, types, num, date
        - étudiants : liste (nom,prénom,présent)
        - éval : une liste de tuples (nomQuestion, nomCompétence, évaluation)
        - modificateurs : une liste de tuples (typeModif, nomModif, évaluation)
        """
        # Vidage
        c = self.conn.cursor()
        clId = self.récupèreIds("classes",{"nom":infos['classe']})[0]
        dvId = self.récupèreIds("devoir",{"classeId":clId, "numero":infos['devoirNum'], \
                                         "typeId":"""(select id from devoirType where nom like "{}")""".\
                                          format(infos['devoirType'])})[0]
        self.retraitDevoir(dvId)
        # Recréation
        self.ajoutDevoir(infos['classe'],infos['devoirType'],infos['devoirNum'],infos['date'],\
                         infos['noteMax'],infos['nvxAcq'])
        dvId = self.récupèreIds("devoir",{"classeId":clId, "numero":infos['devoirNum'], \
                                         "typeId":"""(select id from devoirType where nom like "{}")""".\
                                          format(infos['devoirType'])})[0]
        self.créerQuestions(dvId, infos['questions'])
        [ self.ajoutModificateur(dvId, a[0], a[1], a[2]) for a in infos['modificateurs'] ]
        kÉts = range(len(infos['étudiants']))
        étudiantsBDD = self.récupèreÉtudiants(infos['classe'])
        idÉts = [ étudiantsBDD[k]['id'] for k in kÉts ]
        # Présence
        sql_str = "replace into etudiantsPresenceDevoirs (id,devoirId,etudiantsId,presence) values "
        for k in kÉts:
            p_id = self.récupèreIds("etudiantsPresenceDevoirs",{"devoirId":dvId,"etudiantsId":idÉts[k]})[0]
            sql_str += "({},{},{},{}), ".format(p_id,dvId,idÉts[k],int(infos['étudiants'][k][2]))
        sql_str = sql_str[:-2] + ";"
        c.execute(sql_str)
        # Évaluation
        sql_str = "replace into etudiantsEvaluationCompetence "
        sql_str += "(etudiantsId,questionsCompetencesId,evaluation) values "
        if len(infos['éval']) != 0:
            for quest,comp,éval in infos['éval']:
                sql_interm = "select qc.id from questionsCompetences as qc " + \
                             "join competence as c on c.id = qc.competenceId " + \
                             "join questions as q on q.id = qc.questionsId " + \
                             """where q.nom like "{}" and c.nom like "{}";""".format(quest,comp)
                qc_id = [ a[0] for a in c.execute(sql_interm) ][0]
                for k in kÉts:
                    sql_str += "({},{},{}), ".format(idÉts[k],qc_id,éval[k])
            sql_str = sql_str[:-2] + ";"
            c.execute(sql_str)
        # Modificateurs
        sql_str= "replace into etudiantsEvaluationModificateurs "
        sql_str += "(etudiantsId,modificateursDevoirId,evaluation) values "
        if len(infos['modificateurs']) != 0:
            for typ,nom,maxi,éval in infos['modificateurs']:
                sql_interm = "select modificateursDevoir.id from modificateursDevoir " + \
                             "join typesModificateursÉvaluation " + \
                             "on typesModificateursÉvaluation.id = typesModificateursÉvaluationId " + \
                             """where typesModificateursÉvaluation.nom like "{}" """.format(typ) + \
                             """ and modificateursDevoir.nom like "{}" """.format(nom) + \
                             "and modificateursDevoir.devoirId = {};".format(dvId)
                mod_id = [ a[0] for a in c.execute(sql_interm) ][0]
                for k in kÉts:
                    sql_str += "({},{},{}), ".format(idÉts[k],mod_id,éval[k])
            sql_str = sql_str[:-2] + ";"
            c.execute(sql_str)
        self.conn.commit()

    def récupérerÉvaluation(self, idDev:int) -> dict:
        """
        Renvoie un dictionnaire contenant :
        - présence : une liste de tuples (nomÉtudiant,prénomÉtudiant,présence)
        - éval : une liste de tuples (nomQuestion,nomCompétence,nomÉtudiant,prénomÉtudiant,note)
        - pointsFixes : une liste de tuples (nomItem,nomÉtudiant,prénomÉtudiant,note)
        - modifs : une liste de tuples (nomItem,nomÉtudiant,prénomÉtudiant,note) pour les pourcentages
        """
        ret = {}
        c = self.conn.cursor()
        str_sql = "select etudiants.nom, etudiants.prenom, etudiantsPresenceDevoirs.presence "+ \
                  "from etudiants join etudiantsPresenceDevoirs " + \
                  "on etudiants.id = etudiantsPresenceDevoirs.etudiantsId " + \
                  "where etudiantsPresenceDevoirs.devoirId = {};".format(idDev)
        ret['présence'] = [ (a[0],a[1],a[2] == 1) for a in c.execute(str_sql) ]
        str_sql = "select Q.nom, C.nom, E.nom, E.prenom, EEC.evaluation " + \
                  "from etudiants as E join etudiantsEvaluationCompetence as EEC on E.id = EEC.etudiantsId " + \
                  "join questionsCompetences as QC on EEC.questionsCompetencesId = QC.id " + \
                  "join competence as C on QC.competenceId = C.id " + \
                  "join questions as Q on QC.questionsId = Q.id " + \
                  "where Q.devoirId = {};".format(idDev)
        ret['éval'] = [ a for a in c.execute(str_sql) ]
        str_sql = "select M.nom, E.nom, E.prenom, EEM.evaluation from etudiants as E " + \
                  "join etudiantsEvaluationModificateurs as EEM on E.id = EEM.etudiantsId " + \
                  "join modificateursDevoir as M on EEM.modificateursDevoirId = M.id " + \
                  "join typesModificateursÉvaluation as T " + \
                  "on M.typesModificateursÉvaluationId = T.id " + \
                  "where M.devoirId = {} and T.nom like 'points fixes';".format(idDev)
        ret['pointsFixes'] = [ a for a in c.execute(str_sql) ]
        str_sql = "select M.nom, E.nom, E.prenom, EEM.evaluation from etudiants as E " + \
                  "join etudiantsEvaluationModificateurs as EEM on E.id = EEM.etudiantsId " + \
                  "join modificateursDevoir as M on EEM.modificateursDevoirId = M.id " + \
                  "join typesModificateursÉvaluation as T " + \
                  "on M.typesModificateursÉvaluationId = T.id " + \
                  "where M.devoirId = {} and T.nom like 'pourcentage';".format(idDev)
        ret['modifs'] = [ a for a in c.execute(str_sql) ]
        return(ret)

    def sauverÉvaluationUnÉtudiant(self, infos:dict) -> None:
        """
        Met à jour la BDD avec les évaluations. Le dictionnaire doit avoir les entrées suivantes :
        - classe, types, num, date
        - étudiants : (nom,prénom,présent)
        - éval : une liste de tuples (nomQuestion, nomCompétence, évaluation)
        - modificateurs : une liste de tuples (typeModif, nomModif, évaluation)
        """
        c = self.conn.cursor()
        clId = self.récupèreIds("classes",{"nom":infos['classe']})[0]
        dvId = self.récupèreIds("devoir",{"classeId":clId, "numero":infos['devoirNum'], \
                                         "typeId":"""(select id from devoirType where nom like "{}")""".\
                                          format(infos['devoirType'])})[0]
        idÉt = self.récupèreIds("etudiants",{"nom":infos['étudiant'][0],"prenom":infos['étudiant'][1]})[0]
        # Présence
        sql_str = "replace into etudiantsPresenceDevoirs (id,devoirId,etudiantsId,presence) values "
        sql_str += "((select id from etudiantsPresenceDevoirs where devoirId={} and etudiantsId={}),{},{},{});".\
                        format(dvId,idÉt,dvId,idÉt,int(infos['étudiant'][2]))
        c.execute(sql_str)
        # Évaluation
        sql_str = "replace into etudiantsEvaluationCompetence "
        sql_str += "(id,etudiantsId,questionsCompetencesId,evaluation) values "
        if len(infos['éval']) != 0:
            for quest,comp,éval in infos['éval']:
                sql_interm = "select qc.id from questionsCompetences as qc " + \
                             "join competence as c on c.id = qc.competenceId " + \
                             "join questions as q on q.id = qc.questionsId " + \
                             """where q.nom like "{}" and c.nom like "{}";""".format(quest,comp)
                qc_id = [ a[0] for a in c.execute(sql_interm) ][0]
                eval_id = self.récupèreIds("etudiantsEvaluationCompetence", \
                                           {"questionsCompetencesId":qc_id,"etudiantsId":idÉt})[0]
                sql_str += "({},{},{},{}), ".format(eval_id,idÉt,qc_id,éval)
            sql_str = sql_str[:-2] + ";"
            c.execute(sql_str)
        # Modificateurs
        sql_str= "replace into etudiantsEvaluationModificateurs "
        sql_str += "(id,etudiantsId,modificateursDevoirId,evaluation) values "
        if len(infos['modificateurs']) != 0:
            for typ,nom,maxi,éval in infos['modificateurs']:
                sql_interm = "select modificateursDevoir.id from modificateursDevoir " + \
                             "join typesModificateursÉvaluation " + \
                             "on typesModificateursÉvaluation.id = typesModificateursÉvaluationId " + \
                             """where typesModificateursÉvaluation.nom like "{}" """.format(typ) + \
                             """ and modificateursDevoir.nom like "{}" """.format(nom) + \
                             "and modificateursDevoir.devoirId = {};".format(dvId)
                mod_id = [ a[0] for a in c.execute(sql_interm) ][0]
                eval_id = self.récupèreIds("etudiantsEvaluationModificateurs",\
                                           {"modificateursDevoirId":mod_id, "etudiantsId":idÉt})[0]
                sql_str += "({},{},{},{}), ".format(eval_id,idÉt,mod_id,éval)
            sql_str = sql_str[:-2] + ";"
            c.execute(sql_str)
        self.conn.commit()


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

def effectuerTests() -> None:
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
    afficherAction("Peuplement... Récupération des types de compétence :")
    [ bdd.ajoutCompétenceType(compTp) for compTp in tab ]
    afficherRetour(bdd.récupèreCompétenceTypes())
    afficherAction("Retrait de 'technique'... Récupération des types de compétence :")
    bdd.retraitCompétenceType('technique')
    afficherRetour(bdd.récupèreCompétenceTypes())
    afficherAction("Repeuplement correct de la base")
    [ bdd.retraitCompétenceType(t['nom']) for t in bdd.récupèreCompétenceTypes() ]
    [ bdd.ajoutCompétenceType(compTp) for compTp in tab ]

    # Test de gestion de la table des chapitres de compétences
    afficherSection("Test de l'interface avec la table compétenceChapitre")
    tab = ['généralités','mécanique','transformations chimiques']
    afficherAction("Récupération des chapitres existants :")
    afficherRetour(bdd.récupèreCompétenceChapitres())
    afficherAction("Peuplement... Récupération des chapitres existants :")
    [ bdd.ajoutCompétenceChapitre(compTp) for compTp in tab ]
    afficherRetour(bdd.récupèreCompétenceChapitres())
    afficherAction("Retrait de 'mécanique'... Récupération des chapitres existants :")
    bdd.retraitCompétenceChapitre('mécanique')
    afficherRetour(bdd.récupèreCompétenceChapitres())
    afficherAction("Repeuplement correct de la base")
    [ bdd.retraitCompétenceChapitre(t['nom']) for t in bdd.récupèreCompétenceChapitres() ]
    [ bdd.ajoutCompétenceChapitre(compTp) for compTp in tab ]

    # Test des insertions avec liens entre tables
    afficherSection("Test de l'interface avec competences")
    afficherAction("Peuplement... Contenu de la table competence après ajouts :")
    bdd.ajoutCompétence("Vérifier l'homogénéité","généralités","technique")
    bdd.ajoutCompétence("Écrire la loi de Newton","mécanique","technique")
    bdd.ajoutCompétence("Interpréter une mouvement par principe d'inertie","mécanique","analyse")
    c.execute("select * from competence;")
    [ afficherLigne(tu) for tu in c.fetchall() ]
    afficherAction("Retrait de 'Écrire la loi de Newton'... Contenu de la table competence après retrait :")
    bdd.retraitCompétence("Écrire la loi de Newton")
    c.execute("select * from competence;")
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
    afficherAction("Peuplement de la base... Récupération des classes :")
    bdd.ajoutClasse("MPSI")
    bdd.ajoutClasse("MP")
    bdd.ajoutClasse("PSI")
    afficherRetour(bdd.récupèreClasses())
    afficherAction("Retrait de la classe 'PSI'... Récupération des classes :")
    bdd.retraitClasse("PSI")
    afficherRetour(bdd.récupèreClasses())
    listeDépart = [('Alp','Selin'), ('Gourgues','Maxime'), ('Morceaux','Jérémy')]
    afficherAction("Peuplement de la MPSI... Récupération des classes :")
    bdd.ajoutListeÉtudiants(listeDépart,'MPSI')
    [ afficherLigne(l) for l in bdd.récupèreÉtudiants("MPSI") ]
    afficherAction("Modification de la MPSI... Récupération des classes :")
    bdd.ajoutÉtudiant("Bazin","Jérémy","MPSI")
    bdd.retraitÉtudiant("Gourgues", "Maxime")
    [ afficherLigne(l) for l in bdd.récupèreÉtudiants("MPSI") ]

    # Tables des devoirs
    afficherSection("Test de l'interface avec les devoirs")
    afficherAction("Peuplement des types de devoirs... Récupération des types :")
    bdd.ajoutTypeDevoir('DS')
    bdd.ajoutTypeDevoir('Interro')
    bdd.ajoutTypeDevoir('DM')
    afficherRetour(bdd.récupèreTypesDevoirs())
    afficherAction("Retrait du type de devoirs 'DM'... Récupération des types :")
    bdd.retraitTypeDevoir('DM')
    afficherRetour(bdd.récupèreTypesDevoirs())
    afficherAction("Peuplement des devoirs... Récupération des devoirs :")
    bdd.ajoutDevoir("MPSI","DS",1,"20.09.2017")
    bdd.ajoutDevoir("MPSI","DS",2,"20.10.2017",3)
    bdd.ajoutDevoir("MPSI","Interro",1,"15.09.2017")
    [ afficherLigne(l) for l in bdd.récupèreDevoirs() ]
    afficherAction("Retrait du devoirs n°2... Récupération des devoirs :")
    bdd.retraitDevoir(2)
    [ afficherLigne(l) for l in bdd.récupèreDevoirs() ]
    questions = [('1.a',[("Vérifier l'homogénéité",1),("Interpréter une mouvement par principe d'inertie",2)]), \
                 ('1.b',[("Vérifier l'homogénéité",1),('Écrire la loi de Newton',2)]), \
                 ('2',  [('Écrire la loi de Newton',3)])]
    afficherAction("Peuplement des questions du devoir 1... Récupération des questions :")
    bdd.créerQuestions(1,questions)
    [ afficherLigne(l) for l in bdd.récupérerQuestions(1) ]
    afficherAction("Retrait de la question 1.b du devoir 1... Récupération des questions :")
    bdd.retraitQuestion(1,'1.b')
    [ afficherLigne(l) for l in bdd.récupérerQuestions(1) ]
    afficherAction("Peuplement des types de modificateurs... Récupération des types :")
    bdd.ajoutTypeModificateur('pointsFixes')
    bdd.ajoutTypeModificateur('bonusMalus')
    afficherRetour(bdd.récupèreTypesModificateur())
    afficherAction("Retrait du type 'bonusMalus'... Récupération des types :")
    bdd.retraitTypeModificateur("bonusMalus")
    afficherRetour(bdd.récupèreTypesModificateur())
    afficherAction("Création d'un modificateur... Récupération des modificateurs du devoir 1 :")
    bdd.ajoutModificateur(1,'pointsFixes','Présentation',2)
    bdd.ajoutModificateur(1,'pointsFixes','Homogénéité',3)
    [ afficherLigne(a) for a in bdd.récupèreModificateurs(1) ]
    afficherAction("Retrait du modificateur 'Présentation'... Récupération des modificateurs du devoir 1 :")
    bdd.retraitModificateur(1,'Présentation')
    [ afficherLigne(a) for a in bdd.récupèreModificateurs(1) ]

    afficherSéparateur()
    bdd.fermerDB()


if __name__ == '__main__':
    effectuerTests()
    # bdd = BaseDeDonnées("competences.db")
    # bdd.créerSchéma()
    pass
