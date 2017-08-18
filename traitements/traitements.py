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
