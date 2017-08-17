#!/usr/bin/python3

"""
Module gérant l'interface graphique.
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
                       ["Propoager une incertitude","Technique","Généralités"],
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

## imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

## Classe regroupant des créations de fenêtres sans intéraction
class FenêtresInformation(object):
    """
    Classe regroupant des créations de fenêtres sans intéraction avec l'utilisateur
    """
    def affichageErreur(parent,texte:str) -> None:
        """
        Une fonction utilisée pour afficher les messages d'erreur.
        """
        dialogueErreur = Gtk.MessageDialog(parent, 0, Gtk.MessageType.ERROR, \
                    Gtk.ButtonsType.CANCEL, "Une erreur s'est produite")
        dialogueErreur.format_secondary_text(texte)
        dialogueErreur.run()
        dialogueErreur.destroy()

    def demandeConfirmation(parent,texte:str) -> None:
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
    def __init__(self, parent:Gtk.Window, label:str, demandes:list):
        """
        Constructeur.

        Permet de créer la fenêtre qui aura les demandes fournies.
        La liste demandes contient des paires (label, choix). Si choix est la str "libre", alors une entrée
        clavier est demandée ; si choix est une paire (ListStore,int), alors on demande à l'utilisateur de
        choisir parmi les entrées du ListStore, colonne int.
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
        for txt,dem in demandes:
            self.grille.attach(Gtk.Label(txt),0,ligne,1,1)
            if type(dem) == str and dem == "libre":
                saisie = Gtk.Entry()
                saisie.set_hexpand(True)
                saisie.set_activates_default(True)
                self.grille.attach(saisie,1,ligne,1,1)
            elif type(dem) == tuple:
                comboBox = Gtk.ComboBox.new_with_model(dem[0])
                comboBox.set_hexpand(True)
                renderer = Gtk.CellRendererText()
                comboBox.pack_start(renderer, True)
                comboBox.add_attribute(renderer, "text", dem[1])
                self.grille.attach(comboBox,1,ligne,1,1)
            else:
                FenêtresInformation.affichageErreur(self, \
                                                    "Demande non gérée dans le constructeur de FenetreDemande ; " \
                                                    "le type proposé est {}".format(type(dem)))
            ligne += 1
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
        for i,(txt,dem) in enumerate(self.demandes):
            if type(dem) == str and dem == "libre":
                retours.append(self.grille.get_child_at(1,i).get_text())
            elif type(dem) == tuple:
                comboBox = self.grille.get_child_at(1,i)
                retours.append(dem[0][comboBox.get_active()][dem[1]])
        return(retours)


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
        dialogue = FenetreDemande(self.fenêtrePrincipale, \
                                  texte, \
                                  [("Choix",(filtre,col))])
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

    def suppressionDepuisAfficheurListe(self, afficheur:str, texteConfirmation:'function', msgErr:str) -> None:
        """
        Fonction générique utilisée pour supprimer depuis une liste ordonnable et triable.

        - L'afficheur est identifié par son identifiant glade
        - texteConfirmation est une fonction à un paramètre qui construit la chaîne de caractère à partir
          de la ligne récupérée
        - msgErr est utilisée en cas d'absence de sélection de la part de l'utilisateur
        """
        modèleSup, it = self.builder.get_object(afficheur).get_selection().get_selected()
        if it is None:
            FenêtresInformation.affichageErreur(self.fenêtrePrincipale,msgErr)
        else:
            msg = texteConfirmation(modèleSup[it])
            if FenêtresInformation.demandeConfirmation(self.fenêtrePrincipale,msg):
                iterInterm = modèleSup.convert_iter_to_child_iter(it)
                modèleInter = modèleSup.get_model()
                iterFinal = modèleInter.convert_iter_to_child_iter(iterInterm)
                modèleInter.get_model().remove(iterFinal)

    def créationNouvelObjet(self, label:str, demandes:list, modèle:Gtk.ListStore) -> None:
        """
        Fonction générique utilisée pour la création d'un nouvel objet.

        La liste demandes contient des paires (label, choix). Si choix est la str "libre", alors une entrée
        clavier est demandée ; si choix est une paire (ListStore,int), alors on demande à l'utilisateur de
        choisir parmi les entrées du ListStore, colonne int.

        modèle est le modèle auquel on ajoutera l'élément créé ; les champs demandés doivent donc être
        dans l'ordre du modèle sous-jacent.
        """
        # Préparation de la fenêtre
        dialogue = FenetreDemande(self.fenêtrePrincipale, label, demandes)
        réponse = dialogue.run()
        if réponse == Gtk.ResponseType.OK:
            liste = dialogue.récupèreInfos()
            if "" in liste:
                FenêtresInformation.affichageErreur(dialogue,"Vous devez remplir tous les champs")
            elif liste in [a[:] for a in modèle]:
                FenêtresInformation.affichageErreur(dialogue,"Cet élément existe déjà")
            else:
                modèle.append(liste)
        dialogue.destroy()

    # Fonctions liées à la gestion des classes / étudiants
    def chargerClasses(self):
        """
        Fonction qui charge les compétences dans les ListStore adaptés.
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
        self.créationNouvelObjet("Entrez le nom de la nouvelle classe",\
                                 [("Nom","libre")], \
                                 self.modèleClasses)

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

    def ajouterÉtudiant(self,dummy):
        """
        Callback utilisé pour la suppression d'un étudiant.
        """
        filtre = self.modèleClasses.filter_new()
        filtre.set_visible_func(self.filtreModifiables)
        self.créationNouvelObjet("Entrez le nouvel étudiant",\
                                 [("Classe",(filtre,0)),("Nom","libre"),("Prénom","libre")], \
                                 self.modèleÉtudiants)

    def supprimerÉtudiant(self,dummy):
        """
        Callback utilisé pour la suppression d'un étudiant.
        """
        constructionMsg = lambda a: "Voulez-vous supprimer l'étudiant {} {} ?".format(a[1],a[2])
        self.suppressionDepuisAfficheurListe("afficheurÉtudiants", constructionMsg, \
                                             "Vous n'avez pas sélectionné d'étudiant")

    def changerClasseActive(self,sélecteur:Gtk.ComboBox):
        """
        Callback pour le changement de classe active.
        """
        nomClasse = self.modèleClasses[sélecteur.get_active()][0]
        self.classeActive = nomClasse
        self.builder.get_object("modèleÉtudiantsFiltré").refilter()

    def filtreVisibilitéParClasse(self,model,it,data):
        """
        Fonction pour rendre visible uniquement les étudiants de la classe active
        """
        if self.classeActive in ["Toutes","Tous"]:
            return(True)
        return(model[it][0] == self.classeActive)

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
        self.créationNouvelObjet("Entrez le nom du nouveau type de compétence.", \
                                    [("Nom","libre")], \
                                     self.modèleCompétenceType)

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

    def créerNouveauChapitre(self,dummy):
        """
        Callback utilisé pour la création d'un nouveau type de compétence
        """
        self.créationNouvelObjet("Entrez le nom du nouveau chapitre.", \
                                 [("Nom","libre")], \
                                 self.modèleCompétenceChapitre)

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

    def créerCompétence(self,dummy):
        """
        Callback pour la création de compétence
        """
        filtreType = self.modèleCompétenceType.filter_new()
        filtreType.set_visible_func(self.filtreModifiables)
        filtreChap = self.modèleCompétenceChapitre.filter_new()
        filtreChap.set_visible_func(self.filtreModifiables)
        self.créationNouvelObjet("Créez une nouvelle compétence", \
                                 [("Nom","libre"), \
                                  ("Catégorie",(filtreType,0)), \
                                  ("Chapitre",(filtreChap,0))], \
                                 self.modèleCompétence)

    def supprimerCompétence(self,dummy):
        """
        Callback pour la suppression d'une compétence.
        """
        msgFunc = lambda a: "Voulez-vous supprimer la compétence {} ?".format(a[0])
        self.suppressionDepuisAfficheurListe("afficheurCompétences", msgFunc, \
                                             "Aucune compétence n'est sélectionnée.")

    def changerFiltresCompétences(self,sélecteur:Gtk.ComboBox):
        """
        Callback pour les sélecteurs de type / chapitre de compétences.
        """
        self.builder.get_object("modèleCompétenceFiltré").refilter()

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
        self.gladefile = 'interface.glade'
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        # Récupération des objets utiles
        self.fenêtrePrincipale = self.builder.get_object("fenêtrePrincipale")
        # Création des objets de l'état : les classes, les étudiants
        self.classeActive = "Toutes"
        self.modèleClasses = self.builder.get_object("modèleClasses")
        self.modèleÉtudiants = self.builder.get_object("modèleÉtudiants")
        self.modèleCompétenceType = self.builder.get_object("modèleCompétenceType")
        self.modèleCompétenceChapitre = self.builder.get_object("modèleCompétenceChapitre")
        self.modèleCompétence = self.builder.get_object("modèleCompétence")
        # Mise en place de la vue des étudiants
        self.builder.get_object("modèleÉtudiantsFiltré").set_visible_func(self.filtreVisibilitéParClasse)
        # Mise en place des exclusions de listes
        self.builder.get_object("modèleCompétenceFiltré").set_visible_func(self.filtreVisibilitéCompétences)
        # Chargement des données
        self.chargerClasses()
        self.chargerCompétences()
        # lancement
        self.fenêtrePrincipale.show()


## Tests
if __name__ == '__main__':
    f = FenêtrePrincipale()

Gtk.main()
