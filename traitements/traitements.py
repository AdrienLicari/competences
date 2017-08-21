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
    """
    maxQuestions = 100
    maxCompétences = 100
    # Fonctions d'intéraction avec l'interface
    def __init__(self, classe:str, typ:str, num:int, date:str, nvxAcq:int, étudiants:list, \
                 noteMax:int, pointsFixes:list, modificateurs:list) -> 'Devoir':
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
        Fonction pour tester qu'un devoir correspond à une liste [classe,type,num,date]
        """
        return(self.classe == liste[0] and self.typ == liste[1] \
               and self.num == liste[2] and self.date == liste[3])

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

    def get_niveauxAcquisition(self) -> int:
        """
        Getter simple pour les niveaux d'acquisition.
        """
        return(self.nvxAcq)

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

    def get_évaluationÉtudiantModèle(self, numÉtudiant:int) -> (list,bool):
        """
        Renvoie une paire contenant une liste de listes comprenant :

        - le nom de la question
        - le nom de la compétence évalué
        - le coefficient de la compétence
        - le niveau de l'étudiant numÉtudiant dans cette évaluation

        puis un bool pour la présence de l'étudiant.
        """
        présence = self.étudiants[numÉtudiant][2]
        liste = []
        for i,nomQ in enumerate(self.questions[self.questions != ""]):
            for j,nomC in [(j,a) for (j,a) in enumerate(self.compétences) if self.coeff[i,j] != 0]:
                tmpListe = [nomQ,nomC,self.coeff[i,j],self.éval[i,j,numÉtudiant]]
                liste.append(tmpListe)
        return((liste,présence))

    def set_évaluationÉtudiantModèle(self, numÉtudiant:int, évals:list, présent:bool=True) -> None:
        """
        Fixe l'évaluation de l'étudiant numÉtudiant à partir d'une liste de liste comprenant :

        - le nom de la question
        - le nom de la compétence évalué
        - le coefficient de la compétence
        - le niveau de l'étudiant numÉtudiant dans cette évaluation.

        Le bool fixe la présence de l'étudiant.
        """
        self.étudiants[numÉtudiant][2] = présent
        for comp in évals:
            i = np.where(self.questions == comp[0])[0]
            j = np.where(self.compétences == comp[1])[0]
            self.éval[i,j,numÉtudiant] = comp[3]

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
