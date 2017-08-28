#!/usr/bin/python3

"""
Module gérant le stockage et le traitement des données.
"""

## imports
from itertools import product
import numpy as np

## classe pour gérer les devoirs
class Devoir(object):
    """
    Classe représentant un devoir.

    Contient le type et numéro du devoir, la classe associée, la date, et la liste des
    questions, chacune associée à la liste des compétences testées, chaque compétence étant
    associée à un coefficient.

    Représentation interne des données :
    - self.classe est une str contenant le nom de la classe
    - self.typ est une str contenant la catégorie du devoir
    - self.num est un int contenant le numéro du devoir
    - self.date est une str contenant la date du devoir
    - self.étudiants est un np.ndarray(list) contenant les listes [nom,prénom,présent] des étudiants
        de la classe ; présent contient False si l'étudiant était absent.
    - self.noteMax est la note maximale au devoir (usuellement 10 ou 20)
    - self.questions est une np.ndarray(str) contenant les noms des questions
    - self.compétences est une np.ndarray(str) contenant les noms des compétences évaluées
    - self.coeff est un np.ndarray(int) de dimension 2 dont la ième ligne, jième colonne contient
        le coefficient de la compétence n°j dans la question n°i ; elle est limitée en
        nombre de questions et en nombre de compétences.
    - self.nvxAcq est un int contenant le nombre de niveaux pour l'évaluation (par exemple 2 pour acqui/non acquis
        ou 3 pour acquis/en cours/non acquis)
    - self.pointsFixes est une liste contenant des champs pour des points attribués en-dehors du barême
        Par exemple, [("Présentation",2)] indique qu'on réserve 2 points du total à la présentation
    - self.modificateurs est une liste permettant des bonus / malus en pourcentage de la note totale
        Par exemple, [("Homogénéité",-0.15)] indique qu'une erreur d'homogénéité sera sanctionnée de 15% de la note.
    - self.éval est un np.ndarray(int) de dimension 3 dont la ième ligne, jième colonne, kième cote contient
        l'évaluation de la compétence n°j dans la question n°i par l'étudiant n°k ; elle est limitée
        en nombre de questions et en nombre de compétences. Elle ne doit pas contenir de case > nvxAcq.
        Une valeur négative signifie que la compétence n'a pas été abordée.
    - self.évalPointsFixes est un np.ndarray(float) de dimension 2 dont la ième ligne, jième colonne contient
        l'évaluation de ces points fixes n°i par l'étudiant n°j
    - self.évalModificateurs est un np.ndarray(float) de dimension 2 dont la ième ligne, jième colonne contient
        l'évaluation de ces modificateurs n°i par l'étudiant n°j
    """
    maxQuestions = 100
    maxCompétences = 100
    maxModifs = 10
    # Fonctions d'intéraction avec l'interface
    def __init__(self, classe:str, typ:str, num:int, date:str, noteMax:int, nvxAcq:int, étudiants:list, \
                 pointsFixes:list=[], modificateurs:list=[]) -> 'Devoir':
        """
        Constructeur.

        Un devoir est construit avec ses données générales mais les questions sont
        ajoutées ensuite.

        étudiants est une liste de paires (nom,prénom)
        """
        self.classe = classe
        self.typ = typ
        self.num = num
        self.date = date
        self.noteMax = noteMax
        self.pointsFixes = pointsFixes
        self.modificateurs = modificateurs
        self.étudiants = [ [a[0],a[1],True] for a in étudiants ]
        self.étudiants.sort(key=lambda a: a[0])
        self.questions = np.array([""]*Devoir.maxQuestions,dtype=object)
        self.compétences = np.array([""]*Devoir.maxCompétences,dtype=object)
        self.coeff = np.zeros(shape=(Devoir.maxQuestions,Devoir.maxCompétences),dtype=int)
        self.nvxAcq = nvxAcq
        self.éval = -np.ones(shape=(Devoir.maxQuestions,Devoir.maxCompétences,len(self.étudiants)),dtype=int)
        self.évalPointsFixes = np.zeros(shape=(Devoir.maxModifs,len(self.étudiants)),dtype=float)
        for i,pf in enumerate(self.pointsFixes):
            self.évalPointsFixes[i,:] = pf[1]
        self.évalModificateurs = np.zeros(shape=(Devoir.maxModifs,len(self.étudiants)),dtype=int)

    def copie(self):
        """
        Constructeur de copie
        """
        dev_tmp = Devoir(self.classe, self.typ, self.num, self.date, self.étudiants)
        dev_tmp.questions = self.questions.copy()
        dev_tmp.compétences = self.compétences.copy()
        dev_tmp.coeff = self.coeff.copy()
        return(dev_tmp)

    def correspondÀ(self, liste:list) -> bool:
        """
        Fonction pour tester qu'un devoir correspond à une liste [classe,type,num]
        """
        return(self.classe == liste[0] and self.typ == liste[1] and self.num == liste[2])

    def actuelNombreQuestions(self) -> int:
        """
        Fonction interne utilitaire
        """
        return(len([ a for a in self.questions if a != '' ]))

    def actuelNombreCompétences(self) -> int:
        """
        Fonction interne utilitaire
        """
        return(len([ a for a in self.compétences if a != '' ]))

    def get_enTêteDevoir(self) -> str:
        """
        Fonction renvoyant la str "devoir {type} {num} de la classe {classe} - {date}
        """
        return("devoir {} {} de la classe {} - {}".format(self.typ,self.num,self.classe,self.date))

    def get_noteMax(self) -> int:
        """
        Getter simple pour la note maximale au devoir (typiquement 20)
        """
        return(self.noteMax)

    def set_noteMax(self, note:int) -> None:
        """
        Setter simple pour la note maximale au devoir (typiquement 20).
        """
        self.noteMax = int(note)

    def get_niveauxAcquisition(self) -> int:
        """
        Getter simple pour les niveaux d'acquisition.
        """
        return(self.nvxAcq)

    def set_niveauxAcquisition(self, nombre:int) -> None:
        """
        Setter simple pour le nombre de niveaux d'acquisition des compétences.
        """
        self.nvxAcq = int(nombre)

    def get_listeÉtudiantsModèle(self) -> list:
        """
        Propose la liste des étudiants pour sélection, sous la forme [[id,nomPrénom,présent,évalué],...]
        """
        liste = [0]*len(self.étudiants)
        for k,ét in enumerate(self.étudiants):
            évalué = (self.éval[:,:,k] > -1).any() or not ét[2]
            liste[k] = [k, ét[1]+" "+ét[0], ét[2], évalué]
        return(liste)

    def get_listeQuestionsModèle(self, nombreCompétencesMax:int) -> list:
        """
        Fonction renvoyant une liste de questions sous la forme adaptée à un Gtk.ListStore.

        Chaque élément de la liste est une liste contenant :
        - le nom de la question
        - le nom de la compétence, puis son coefficient, autant de fois que nécessaire
        - "", puis 0, suffisamment de fois pour atteindre nombreCompétencesMax paires str,int.
        """
        liste = []
        for i,q in enumerate(self.questions[self.questions != ""]):
            cp_coeff = [ q ]
            comps = [(j,a) for (j,a) in enumerate(self.compétences) if self.coeff[i,j] != 0]
            for j,nom in comps:
                cp_coeff += [ nom, self.coeff[i,j] ]
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
        for q in modèle:
            nombreCompétencesMax = (len(q)-1)//2
            nom = q[0]
            comps = [ q[2*i+1] for i in range(nombreCompétencesMax) if q[2*i+1] in compétences ]
            coefs = [ q[2*i+2] for i in range(nombreCompétencesMax) if q[2*i+1] in compétences ]
            if nom not in self.questions:
                self.questions[self.actuelNombreQuestions()] = nom
            i = np.where(self.questions == nom)[0]
            for (k,comp) in enumerate(comps):
                if comp not in self.compétences:
                    self.compétences[self.actuelNombreCompétences()] = comp
                j = np.where(self.compétences == comp)[0]
                self.coeff[i,j] = coefs[k]
            # retrait des compétences associées à cette question qui ont (éventuellement) disparu
            for j in [k for k in range(self.actuelNombreCompétences()) if self.compétences[k] not in comps]:
                self.coeff[i,j] = 0
                self.éval[i,j,:] = -1
        # retrait des questions devenues obsolètes
        for i in [k for k in range(self.actuelNombreQuestions()) if self.questions[k] not in [q[0] for q in modèle]]:
            self.questions[i] = ""
            self.coeff[i,:] = 0
            self.éval[i,:,:] = -1
        # recompression des tableaux
        self.questions[ self.questions == "" ] = "zz"  # changement temporaire pour les np.sort
        self.compétences[ self.compétences == "" ] = "zz"
        indsQ, indsC = np.argsort(self.questions), np.argsort(self.compétences)
        self.questions[ self.questions == "zz" ] = ""
        self.compétences[ self.compétences == "zz" ] = ""
        self.questions = self.questions[indsQ]
        self.compétences = self.compétences[indsC]
        self.coeff = self.coeff[indsQ][:,indsC]
        self.éval = self.éval[indsQ][:,indsC,:]

    def get_listeCatégoriesModificateurs(self) -> list:
        """
        Renvoie la liste des types demodificateurs possibles.
        Contient : "points fixes", "pourcentage"
        """
        return(["points fixes", "pourcentage"])

    def get_listeModificateursModèle(self) -> list:
        """
        Getter qui renvoie la liste des modificateurs (points fixes ET bonus/malus) sous
        forme de liste [(type,nom,valeur)]
        """
        liste = [ ("points fixes",a[0],a[1]) for a in self.pointsFixes ] + \
                [ ("pourcentage", a[0],a[1]) for a in self.modificateurs ]
        return(liste)

    def set_modificateursDepuisModèle(self, liste:list) -> None:
        """
        Prend en paramètre une liste [(type,nom,valeur)] et peuple les listes
        self.pointsFixes et self.modificateurs en conséquence
        Met à jour les éval
        """
        for a in [ b for b in liste if b[0] == "points fixes" if (b[1],b[2]) not in self.pointsFixes ]:
            self.pointsFixes.append((a[1],a[2]))
        iSupp = [ i for (i,val) in enumerate(self.pointsFixes) if val not in [(a[1],a[2]) for a in liste] ]
        for index in sorted(iSupp, reverse=True):
            del self.pointsFixes[index]
            self.évalPointsFixes[index:-1] = self.évalPointsFixes[index+1:]

        for a in [ b for b in liste if b[0] == "pourcentage" if (b[1],b[2]) not in self.modificateurs ]:
            self.modificateurs.append((a[1],a[2]))
        iSupp = [ i for (i,val) in enumerate(self.modificateurs) if val not in [(a[1],a[2]) for a in liste] ]
        for index in sorted(iSupp, reverse=True):
            del self.modificateurs[index]
            self.évalModificateurs[index:-1] = self.évalModificateurs[index+1:]

    def get_évaluationÉtudiantModèle(self, numÉtudiant:int) -> (list,bool):
        """
        Renvoie une paire contenant une liste de listes comprenant :

        - le nom de la question / du type de modificateur
        - le nom de la compétence évalué / du modificateur
        - le coefficient de la compétence / les points du modificateur
        - le niveau de l'étudiant numÉtudiant dans cette évaluation

        puis un bool pour la présence de l'étudiant.
        """
        présence = self.étudiants[numÉtudiant][2]
        liste = [ ["points fixes",a[0],a[1],self.évalPointsFixes[i,numÉtudiant]] \
                  for (i,a) in enumerate(self.pointsFixes) ]
        liste += [ ["pourcentage",a[0],a[1],self.évalModificateurs[i,numÉtudiant]] \
                   for (i,a) in enumerate(self.modificateurs) ]
        for i,nomQ in enumerate(self.questions[self.questions != ""]):
            for j,nomC in [(j,a) for (j,a) in enumerate(self.compétences) if self.coeff[i,j] != 0]:
                tmpListe = [nomQ,nomC,self.coeff[i,j],self.éval[i,j,numÉtudiant]]
                liste.append(tmpListe)
        return((liste,présence))

    def set_évaluationÉtudiantModèle(self, numÉtudiant:int, évals:list, présent:bool=True) -> None:
        """
        Fixe l'évaluation de l'étudiant numÉtudiant à partir d'une liste de liste comprenant :

        - le nom de la question / du type de modificateur
        - le nom de la compétence évalué / du modificateur
        - le coefficient de la compétence / les points du modificateur
        - le niveau de l'étudiant numÉtudiant dans cette évaluation

        Le bool fixe la présence de l'étudiant.
        """
        self.étudiants[numÉtudiant][2] = présent
        for comp in évals:
            if comp[0] == "points fixes":
                i = np.where(np.array([n[0] for n in self.pointsFixes]) == comp[1])
                self.évalPointsFixes[i,numÉtudiant] = comp[3]
            elif comp[0] == "pourcentage":
                i = np.where(np.array([n[0] for n in self.modificateurs]) == comp[1])
                self.évalModificateurs[i,numÉtudiant] = comp[3]
            else:
                i = np.where(self.questions == comp[0])[0]
                j = np.where(self.compétences == comp[1])[0]
                self.éval[i,j,numÉtudiant] = comp[3]

    def get_évaluationBDD(self) -> dict:
        """
        Construit les informations de l'évaluation (présence, points, modificateurs) selon un
        pattern utilisable par la BDD.
        """
        ret = {}
        ret['classe'] = self.classe
        ret['devoirType'] = self.typ
        ret['devoirNum'] = self.num
        ret['date'] = self.date
        ret['noteMax'] = self.noteMax
        ret['nvxAcq'] = self.nvxAcq
        ret['étudiants'] = self.étudiants
        ret['questions'] = [ (q,[(c,self.coeff[i,j]) for (j,c) in enumerate(self.compétences)      \
                                 if self.coeff[i,j] != 0 ]) for (i,q) in enumerate(self.questions) if q != "" ]
        ret['éval'] = [ (q,c,self.éval[i,j,:]) for (i,q),(j,c) in \
                        product(enumerate(self.questions),enumerate(self.compétences)) if self.coeff[i,j] != 0]
        ret['modificateurs'] = [ ('points fixes',p[0],p[1],self.évalPointsFixes[i,:]) \
                                 for i,p in enumerate(self.pointsFixes) ] + \
                                [ ('pourcentage',p[0],p[1],self.évalModificateurs[i,:]) \
                                 for i,p in enumerate(self.modificateurs) ]
        return(ret)

    def get_évaluationBDDUnÉtudiant(self, num:int) -> dict:
        """
        Construit les informations de l'évaluation (présence, points, modificateurs) selon un
        pattern utilisable par la BDD.
        """
        ret = {}
        ret['classe'] = self.classe
        ret['devoirType'] = self.typ
        ret['devoirNum'] = self.num
        ret['date'] = self.date
        ret['noteMax'] = self.noteMax
        ret['nvxAcq'] = self.nvxAcq
        ret['étudiant'] = self.étudiants[num]
        ret['questions'] = [ (q,[(c,self.coeff[i,j]) for (j,c) in enumerate(self.compétences)      \
                                 if self.coeff[i,j] != 0 ]) for (i,q) in enumerate(self.questions) if q != "" ]
        ret['éval'] = [ (q,c,self.éval[i,j,num]) for (i,q),(j,c) in \
                        product(enumerate(self.questions),enumerate(self.compétences)) if self.coeff[i,j] != 0]
        ret['modificateurs'] = [ ('points fixes',p[0],p[1],self.évalPointsFixes[i,num]) \
                                 for i,p in enumerate(self.pointsFixes) ] + \
                                [ ('pourcentage',p[0],p[1],self.évalModificateurs[i,num]) \
                                 for i,p in enumerate(self.modificateurs) ]
        return(ret)

    def set_évaluationBDD(self, évaluation:dict) -> None:
        """
        Récupère les évaluations du devoir depuis un dict et met à jour l'objet Devoir.

        Le dictionnaire à l'entrée contient les champs suivants :
        - présence : une liste de tuples (nomÉtudiant,prénomÉtudiant,présence)
        - éval : une liste de tuples (nomQuestion,nomCompétence,nomÉtudiant,prénomÉtudiant,note)
        - pointsFixes : une liste de tuples (nomItem,nomÉtudiant,prénomÉtudiant,note)
        - modifs : une liste de tuples (nomItem,nomÉtudiant,prénomÉtudiant,note) pour les pourcentages
        """
        étInds = {}  # Construction des indices (internes) associés aux étudiants par paire nom,prénom
        for i,val in enumerate(self.étudiants):
            étInds[(val[0],val[1])] = i
        for n,p,pres in évaluation['présence']:
            self.étudiants[étInds[(n,p)]] = [n,p,bool(pres)]
        for q,c,n,p,éval in évaluation['éval']:
            i = [k for (k,nQ) in enumerate(self.questions) if nQ == q ][0]
            j = [k for (k,nC) in enumerate(self.compétences) if nC == c ][0]
            self.éval[i,j,étInds[(n,p)]] = éval
        for pf,n,p,éval in évaluation['pointsFixes']:
            for i in  [k for (k,nP) in enumerate(self.pointsFixes) if nP[0] == pf ]:
                self.évalPointsFixes[i,étInds[(n,p)]] = éval
        for m,n,p,éval in évaluation['modifs']:
            for i in [k for (k,nM) in enumerate(self.modificateurs) if nM == m ]:
                self.évalModificateurs[i,j,étInds[(n,p)]] = éval

    # Traitement des données
    def calculerRésultatsParCompétences(self) -> dict:
        """
        Renvoie un dict, chaque élément étant pour une compétence (unique)
        - clé : le nom de la compétence
        - valeur : paire (éssais,réussites) les pourcentages d'essais des étudiants,
                   et de réussites des étudiants qui ont essayé
        """
        return(0)

    def calculerRésultatsBruts(self) -> np.ndarray:
        """
        Calcule les résultats bruts du devoir.

        Le calcul se fait ainsi : chaque compétence du devoir correspond à un certain nombre de points
        p (/nvxAcq-1) avec un coefficient c. Les résultats de l'étudiant sont :
             (sum(p*c) / sum((nvxAcq-1)*c) * (noteMax-totalPointsFixes) + pointsFixes)*modificateurs

        Renvoie le calcul sous la forme d'un tableau indexé sur les étudiants dans le tableau self.étudiants
        """
        return(0)

    def calculerRésultatsAjustés(self, traitement="aucun", note=20) -> np.ndarray:
        """
        Calcule les résultats ajustés du devoir après traitement des notes brutes.

        Les traitements disponibles sont :
        - "aucun" : rien n'est fait
        - "moyenne" : la moyenne de la classe est imposée à la valeur de note
        - "médiane" : la médiane de la classe est imposée à la valeur de note
        - "meilleure" : la meilleure note est imposée à la valeur de note, ce qui définit un coefficient
                        multiplicatif, qui sera appliqué à toutes les copies.

        Renvoie le calcul sous la forme d'un tableau indexé sur les étudiants dans le tableau self.étudiants
        """
        return(0)

    def calculerTauxDeComplétion(self) -> np.ndarray:
        """
        Calcule le teux de complétion du devoir pour chaque étudiant, en pourcentage du nombre de questions abordées.

        Renvoie le calcul sous la forme d'un tableau indexé sur les étudiants dans le tableau self.étudiants
        """
        return(0)

    def calculerRésultatsClasse(self) -> dict:
        """
        Calcule les résultats après traitement. Renvoie un dict avec les éléments suivants:
        - clé 'moyenne': la moyenne de la classe
        - clé 'médiane': la médiane de la classe
        - clé 'écart-type': l'écart-type de la classe
        - clé 'premier': la meilleure note de la classe
        - clé 'dernier': la moins bonne note de la classe
        - clé 'quantité' : la quantité moyenne de sujet traitée, en pourcentage du nombre de questions
        - clé 'histogramme' : une liste de int contenant l'histogramme par deux points (le nombre
                              d'étudiants dans ]0,2], puis ]2,4] etc...)
        - pour chaque malus, une clé avec le nom du malus : le nombre d'étudiants ayant subi le malus
        - pour chaque bloc de points fixes, une clé avec le nom : la moyenne de la classe sur ce fixe
        """
        return(0)

    # Tests
    def test_créerQuestionsDevoir(self, évals=False):
        """
        Auto-génère une liste de questions pour les tests.
        Cette fonction n'est pas censée être utilisée hors des tests.

        Si évals vaut True, elle est change la classe pour y mettre 5 étudiants et les évaluations correspondantes.
        """
        q1 = ("1.",[("Connaître les dimensions fondamentales",1),("Connaître les dimensions dérivées",1)])
        q2 = ("2.a.",[("Vérifier l'homogénéité",2)])
        q3 = ("2.b.",[("Prévoir un résultat par AD",3)])
        for q in [q1,q2,q3]:
            self.questions[self.actuelNombreQuestions()] = q[0]
            for comp in q[1]:
                if comp[0] not in self.compétences:
                    self.compétences[self.actuelNombreCompétences()] = comp[0]
                i,j = np.where(self.questions == q[0])[0], np.where(self.compétences == comp[0])[0]
                self.coeff[i,j] = comp[1]
        if évals:
            self.étudiants = [["Alp","Selin",True], \
                              ["Bazin","Jérémy",True], \
                              ["Morceaux","Jérémy",True], \
                              ["Dias","Léo",True], \
                              ["Gourgues","Maxime",False]]
            self.étudiants.sort(key=lambda a: a[0])
            self.nvxAcq = 2
            self.éval = np.array([[[ 1, 1, 1, 1, 1], \
                               [ 1, 1,-1, 0, 0], \
                                   [-1,-1,-1,-1,-1], \
                                   [-1,-1,-1,-1,-1]], \
                                  [[-1,-1,-1,-1,-1], \
                                   [-1,-1,-1,-1,-1], \
                                   [ 1, 1,-1, 1, 0], \
                                   [-1,-1,-1,-1,-1]], \
                                  [[-1,-1,-1,-1,-1], \
                                   [-1,-1,-1,-1,-1], \
                                   [-1,-1,-1,-1,-1], \
                                   [ 0, 1, 0,-1, 1]]],dtype=int)
            self.pointsFixes = [("Présentation",1), ("Correction de la langue",1)]
            self.modificateurs = [("Homogénéité",-0.15)]
            self.évalPointsFixes = np.array([[1,1,0.5,0,0.5],[1,1,0,0.5,1]],dtype=float)
            self.évalModificateurs = np.array([[0,0,0,1,1]],dtype=int)


## Traitements sur un ensemble de devoirs
def compétenceÉtudiant(listeDevoirs:list, nomÉtudiant:str, prénomÉtudiant:str, compétence:str) -> list:
    """
    Prend en paramètre une liste de devoirs, un étudiant et une compétence, puis renvoie une liste de paires
    (pourcentageEssais,pourcentageRéussite). Chaque paire correspond à un devoir de la liste, et est classée
    par ordre chronologique.
    """
    return(0)


## Partie pour les tests indépendants
if __name__ == '__main__':
    devoir = Devoir('MPSI','DS',1,'20.09.2017',2,[('a','a')],20,[("Présentation",2)],[("Homogénéité",-0.15)])
    devoir.test_créerQuestionsDevoir(True)
