#!/usr/bin/python3

"""
Module gérant l'interface graphique.
"""


## Temporaire : données hardcodées pour la phase de mise en place / tests
# La mise en place de ces schémas est la même que pour la BDD
data_classes = [[0,"Toutes"],  # id,nom
                    [1,"MPSI"],
                    [2,"MP"],
                    [3,"PSI"]]
data_étudiants = [[1,1,"Alp","Selin"],  # id, idClasse, nom, prénom
                      [2,1,"Bazin","Jérémy"],
                      [3,1,"Gourgues","Maxime"],
                      [4,1,"Morceaux","Jérémy"],
                      [5,1,"Dias","Léo"],
                      [6,2,"Chevasson","Raphaël"],
                      [7,2,"Clémenceau","Sandra"],
                      [8,2,"Hubert","Olive"],
                      [9,2,"Bornet","Clément"],
                      [10,3,"Grither","Noëmie"],
                      [11,3,"Berdery","Mathieu"],
                      [12,3,"Milhem","William"]]

## imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


## Classe de la fenêtre principale

class FenêtrePrincipale(object):
    """
    Classe gérant la fenêtre de l'application.
    """
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

    def chargerClasses(self):
        """
        Fonction qui charge les classes dans les ListStore adaptés.
        Implémentation temporaire.
        """
        # Peuplement à la main ; à modifier
        for cl in data_classes:
            self.modèleClasses.append(cl)
        self.builder.get_object("sélecteurClasse").set_active(0)
        data_étudiants.sort(key=lambda elt: elt[2])
        for et in data_étudiants:
            self.modèleÉtudiants.append(et)

    def créerNouvelleClasse(self,dummy):
        """
        Callback utilisé pour la création d'une nouvelle classe.
        """
        # Construction de la boite de dialogue
        # Lancement de la boite de dialogue
        dialogue = self.builder.get_object("dialogueCréationClasse")
        nomClasseEntrée = self.builder.get_object("dialogueCréationClasseEntréeTexte")
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
            if nomClasse in [ a[1] for a in self.modèleClasses ]:
                self.affichageErreur("Le nom de classe que vous avez entré est déjà pris.")
            else:
                nouveauId = max([ a[0] for a in self.modèleClasses ]) + 1
                self.modèleClasses.append([nouveauId,nomClasse])
        dialogue.hide()

    def supprimerClasse(self,dummy):
        """
        Callback utilisé pour la suppression d'une classe.
        """
        # Lancement de la boite de dialogue
        dialogue = self.builder.get_object("dialogueSuppressionClasse")
        dialogue.show()
        réponse = dialogue.run()
        iterClasse = self.builder.get_object("sélectionneurClasseÀSupprimer").get_active_iter()
        if réponse == Gtk.ResponseType.OK:
            self.modèleClasses.remove(iterClasse)
        dialogue.hide()

    def changerClasseActive(self,sélecteur:Gtk.ComboBox):
        """
        Callback pour le changement de classe active.
        """
        idClasse, classe = self.modèleClasses[sélecteur.get_active()]
        self.classeActive = idClasse
        self.builder.get_object("modèleÉtudiantsFiltré").refilter()

    def filtreVisibilitéParClasse(self,model,it,data):
        """
        Fonction pour rendre visible uniquement les étudiants de la classe active
        """
        if self.modèleClasses[self.classeActive][1] in ["Toutes","Tous"]:
            return(True)
        return(model[it][1] == self.classeActive)

    def filtreModifiables(self,model,it,data):
        """
        Fonction pour rendre visible uniquement les entités modifiables ou supprimables. 
        Est utilisé dans le cas de modèles contenant l'entrée "Tous" pour l'exclure.
        """
        if model[it][1] in ["Toutes","Tous"]:
            return(False)
        return(True)

    def __init__(self):
        """
        Constructeur
        """
        # Chargmenet du glade
        # Chargement du glade
        self.gladefile = 'interface.glade'
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        # Récupération des objets utiles
        self.fenêtrePrincipale = self.builder.get_object("fenêtrePrincipale")
        # Création des objets de l'état : les classes, les étudiants
        self.classeActive = 0
        self.modèleClasses = self.builder.get_object("modèleClasses")
        self.modèleÉtudiants = self.builder.get_object("modèleÉtudiants")
        # Mise en place de la vue des étudiants
        self.builder.get_object("modèleÉtudiantsFiltré").set_visible_func(self.filtreVisibilitéParClasse)
        self.builder.get_object("modèleÉtudiantsClassé").set_sort_column_id(2,Gtk.SortType.ASCENDING)
        # Mise en place des exclusions de listes
        self.builder.get_object("modèleClassesModifiables").set_visible_func(self.filtreModifiables)
        # Chargement des données
        self.chargerClasses()
        # lancement
        self.fenêtrePrincipale.show()


## Classe de la fenêtre popup test


## Tests
if __name__ == '__main__':
    f = FenêtrePrincipale()

Gtk.main()
