#!/usr/bin/python3

"""
Module gérant le stockage et le traitement des données.
"""

## imports
import numpy as np

## classe pour gérer les devoirs
class Devoir(object):
    """
    Classe représentant un devoir.

    Contient le type et numéro du devoir, la classe associée, la date, et la liste des
    questions, chacune associée à la liste des compétences testées, chaque compétence étant
    associée à un coefficient.
    """
    def __init__(self, classe:str, typ:str, num:int, date:str) -> 'Devoir':
        """
        Constructeur.

        Un devoir est construit avec ses données générales mais les questions sont
        ajoutées ensuite.
        La liste self.questions contient des paires ("nom_question",[("nom_compétence",coeff)])
        """
        self.classe = classe
        self.typ = typ
        self.num = num
        self.date = date
        self.questions = []

    def copie(self):
        """
        Constructeur de copie
        """
        dev_tmp = Devoir(self.classe, self.typ, self.num, self.date)
        for q in self.questions:
            dev_tmp.append((q[0],q[1][:]))
        return(dev_tmp)

    def correspondÀ(self, liste:list) -> bool:
        """
        Fonction pour tester qu'un devoir correspond à une liste [classe,type,num,date]
        """
        return(self.classe == liste[0] and self.typ == liste[1] \
               and self.num == liste[2] and self.date == liste[3])

    def ajouterQuestion(self, nom:str, compétences_coef:list) -> None:
        """
        Fonction utilisée pour ajouter des questions, associées à des compétences et des
        coefficients.

        La liste contient des paires ("nom_compétence",coeff)
        """
        self.questions.append((nom,compétences_coef))
        self.questions.sort(key=lambda x: x[0])

    def changerQuestion(self, num:int, nom:str, compétences_coef:list) -> None:
        """
        Fonction utilisée pour modifier la num-ième question, associée à des compétences et des
        coefficients.

        La liste contient des paires ("nom_compétence",coeff)
        """
        self.question[num] = (nom,compétences_coef)
        self.questions.sort(key=lambda x: x[0])

    def get_listeQuestionsModèle(self, nombreCompétencesMax:int) -> list:
        """
        Fonction renvoyant une liste de questions sous la forme adaptée à un Gtk.ListStore.

        Chaque élément de la liste est une liste contenant :
        - le nom de la question
        - le nom de la compétence, puis son coefficient, autant de fois que nécessaire
        - "", puis 0, suffisamment de fois pour atteindre nombreCompétencesMax paires str,int.
        """
        liste = []
        for q in self.questions:
            cp_coeff = [ q[0] ]
            for comp,coef in q[1]:
                cp_coeff += [ comp, coef ]
            cp_coeff += ["",0]*(nombreCompétencesMax-len(cp_coeff)//2)
            liste.append(cp_coeff)
        return(liste)

    def set_questionsDepuisModèle(self, modèle:list, compétences:list) -> None:
        """
        Fonction utilisée pour mettre à jour les questions depuis la forme adaptée à un Gtk.ListStore.
        Vérifie que les compétences proposées sont bien dans la liste compétences avant de valider.

        Chaque élément de la liste est une liste contenant :
        - le nom de la question
        - le nom de la compétence, puis son coefficient, autant de fois que nécessaire
        - "", puis 0, éventuellement répété un certain nombre de fois
        """
        self.questions.clear()
        for q in modèle:
            nombreCompétencesMax = (len(q)-1)//2
            nom = q[0]
            comps = [ (q[2*i+1],q[2*i+2]) for i in range(nombreCompétencesMax) if q[2*i+1] in compétences ]
            self.questions.append((nom,comps))

    def test_créerQuestionsDevoir(self):
        """
        Auto-génère une liste de questions pour les tests.
        Cette fonction n'est pas censée être utilisée hors des tests.
        """
        q1 = ("1.",[("Connaître les dimensions fondamentales",1),("Connaître les dimensions dérivées",1)])
        q2 = ("2.a.",[("Vérifier l'homogénéité",2)])
        q3 = ("2.b.",[("Prévoir un résultat par AD",3)])
        self.questions = [q1,q2,q3]
