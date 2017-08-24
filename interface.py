#!/usr/bin/python3

"""
Module principal gérant l'interface graphique.
"""


## Temporaire : données hardcodées pour la phase de mise en place / tests
# La mise en place de ces schémas est la même que pour la BDD
data_classes = ["Toutes","MPSI","MP","PSI"]
data_étudiants = [["MPSI","Alp","Selin"],  # id, idClasse, nom, prénom
                  ["MPSI","Bazin","Jérémy"],
                  ["MPSI","Morceaux","Jérémy"],
                  ["MPSI","Dias","Léo"],
                  ["MPSI","Gourgues","Maxime"],
                  ["MP","Chevasson","Raphaël"],
                  ["MP","Clémenceau","Sandra"],
                  ["MP","Hubert","Olive"],
                  ["MP","Bornet","Clément"],
                  ["PSI","Grither","Noëmie"],
                  ["PSI","Berdery","Mathieu"],
                  ["PSI","Milhem","William"]]
data_competenceType = ["Toutes","Connaissance","Technique","Raisonnement"]
data_competenceChapitre = ["Tous","Généralités","Mécanique","Info_BDD"]
data_competence = [["Connaître les unités standard","Connaissance","Généralités"],  # nom, type, chapitre
                   ["Connaître les dimensions fondamentales","Connaissance","Généralités"],
                   ["Connaître les dimensions dérivées","Connaissance","Généralités"],
                   ["Vérifier l'homogénéité","Technique","Généralités"],
                   ["Prévoir un résultat par AD","Technique","Généralités"],
                   ["Propager une incertitude","Technique","Généralités"],
                   ["Connaître le principe d'inertie","Connaissance","Mécanique"],
                   ["Connaître la poussée d'Archimède","Connaissance","Mécanique"],
                   ["Définir le travail d'une force","Connaissance","Mécanique"],
                   ["Calculer le travail d'une force","Technique","Mécanique"],
                   ["Exprimer l'accélération dans une base cylindrique","Technique","Mécanique"],
                   ["Calculer un moment scalaire par bras de levier","Technique","Mécanique"],
                   ["Interpréter une accélération centripète","Raisonnement","Mécanique"],
                   ["Interpréter la conservation de l'énergie","Raisonnement","Mécanique"],
                   ["Effectuer un bilan des forces","Raisonnement","Mécanique"],
                   ["Effectuer une requête simple","Technique","Info_BDD"],
                   ["Effectuer une jointure","Technique","Info_BDD"]]
data_devoirType = ["Tous","DS","DM","interro"]
data_devoir = [["MPSI","DS",1,"20.09.2017"],
               ["MPSI","DS",2,"14.10.2017"],
               ["MPSI","interro",1,"15.09.2017"],
               ["PSI","DS",1,"20.11.2017"]]

## imports
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from autocompletion import *
from fenetresDevoir import *
from traitements.traitements import *
from dbManagement.dbManagement import BaseDeDonnées

## Classe regroupant des créations de fenêtres sans intéraction
class FenêtresInformation(object):
    """
    Classe regroupant des créations de fenêtres sans intéraction avec l'utilisateur
    """
    def affichageErreur(parent, texte:str) -> None:
        """
        Une fonction utilisée pour afficher les messages d'erreur.
        """
        dialogueErreur = Gtk.MessageDialog(parent, 0, Gtk.MessageType.ERROR, \
                    Gtk.ButtonsType.CANCEL, "Une erreur s'est produite")
        dialogueErreur.format_secondary_text(texte)
        dialogueErreur.run()
        dialogueErreur.destroy()

    def demandeConfirmation(parent, texte:str) -> None:
        """
        Une fonction utilisée pour demander une confirmation.
        Renvoie True ou False.
        """
        dialogueConf = Gtk.MessageDialog(parent, 0, Gtk.MessageType.QUESTION, \
                    Gtk.ButtonsType.OK_CANCEL, "Confirmation")
        dialogueConf.format_secondary_text(texte)
        réponse = (dialogueConf.run() == Gtk.ResponseType.OK)
        dialogueConf.destroy()
        return(réponse)


## Classe pour les dialogues de demande
class FenetreDemande(Gtk.Dialog):
    """
    Classe gérant la construction d'une fenêtre popup pour créer un objet ou demander un choix.

    Peut gérer le cas de la construction avec plusieurs champs.
    """
    def __init__(self, parent:Gtk.Window, label:str, demandes:list, **kwargs):
        """
        Constructeur.

        Permet de créer la fenêtre qui aura les demandes fournies.

        La liste demandes contient des paires (label, choix). Les possibilités sont les suivantes :
        - si choix est une str du type "libre_type", alors une entrée clavier est demandée ;
        - si choix est une paire (ListStore,int), alors on demande à l'utilisateur de choisir parmi
          les entrées du ListStore, colonne int.
        - si choix est la str "date" alors un calendrier est inséré et une date est demandée
        - si choix est la str "fichier", alors un bouton donnant accès à un sélecteur de fichiers est inséré

        Les paramètres par keywords sont optionnels:
        - défauts est un dictionnaire reliant la clé "label" (associée à la liste demandes)
          avec une éventuelle valeur par défaut.
        - infobulles est un dictionnaire reliant la clé "label" (associée à la liste demandes)
          avec une infobulle à placer sur le label
        """
        Gtk.Dialog.__init__(self, " ", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = self.get_content_area()
        titre = Gtk.Label(label)
        box.add(titre)
        self.grille = Gtk.Grid()
        box.add(self.grille)
        ligne = 0
        self.demandes = demandes
        self.fichiers = []  # utilisé dans le cas de demandes de fichiers
        # gestion des kwargs
        défauts, infobulles = {}, {}
        if "défauts" in kwargs:
            défauts = kwargs["défauts"]
        if "infobulles" in kwargs:
            infobulles = kwargs["infobulles"]
        # mise en place des paires label / widgets
        for txt,dem in demandes:
            label = Gtk.Label(txt)
            label.set_xalign(1)
            label.set_yalign(0)
            self.grille.attach(label,0,ligne,1,1)
            if type(dem) == str and "libre_" in dem:
                widget = Gtk.Entry()
                widget.set_hexpand(True)
                widget.set_activates_default(True)
                if txt in défauts:
                    widget.set_text(str(défauts[txt]))
                self.grille.attach(widget,1,ligne,1,1)
            elif type(dem) == str and dem == "date":
                widget = Gtk.Calendar()
                widget.set_hexpand(True)
                self.grille.attach(widget,1,ligne,1,1)
            elif type(dem) == str and dem == "fichier":
                widget = Gtk.Button("Choisir fichier")
                widget.connect("clicked", self.sousFenêtreFichier, len(self.fichiers))
                self.grille.attach(widget,1,ligne,1,1)
                self.fichiers.append(None)
            elif type(dem) == tuple:
                widget = Gtk.ComboBox.new_with_model(dem[0])
                widget.set_hexpand(True)
                renderer = Gtk.CellRendererText()
                widget.pack_start(renderer, True)
                widget.add_attribute(renderer, "text", dem[1])
                self.grille.attach(widget,1,ligne,1,1)
            else:
                FenêtresInformation.affichageErreur(self, \
                                                    "Demande non gérée dans le constructeur de FenetreDemande ; " \
                                                    "le type proposé est {}".format(type(dem)))
            ligne += 1
            if txt in infobulles:
                label.set_tooltip_text(infobulles[txt])
        boutonOk = self.get_widget_for_response(response_id=Gtk.ResponseType.OK)
        boutonOk.set_can_default(True)
        boutonOk.grab_default()
        # Lancement de la fenêtre
        self.show_all()

    def récupèreInfos(self) -> list:
        """
        Fonction appelée pour récupérer les infos dans les champs de la fenêtre.
        """
        retours = []
        i = 0
        for txt,dem in self.demandes:
            if type(dem) == str and "libre" in dem:
                retours.append(self.grille.get_child_at(1,i).get_text())
            elif type(dem) == str and dem == "date":
                date = self.grille.get_child_at(1,i).get_date()
                date_str = "{:02d}.{:02d}.{:4d}".format(date[2],date[1],date[0])
                retours.append(date_str)
            elif type(dem) == str and dem == "fichier":
                retours.append(self.fichiers[0])
                self.fichiers.pop(0)
            elif type(dem) == tuple:
                comboBox = self.grille.get_child_at(1,i)
                retours.append(dem[0][comboBox.get_active()][dem[1]])
            i += 1
        return(retours)

    def sousFenêtreFichier(self, bouton:Gtk.Button, numFichier:int) -> None:
        """
        Callback utilisé pour lancer une fenêtre sélecteur de fichier.

        Modifie le texte du bouton une fois le fichier sélectionné.
        """
        dialogue = Gtk.FileChooserDialog("Choisissez un fichier", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        réponse = dialogue.run()
        if réponse == Gtk.ResponseType.OK:
            self.fichiers[numFichier] = dialogue.get_filename()
        dialogue.destroy()
        nomFichier = self.fichiers[numFichier].split("/")[-1]
        bouton.set_label(nomFichier)


## Classe de la fenêtre principale
class FenêtrePrincipale(object):
    """
    Classe gérant la fenêtre de l'application.
    """
    # Fonctions d'ordre général
    def fermetureGlobale(self,*args):
        """
        Handler pour quitter la fenêtre.
        """
        Gtk.main_quit(*args)

    def filtreModifiables(self,model,it,data) -> bool:
        """
        Fonction pour rendre visible uniquement les entités modifiables ou supprimables.
        Est utilisé dans le cas de modèles contenant l'entrée "Tous" pour l'exclure.
        """
        if model[it][0] in ["Toutes","Tous"]:
            return(False)
        return(True)

    def suppressionÉlémentsAssociésÀCatégorie(self, strCat:str, modèleÉléments:Gtk.ListStore, ind:int) -> None:
        """
        Fonction générique utilisée pour supprimer tous les éléments associés à une catégorie (par exemple
        tous les étudiants associés à une classe). Le paramètre ind permet de préciser quel champ du modèle
        correspond à la catégorie.
        """
        it = modèleÉléments.get_iter_first()
        while it is not None and modèleÉléments.iter_is_valid(it):
            if modèleÉléments[it][ind] == strCat:
                modèleÉléments.remove(it)
            else:
                it = modèleÉléments.iter_next(it)

    def suppressionObjetSimple(self, texte:str, modèle:Gtk.ListStore, texteConfirmation:str, col:int=0) -> str:
        """
        Fonction générique utilisée pour la suppression d'un objet simple (classe, type de compétence...).
        Le texte de confirmation est pensé pour contenir le nom de l'élément sélectionné, il doit donc contenir
        {} pour pouvoir appeler str.format.
        L'affichage pour le choix dans le modèle s'appuie sur la colonne col.
        Renvoie le nom de l'objet supprimé, ou None si l'opération est annulée.
        """
        filtre = modèle.filter_new()
        filtre.set_visible_func(self.filtreModifiables)
        dialogue = FenetreDemande(self.fenêtrePrincipale, texte, [("Choix",(filtre,col))])
        réponse = dialogue.run()
        infos = dialogue.récupèreInfos()
        dialogue.destroy()
        if réponse == Gtk.ResponseType.OK:
            it = modèle.get_iter_first()
            while infos[0] != modèle[it][col]:
                it = modèle.iter_next(it)
            nom = modèle[it][col]
            if FenêtresInformation.demandeConfirmation(self.fenêtrePrincipale,texteConfirmation.format(nom)):
                modèle.remove(it)
                return(nom)
        return(None)

    def sélectionDepuisAfficheurListe(self, afficheur:str, msgErr:str) -> tuple:
        """
        Fonction générique utilisée pour supprimer depuis une liste ordonnable et triable.

        - L'afficheur est identifié par son identifiant glade
        - msgErr est utilisée en cas d'absence de sélection de la part de l'utilisateur

        Renvoie une paire contenant le modèle lié à l'affichage et l'itérateur sélectionné ;
        s'il n'y a pas de sélection, renvoie (None,None).
        """
        modèleSup, it = self.builder.get_object(afficheur).get_selection().get_selected()
        if it is None:
            FenêtresInformation.affichageErreur(self.fenêtrePrincipale,msgErr)
            return((None,None))
        else:
            modèle = modèleSup
            while hasattr(modèle,'get_model'):
                it = modèle.convert_iter_to_child_iter(it)
                modèle =  modèle.get_model()
            return(modèle, it)

    def suppressionDepuisAfficheurListe(self, afficheur:str, texteConfirmation:'function', msgErr:str,
                                        dbFonction:'function'=None) -> None:
        """
        Fonction générique utilisée pour supprimer depuis une liste ordonnable et triable.

        - L'afficheur est identifié par son identifiant glade
        - texteConfirmation est une fonction à un paramètre qui construit la chaîne de caractère à partir
          de la ligne récupérée
        - msgErr est utilisée en cas d'absence de sélection de la part de l'utilisateur
        - dbFunction est une fonction prenant en paramètre modèle et it et qui gère la mise à jour de la db
        """
        modèle, it = self.sélectionDepuisAfficheurListe(afficheur, msgErr)
        if it is not None:
            msg = texteConfirmation(modèle[it])
            if FenêtresInformation.demandeConfirmation(self.fenêtrePrincipale,msg):
                if dbFonction is not None:
                    dbFonction(modèle,it)
                modèle.remove(it)

    def créationNouvelObjet(self, label:str, demandes:list, **kwargs) -> list:
        """
        Fonction générique utilisée pour la création d'un nouvel objet.

        La liste demandes contient des paires (label, choix). Les possibilités sont documentées dans la
        docstring de FenetreDemande.__init__ ; les demandes de type libre_str ou libre_int permettent de
        demander des conversions.
        Ces conversions peuvent lever une ValueError. Elle doit être gérée par l'appelant.

        Renvoie la liste correspondant aux données demandées s'il y a réponse, None sinon.
        """
        # Préparation de la fenêtre
        dialogue = FenetreDemande(self.fenêtrePrincipale, label, demandes, **kwargs)
        réponse = dialogue.run()
        liste = dialogue.récupèreInfos()
        dialogue.destroy()
        if réponse == Gtk.ResponseType.OK:
            for i in range(len(liste)):
                if type(demandes[i][1]) == str and demandes[i][1] == "libre_int":
                    try:
                        liste[i] = int(liste[i])
                    except(ValueError):
                        FenêtresInformation.affichageErreur(self.fenêtrePrincipale, \
                                                            "Un champ de type entier a été mal entré.")
            if "" in liste:
                FenêtresInformation.affichageErreur(dialogue,"Vous devez remplir tous les champs")
            else:
                return(liste)
            return(None)

    def changerSélecteurs(self,dummy):
        """
        Callback pour les sélecteurs qui filtrent les listes actives.
        """
        self.classeActive = self.modèleClasses[self.builder.get_object("sélecteurClasse").get_active()][0]
        self.builder.get_object("modèleÉtudiantsFiltré").refilter()
        self.builder.get_object("modèleDevoirFiltré").refilter()
        self.builder.get_object("modèleCompétenceFiltré").refilter()

    def chargerInfosDepuisBDD(self):
        """
        Fonction permettant de charger les informations d'une bdd. Commence par vider les informations
        précédentes.
        """
        self.modèleCompétenceType.clear()
        self.modèleCompétenceType.append(["Toutes"])
        for elt in self.bdd.récupèreCompétenceTypes():
            self.modèleCompétenceType.append([elt['nom']])
        self.builder.get_object("sélecteurCompétenceType").set_active(0)
        self.modèleCompétenceChapitre.clear()
        self.modèleCompétenceChapitre.append(["Tous"])
        for elt in self.bdd.récupèreCompétenceChapitres():
            self.modèleCompétenceChapitre.append([elt['nom']])
        self.builder.get_object("sélecteurCompétenceChapitre").set_active(0)
        self.modèleCompétence.clear()
        for elt in self.bdd.récupèreCompétencesComplet():
            self.modèleCompétence.append([elt['nom'],elt['type'],elt['chapitre']])
        self.modèleClasses.clear()
        self.modèleClasses.append(["Toutes"])
        for elt in self.bdd.récupèreClasses():
            self.modèleClasses.append([elt['nom']])
        self.builder.get_object("sélecteurClasse").set_active(0)
        self.modèleÉtudiants.clear()
        for classe in [ a[0] for a in self.modèleClasses ]:
            for elt in self.bdd.récupèreÉtudiants(classe):
                self.modèleÉtudiants.append([classe,elt['nom'],elt['prenom']])
        self.modèleDevoirType.clear()
        self.modèleDevoirType.append(["Tous"])
        for elt in self.bdd.récupèreTypesDevoirs():
            self.modèleDevoirType.append([elt['nom']])
        self.builder.get_object("sélecteurDevoirType").set_active(0)
        compétences = [ a[0] for a in self.modèleCompétence ]
        for elt in self.bdd.récupèreDevoirs():
            idDev, cl, typ, num, date, noteMax, nvxAcq = elt['id'], elt['classe'], elt['type'], elt['numéro'], \
                                                         elt['date'], elt['noteMax'], elt['nvxAcq']
            self.modèleDevoir.append([cl,typ,num,date])
            étudiants = [(e['nom'],e['prenom']) for e in self.bdd.récupèreÉtudiants(cl)]
            self.devoirs.append(Devoir(cl,typ,num,date,noteMax,nvxAcq,étudiants))
            self.devoirs[-1].set_questionsDepuisModèle(self.bdd.récupérerQuestions(idDev),compétences)
            self.devoirs[-1].set_modificateursDepuisModèle(self.bdd.récupèreModificateurs(idDev))
            self.devoirs[-1].set_noteMax(noteMax)
            self.devoirs[-1].set_niveauxAcquisition(nvxAcq)

    # Fonctions liées à la gestion des classes / étudiants
    def chargerClasses(self):
        """
        Fonction qui charge les classes / étudiants dans les ListStore adaptés.
        Implémentation temporaire.
        """
        # Peuplement à la main ; à modifier
        for cl in data_classes:
            self.modèleClasses.append([cl])
        self.builder.get_object("sélecteurClasse").set_active(0)
        for et in data_étudiants:
            self.modèleÉtudiants.append(et)

    def créerNouvelleClasse(self,dummy):
        """
        Callback utilisé pour la création d'une nouvelle classe.
        """
        liste = self.créationNouvelObjet("Entrez le nom de la nouvelle classe",\
                                         [("Nom","libre_str")])
        if liste is not None:
            if liste in [ a[:] for a in self.modèleClasses ]:
                FenêtresInformation.affichageErreur(self.fenêtrePrincipale,"Cette classe existe déjà")
            else:
                self.modèleClasses.append(liste)
                self.bdd.ajoutClasse(liste[0])

    def supprimerClasse(self,dummy):
        """
        Callback utilisé pour la suppression d'une classe.
        """
        classeSupprimée =  self.suppressionObjetSimple("Sélectionnez la classe à supprimer", \
                                            self.modèleClasses, \
                                            "Êtes-vous sûr de vouloir supprimer la classe {} " \
                                            "ainsi que tous les étudiants qui la composent ?")
        if classeSupprimée is not None:
            self.suppressionÉlémentsAssociésÀCatégorie(classeSupprimée, self.modèleÉtudiants, 0)
            [ self.bdd.retraitÉtudiant(ét['nom'],ét['prenom']) for ét in self.bdd.récupèreÉtudiants(classeSupprimée) ]
            self.bdd.retraitClasse(classeSupprimée)

    def ajouterÉtudiant(self,dummy):
        """
        Callback utilisé pour la création d'un étudiant.
        """
        filtre = self.modèleClasses.filter_new()
        filtre.set_visible_func(self.filtreModifiables)
        liste = self.créationNouvelObjet("Entrez le nouvel étudiant",\
                                         [("Classe",(filtre,0)),("Nom","libre_str"),("Prénom","libre_str")])
        if liste is not None:
            if liste in [ a[:] for a in self.modèleÉtudiants ]:
                FenêtresInformation.affichageErreur(self.fenêtrePrincipale,"Cet étudiant existe déjà")
            else:
                self.modèleÉtudiants.append(liste)
                self.bdd.ajoutÉtudiant(liste[1], liste[2], liste[0])

    def ajouterÉtudiantsDepuisFichier(self,dummy):
        """
        Fonction pour ajouter une liste d'étudiants depuis un fichier
        correctement formaté.
        """
        # Choix du fichier
        filtre = self.modèleClasses.filter_new()
        filtre.set_visible_func(self.filtreModifiables)
        explication = "Sélectionnez un fichier contenant un étudiant par ligne, nom puis prénom, " \
                      "séparés par un point-virgule."
        classe, nomFichier = self.créationNouvelObjet("Ajouter une liste d'étudiants", \
                                                      [("Classe",(filtre,0)),(explication,"fichier")])
        # Lecture du fichier
        séparateur = ";"
        fichier = open(nomFichier,'r')
        for ligne in fichier:
            nom,prénom = ligne.split(séparateur)
            self.modèleÉtudiants.append([classe,nom,prénom[:-1]])  # on exclut le '\n' de fin de ligne
            self.bdd.ajoutÉtudiant(nom, prénom[:-1], classe)
        fichier.close()

    def supprimerÉtudiant(self,dummy):
        """
        Callback utilisé pour la suppression d'un étudiant.
        """
        constructionMsg = lambda a: "Voulez-vous supprimer l'étudiant {} {} ?".format(a[1],a[2])
        gestionDb = lambda mod,it: self.bdd.retraitÉtudiant(mod[it][1],mod[it][2])
        self.suppressionDepuisAfficheurListe("afficheurÉtudiants", constructionMsg, \
                                             "Vous n'avez pas sélectionné d'étudiant",gestionDb)

    def filtreVisibilitéParClasse(self,model,it,data):
        """
        Fonction pour rendre visible uniquement les étudiants de la classe active
        """
        if self.classeActive in ["Toutes","Tous"]:
            return(True)
        return(model[it][0] == self.classeActive)

    # Fonctions liées à la gestion des devoirs
    def chargerDevoirs(self):
        """
        Fonction qui charge les devoirs dans les ListStore adaptés.
        Implémentation temporaire.
        """
        # Peuplement à la main ; à modifier
        for dt in data_devoirType:
            self.modèleDevoirType.append([dt])
        self.builder.get_object("sélecteurDevoirType").set_active(0)
        for dv in data_devoir:
            étudiants = [(a[1],a[2]) for a in data_étudiants if a[0] == dv[0]]
            self.modèleDevoir.append(dv)
            self.devoirs.append(Devoir(dv[0],dv[1],dv[2],dv[3],20,2,étudiants))
        self.devoirs[0].test_créerQuestionsDevoir(True)
        self.devoirs[1].test_créerQuestionsDevoir()

    def créerNouveauDevoirType(self,dummy):
        """
        Callback pour créer un nouveau type de devoir.
        """
        liste = self.créationNouvelObjet("Créez un nouveau type de devoir", [("Nom","libre_str")])
        if liste is not None:
            if liste in [ a[:] for a in self.modèleDevoirType ]:
                FenêtresInformation.affichageErreur(self.fenêtrePrincipale,"Ce type de devoir existe déjà")
            else:
                self.modèleDevoirType.append(liste)
                self.bdd.ajoutTypeDevoir(liste[0])

    def supprimerDevoirType(self,dummy):
        """
        Callback pour supprimer un type de devoir.
        """
        typeSupprimé =  self.suppressionObjetSimple("Sélectionnez le type de devoir à supprimer", \
                                                    self.modèleDevoirType, \
                                                    "Êtes-vous sûr de vouloir supprimer la catégorie {} " \
                                                    "ainsi que tous les devoirs associés ?")
        if typeSupprimé is not None:
            self.suppressionÉlémentsAssociésÀCatégorie(typeSupprimé, self.modèleDevoir, 1)
            devoirs = [ a['id'] for a in self.bdd.récupèreDevoirs() if a['type'] == typeSupprimé ]
            [ self.bdd.retraitDevoir(i) for i in devoirs ]
            self.bdd.retraitTypeDevoir(typeSupprimé)

    def récupérerIdDevoir(self,dv) -> int:
        return([ a['id'] for a in self.bdd.récupèreDevoirs() \
                 if a['classe'] == dv[0] and a['type'] == dv[1] and a['numéro'] == dv[2] ][0])

    def créerDevoir(self,dummy):
        """
        Callback pour créer un nouveau devoir.
        """
        séparateur = ";"
        filtreC = self.modèleClasses.filter_new()
        filtreT = self.modèleDevoirType.filter_new()
        filtreC.set_visible_func(self.filtreModifiables)
        filtreT.set_visible_func(self.filtreModifiables)
        str_fich = "Fichier de questions (optionnel)"
        explication_fich = "Vous pouvez optionnellement charger un fichier définissant les questions, chaque ligne " \
                           "correspondant à une question sous la forme :\n" \
                           "nomQuestion;compétence1;coeffCompétence1;compétence2;coeffCompétence2..."
        str_niveauxComp = "Niveaux d'acquisition"
        explication_nvx = "Le nombre de niveaux d'acquisition (pour un simple acquis/non acquis, mettez 2 ; " \
                          "pour acquis/en cours d'acquisition/non acquis, mettez 3 etc..."
        demandes = [("Classe",(filtreC,0)), ("Type",(filtreT,0)), ("Numéro","libre_int"), ("Date","date"), \
                    ("Note maximale","libre_int"),(str_niveauxComp,"libre_int"),(str_fich,"fichier")]
        déf = {str_niveauxComp:2, "Note maximale":20}
        infos= {str_niveauxComp:explication_nvx, str_fich:explication_fich}
        dv = self.créationNouvelObjet("Créez un nouveau devoir", demandes, défauts=déf, infobulles=infos)
        if dv is not None:
            if True not in [ d.correspondÀ(dv[0:3]) for d in self.devoirs ]:
                étudiants = [ (a[0],a[1]) for a in self.modèleÉtudiants if a[0] == dv[0] ]
                self.devoirs.append(Devoir(dv[0],dv[1],dv[2],dv[3],dv[4],dv[5],étudiants))
                self.modèleDevoir.append([dv[0],dv[1],dv[2],dv[3]])
                self.bdd.ajoutDevoir(dv[0],dv[1],dv[2],dv[3],dv[4],dv[5])
                if dv[6] != None:
                    fichier = open(dv[6],'r')
                    questions = []
                    try:
                        for ligne in fichier:
                            questions.append(ligne[:-1].split(séparateur))
                            n = len(questions[-1])
                            for i in [ k for k in range(n) if (k > 0 and k%2 == 0) ]:  # conversion des entiers
                                questions[-1][i] = int(questions[-1][i])
                        qBDD = [ (q[0], [(q[2*i+1],q[2*i+2]) for i in range(len(q)//2)]) for q in questions ]
                        compétences = listeCompétences = [ ligne[0] for ligne in self.modèleCompétence ]
                        self.devoirs[-1].set_questionsDepuisModèle(questions, compétences)
                        idDev = self.récupérerIdDevoir(dv)
                        self.bdd.créerQuestions(idDev, qBDD)
                    except(ValueError):
                        FenêtresInformation.affichageErreur(self.fenêtrePrincipale, \
                                                            "Un coefficient n'est pas un nombre dans le fichier.")
            else:
                FenêtresInformation.affichageErreur(self.fenêtrePrincipale, \
                                                    "Ce devoir existe déjà.")

    def supprimerDevoir(self,dummy):
        """
        Callback utilisé pour la suppression d'un devoir.
        """
        constructionMsg = lambda a: "Voulez-vous supprimer le devoir {} {} des {} ?".format(a[1],a[2],a[0])
        def dbFonction(mod,it):
            dv = [ a for a in mod[it] ]
            self.bdd.retraitDevoir(self.récupérerIdDevoir(dv))
            dev = [ a for a in self.devoirs if a.correspondÀ(mod[it][0:3]) ][0]
            self.devoirs.remove(dev)
        self.suppressionDepuisAfficheurListe("afficheurDevoirs", constructionMsg, \
                                             "Vous n'avez pas sélectionné de devoir", dbFonction)

    def modifierQuestionsDevoir(self,dummy):
        """
        Callback utilisé pour la modification des questions dans un devoir.
        Délègue à la classe FenêtreQuestionsDevoir.
        """
        modèle,it = self.sélectionDepuisAfficheurListe("afficheurDevoirs", \
                                                       "Vous n'avez pas sélectionné de devoir")
        if it is not None:
            dev = [d for d in self.devoirs if d.correspondÀ(modèle[it][0:3])][0]
            cl, typ, num = tuple(modèle[it][0:3])
            idDev = [ a['id'] for a in self.bdd.récupèreDevoirs() if dev.correspondÀ([a['classe'], \
                                                                                      a['type'],a['numéro']])][0]
            fenêtreQuestions = FenêtreQuestionsDevoir(dev, self.builder, self.bdd, idDev)

    def évaluerDevoir(self,dummy):
        """
        Callback utilisé pour lancer l'évaluation d'un devoir.
        Délègue à la classe FenêtreÉvaluationDevoir.
        """
        modèle,it = self.sélectionDepuisAfficheurListe("afficheurDevoirs", \
                                                       "Vous n'avez pas sélectionné de devoir")
        if it is not None:
            dev = [d for d in self.devoirs if d.correspondÀ(modèle[it])][0]
            fenêtreÉvaluation = FenêtreÉvaluationDevoir(dev, self.builder)

    def filtreVisibilitéDevoirs(self,model,it,data):
        """
        Fonction pour rendre visible uniquement les devoirs d'un type / d'une classe
        """
        typeActif = self.modèleDevoirType[self.builder.get_object("sélecteurDevoirType").get_active()][0]
        return( (typeActif == "Tous" or typeActif == model[it][1]) and \
          (self.classeActive == "Toutes" or self.classeActive == model[it][0]))

    # Fonctions liées à la gestion des compétences
    def chargerCompétences(self):
        """
        Fonction qui charge les classes dans les ListStore adaptés.
        Implémentation temporaire.
        """
        # Peuplement à la main ; à modifier
        for ty in data_competenceType:
            self.modèleCompétenceType.append([ty])
        self.builder.get_object("sélecteurCompétenceType").set_active(0)
        for ch in data_competenceChapitre:
            self.modèleCompétenceChapitre.append([ch])
        self.builder.get_object("sélecteurCompétenceChapitre").set_active(0)
        for cp in data_competence:
            self.modèleCompétence.append(cp)

    def créerNouveauTypeCompétence(self,dummy):
        """
        Callback utilisé pour la création d'un nouveau type de compétence
        """
        liste = self.créationNouvelObjet("Entrez le nom du nouveau type de compétence", [("Nom","libre_str")])
        if liste is not None:
            if liste in [ a[:] for a in self.modèleCompétenceType ]:
                FenêtresInformation.affichageErreur(self.fenêtrePrincipale,"Ce type de compétence existe déjà")
            else:
                self.modèleCompétenceType.append(liste)
                self.bdd.ajoutCompétenceType(liste[0])

    def supprimerTypeCompétence(self,dummy):
        """
        Callback utilisé pour la suppression d'un type de compétence
        """
        typeSupprimé = self.suppressionObjetSimple("Choisissez type de compétence à supprimer.",\
                                                       self.modèleCompétenceType,\
                                                       "Êtes-vous sûr de vouloir supprimer la catégorie {} " \
                                                       "ainsi que toutes les compétences associées ?")
        if typeSupprimé is not None:
            self.suppressionÉlémentsAssociésÀCatégorie(typeSupprimé, self.modèleCompétence, 1)
            [ self.bdd.retraitCompétence(elt['nom']) for elt in self.bdd.récupèreCompétencesComplet() \
              if elt['type'] == typeSupprimé ]
            self.bdd.retraitCompétenceType(typeSupprimé)

    def créerNouveauChapitre(self,dummy):
        """
        Callback utilisé pour la création d'un nouveau type de compétence
        """
        liste = self.créationNouvelObjet("Entrez le nom du nouveau chapitre.", [("Nom","libre_str")])
        if liste is not None:
            if liste in [ a[:] for a in self.modèleCompétenceChapitre ]:
                FenêtresInformation.affichageErreur(self.fenêtrePrincipale,"Ce chapitre existe déjà")
            else:
                self.modèleCompétenceChapitre.append(liste)
                self.bdd.ajoutCompétenceChapitre(liste[0])

    def supprimerChapitre(self,dummy):
        """
        Callback utilisé pour la suppression d'un chapitre
        """
        chapSupprimé = self.suppressionObjetSimple("Entrez le nom du chapitre à supprimer.",\
                                                       self.modèleCompétenceChapitre,\
                                                       "Êtes-vous sûr de vouloir supprimer le chapitre {} " \
                                                       "ainsi que toutes les compétences associées ?")
        if chapSupprimé is not None:
            self.suppressionÉlémentsAssociésÀCatégorie(chapSupprimé, self.modèleCompétence, 2)
            [ self.bdd.retraitCompétence(elt['nom']) for elt in self.bdd.récupèreCompétencesComplet() \
              if elt['chapitre'] == chapSupprimé ]
            self.bdd.retraitCompétenceChapitre(chapSupprimé)

    def créerCompétence(self,dummy):
        """
        Callback pour la création de compétence
        """
        filtreType = self.modèleCompétenceType.filter_new()
        filtreType.set_visible_func(self.filtreModifiables)
        filtreChap = self.modèleCompétenceChapitre.filter_new()
        filtreChap.set_visible_func(self.filtreModifiables)
        demandes = [("Nom","libre_str"), ("Catégorie",(filtreType,0)), ("Chapitre",(filtreChap,0))]
        liste = self.créationNouvelObjet("Créez une nouvelle compétence", demandes)
        if liste is not None:
            if liste in [ a[:] for a in self.modèleCompétence ]:
                FenêtresInformation.affichageErreur(self.fenêtrePrincipale,"Cette compétence existe déjà")
            else:
                self.modèleCompétence.append(liste)
                self.bdd.ajoutCompétence(liste[0],liste[2],liste[1])

    def supprimerCompétence(self,dummy):
        """
        Callback pour la suppression d'une compétence.
        """
        msgFunc = lambda a: "Voulez-vous supprimer la compétence {} ?".format(a[0])
        dbFonction = lambda mod,it: self.bdd.retraitCompétence(mod[it][0])
        self.suppressionDepuisAfficheurListe("afficheurCompétences", msgFunc, \
                                             "Aucune compétence n'est sélectionnée.", dbFonction)

    def filtreVisibilitéCompétences(self,model,it,data):
        """
        Fonction pour rendre visible uniquement les compétences d'un chapitre / une catégorie.
        """
        typeActif = self.modèleCompétenceType[self.builder.get_object("sélecteurCompétenceType").get_active()][0]
        chapitreActif = \
          self.modèleCompétenceChapitre[self.builder.get_object("sélecteurCompétenceChapitre").get_active()][0]
        return( (typeActif == "Toutes" or typeActif == model[it][1]) and \
          (chapitreActif == "Tous" or chapitreActif == model[it][2]))

    # Constructeur
    def __init__(self):
        """
        Constructeur
        """
        # Chargement du glade
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.gladefile = dir_path + "/interface.glade"
        self.dbfile = dir_path + "/dbManagement/competences.db"
        self.bdd = BaseDeDonnées(self.dbfile)
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        # Récupération des objets utiles
        self.fenêtrePrincipale = self.builder.get_object("fenêtrePrincipale")
        # Création des objets de l'état : les classes, les étudiants
        self.classeActive = "Toutes"
        self.devoirs = []
        # Création des modèles de données pour les affichages
        self.modèleClasses = self.builder.get_object("modèleClasses")
        self.modèleÉtudiants = self.builder.get_object("modèleÉtudiants")
        self.modèleCompétenceType = self.builder.get_object("modèleCompétenceType")
        self.modèleCompétenceChapitre = self.builder.get_object("modèleCompétenceChapitre")
        self.modèleCompétence = self.builder.get_object("modèleCompétence")
        self.modèleDevoirType = self.builder.get_object("modèleDevoirType")
        self.modèleDevoir = self.builder.get_object("modèleDevoir")
        # Mise en place des vues filtrées
        self.builder.get_object("modèleÉtudiantsFiltré").set_visible_func(self.filtreVisibilitéParClasse)
        self.builder.get_object("modèleDevoirFiltré").set_visible_func(self.filtreVisibilitéDevoirs)
        self.builder.get_object("modèleCompétenceFiltré").set_visible_func(self.filtreVisibilitéCompétences)
        # Chargement des données
        self.chargerInfosDepuisBDD()
        # lancement
        self.builder.connect_signals(self)
        self.fenêtrePrincipale.show()


## Tests
if __name__ == '__main__':
    f = FenêtrePrincipale()
    Gtk.main()
