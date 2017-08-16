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

    def affichageErreur(self,texte):
        """
        Une fonction utilisée pour afficher les messages d'erreur.
        """
        dialogueErreur = Gtk.MessageDialog(self.fenêtrePrincipale, 0, Gtk.MessageType.ERROR, \
                    Gtk.ButtonsType.CANCEL, "Une erreur s'est produite")
        dialogueErreur.format_secondary_text(texte)
        dialogueErreur.run()
        dialogueErreur.destroy()

    def demandeConfirmation(self,texte):
        """
        Une fonction utilisée pour demander une confirmation.
        Renvoie True ou False.
        """
        dialogueConf = Gtk.MessageDialog(self.fenêtrePrincipale, 0, Gtk.MessageType.QUESTION, \
                    Gtk.ButtonsType.OK_CANCEL, "Confirmation")
        dialogueConf.format_secondary_text(texte)
        réponse = (dialogueConf.run() == Gtk.ResponseType.OK)
        dialogueConf.destroy()
        return(réponse)

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
        # Lancement de la boite de dialogue
        dialogue = self.builder.get_object("dialogueCréationClasse")
        nomClasseEntrée = self.builder.get_object("saisieNouvelleClasse")
        # Utilisation de Entrée pour valider
        nomClasseEntrée.set_activates_default(True)
        boutonOk = dialogue.get_widget_for_response(response_id=Gtk.ResponseType.OK)
        boutonOk.set_can_default(True)
        boutonOk.grab_default()
        # Lancement de la boite de dialogue
        dialogue.show()
        réponse = dialogue.run()
        nomClasse = nomClasseEntrée.get_text()
        if réponse == Gtk.ResponseType.OK:
            if nomClasse in [ a[0] for a in self.modèleClasses ]:
                self.affichageErreur("Le nom de classe que vous avez entré est déjà pris.")
            else:
                self.modèleClasses.append([nomClasse])
        dialogue.hide()

    def supprimerClasse(self,dummy):
        """
        Callback utilisé pour la suppression d'une classe.
        """
        # Lancement de la boite de dialogue
        dialogue = self.builder.get_object("dialogueSuppressionClasse")
        dialogue.show()
        réponse = dialogue.run()
        if réponse == Gtk.ResponseType.OK:
            iterClasse = self.builder.get_object("sélectionneurClasseÀSupprimer").get_active_iter()
            nomClasse = self.builder.get_object("modèleClassesModifiables")[iterClasse][0]
            if self.demandeConfirmation("Êtes-vous sûr de vouloir supprimer la classe {} " \
                                         "ainsi que tous les étudiants qui la composent ?".format(nomClasse)):
                it = self.builder.get_object("modèleClassesModifiables").convert_iter_to_child_iter(iterClasse)
                self.modèleClasses.remove(it)
                it = self.modèleÉtudiants.get_iter_first()
                while it is not None and self.modèleÉtudiants.iter_is_valid(it):
                    if self.modèleÉtudiants[it][0] == nomClasse:
                        self.modèleÉtudiants.remove(it)
                    else:
                        it = self.modèleÉtudiants.iter_next(it)
        dialogue.hide()

    def ajouterÉtudiant(self,dummy):
        """
        Callback utilisé pour la suppression d'un étudiant.
        """
        # Lancement de la boite de dialogue
        dialogue = self.builder.get_object("dialogueCréationÉtudiant")
        nomÉtudiantEntrée = self.builder.get_object("saisieNomNouvelÉtudiant")
        prénomÉtudiantEntrée = self.builder.get_object("saisiePrénomNouvelÉtudiant")
        # Utilisation de Entrée pour valider
        nomÉtudiantEntrée.set_activates_default(True)
        prénomÉtudiantEntrée.set_activates_default(True)
        boutonOk = dialogue.get_widget_for_response(response_id=Gtk.ResponseType.OK)
        boutonOk.set_can_default(True)
        boutonOk.grab_default()
        # Lancement de la boite de dialogue
        dialogue.show()
        réponse = dialogue.run()
        nomÉtudiant = nomÉtudiantEntrée.get_text()
        prénomÉtudiant = prénomÉtudiantEntrée.get_text()
        iterClasse = self.builder.get_object("sélectionneurClasseNouvelÉtudiant").get_active_iter()
        nomClasse = self.builder.get_object("modèleClassesModifiables")[iterClasse][0]
        if réponse == Gtk.ResponseType.OK:
            if (nomClasse,nomÉtudiant,prénomÉtudiant) in [ tuple(a) for a in self.modèleÉtudiants ]:
                self.affichageErreur("L'étudiant proposé existe déjà.")
            else:
                self.modèleÉtudiants.append([nomClasse,nomÉtudiant,prénomÉtudiant])
        dialogue.hide()

    def supprimerÉtudiant(self,dummy):
        """
        Callback utilisé pour la suppression d'un étudiant.
        """
        modèle, itÉtudiant = self.builder.get_object("afficheurÉtudiants").get_selection().get_selected()
        if itÉtudiant is None:
            self.affichageErreur("Vous n'avez pas sélectionné d'étudiant")
        else:
            nom,prénom = modèle[itÉtudiant][1],modèle[itÉtudiant][2]
            if self.demandeConfirmation("Voulez-vous supprimer l'étudiant {} {} ?".format(nom,prénom)):
                iterInterm = modèle.convert_iter_to_child_iter(itÉtudiant)
                iterFinal = self.builder.get_object("modèleÉtudiantsFiltré").convert_iter_to_child_iter(iterInterm)
                self.modèleÉtudiants.remove(iterFinal)

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

    def filtreModifiables(self,model,it,data):
        """
        Fonction pour rendre visible uniquement les entités modifiables ou supprimables.
        Est utilisé dans le cas de modèles contenant l'entrée "Tous" pour l'exclure.
        """
        if model[it][0] in ["Toutes","Tous"]:
            return(False)
        return(True)

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
        self.builder.get_object("modèleClassesModifiables").set_visible_func(self.filtreModifiables)
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
