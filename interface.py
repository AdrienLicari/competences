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
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from traitements.traitements import *


## Fonction pour les autocomplétions
def match_anywhere(completion, entrystr, iter, data):
    """
    Fonction permettant à une autocomplétion de se faire avec
    un sous-ensemble quelconque de la chaîne.
    Taken from https://stackoverflow.com/questions/2250477/entry-with-suggestions
    """
    idCol = completion.props.text_column
    modelstr = completion.get_model()[iter][idCol].lower()
    entrystr = completion.get_entry().get_text().lower()
    return(entrystr in modelstr)


## CellRendererText avec autocomplétion
class CellRendererAutoComplete(Gtk.CellRendererText):
    """
    Text entry cell which accepts a Gtk.EntryCompletion object
    Taken from https://stackoverflow.com/questions/13756787/gtk-entry-in-gtk-treeview-cellrenderer
    """
    __gtype_name__ = 'CellRendererAutoComplete'
    def __init__(self, completion):
        self.completion = completion
        Gtk.CellRendererText.__init__(self)
    def do_start_editing(
               self, event, treeview, path, background_area, cell_area, flags):
        if not self.get_property('editable'):
            return
        entry = Gtk.Entry()
        entry.set_completion(self.completion)
        entry.connect('editing-done', self.editing_done, path)
        entry.show()
        entry.grab_focus()
        return entry
    def editing_done(self, entry, path):
        self.emit('edited', path, entry.get_text())


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
    def __init__(self, parent:Gtk.Window, label:str, demandes:list):
        """
        Constructeur.

        Permet de créer la fenêtre qui aura les demandes fournies.

        La liste demandes contient des paires (label, choix). Les possibilités sont les suivantes :
        - si choix est la str "libre", alors une entrée clavier est demandée ;
        - si choix est une paire (ListStore,int), alors on demande à l'utilisateur de choisir parmi
          les entrées du ListStore, colonne int.
        - si choix est la str "date" alors un calendrier est inséré et une date est demandée
        - si choix est la str "fichier", alors un bouton donnant accès à un sélecteur de fichiers est inséré
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
        for txt,dem in demandes:
            self.grille.attach(Gtk.Label(txt),0,ligne,1,1)
            if type(dem) == str and dem == "libre":
                saisie = Gtk.Entry()
                saisie.set_hexpand(True)
                saisie.set_activates_default(True)
                self.grille.attach(saisie,1,ligne,1,1)
            elif type(dem) == str and dem == "date":
                cal = Gtk.Calendar()
                cal.set_hexpand(True)
                self.grille.attach(cal,1,ligne,1,1)
            elif type(dem) == str and dem == "fichier":
                bouton = Gtk.Button("Choisir fichier")
                bouton.connect("clicked", self.sousFenêtreFichier)
                self.grille.attach(bouton,1,ligne,1,1)
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
        i = 0
        for txt,dem in self.demandes:
            if type(dem) == str and dem == "libre":
                retours.append(self.grille.get_child_at(1,i).get_text())
            elif type(dem) == str and dem == "date":
                date = self.grille.get_child_at(1,i).get_date()
                date_str = "{:02d}.{:02d}.{:4d}".format(date[2],date[1],date[0])
                retours.append(date_str)
                i -= 1
            elif type(dem) == str and dem == "fichier":
                retours.append(self.fichiers[0])
                self.fichiers.pop(0)
            elif type(dem) == tuple:
                comboBox = self.grille.get_child_at(1,i)
                retours.append(dem[0][comboBox.get_active()][dem[1]])
            i += 1
        return(retours)

    def sousFenêtreFichier(self, bouton:Gtk.Button):
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
            self.fichiers.append(dialogue.get_filename())
        dialogue.destroy()
        nomFichier = self.fichiers[-1].split("/")[-1]
        bouton.set_label(nomFichier)


## Classe pour la création des questions d'un devoir
class FenetreQuestionsDevoir():
    """
    Classe gérant la construction d'une fenêtre popup pour la définition des questions /
        compétences associées à un devoir.

    Doit reçevoir un objet Devoir en paramètre.

    Ne gère pas l'attachement de plus de 10 compétences à chaque question.
    """
    def __init__(self, devoir:Devoir, builder:Gtk.Builder):
        """
        Constructeur de la fenêtre.

        Utilise le patron disponible dans le .glade, donné par le Gtk.Builder, puis modifie
        les lignes en fonction des besoins du devoir considéré.
        """
        self.maxCompétenceParQuestion = 10
        self.devoir_save = devoir
        self.fenêtre = builder.get_object("fenêtreQuestionsDevoir")
        self.treeview = builder.get_object("fenêtreQuestionsDevoirAfficheur")
        titre_str = "Mise en place des questions du devoir {} {} de la classe {} - {}".\
                    format(devoir.typ,devoir.num,devoir.classe,devoir.date)
        self.fenêtre.set_title(titre_str)
        builder.get_object("fenêtreQuestionsDevoirAppliquer").connect("clicked",self.sauvegarderCompétences)
        # Mise en place du modèle - doit être cohérent avec self.maxCompétenceParQuestion
        self.modèle = Gtk.ListStore(str, \
                                    str,int,str,int,str,int,str,int,str,int,str,int,str,int,str,int,str,int,str,int)
        self.màjModèle()
        self.modèleCompétence = builder.get_object("modèleCompétence")
        # Mise en place de vue
        self.vue = builder.get_object("fenêtreQuestionsDevoirAfficheur")
        while self.vue.get_n_columns() > 0:
            self.vue.remove_column(self.vue.get_column(0))
        self.vue.set_model(self.modèle)
        rdNuméro = Gtk.CellRendererText()
        rdNuméro.set_property("editable",True)
        rdNuméro.connect("edited", self.celluleÉditée, 0)
        self.vue.append_column(Gtk.TreeViewColumn("N°",rdNuméro,text=0))
        for i in range(self.maxCompétenceParQuestion):
            col = Gtk.TreeViewColumn("Compétence {}".format(i+1))
            completion = Gtk.EntryCompletion()
            rdComp = CellRendererAutoComplete(completion)
            rdCoef = Gtk.CellRendererText()
            completion.set_model(self.modèleCompétence)
            completion.pack_start(rdComp, True)
            completion.add_attribute(rdComp, "text", 0)
            completion.props.text_column = 0
            completion.set_match_func(match_anywhere, None)
            rdComp.set_property("editable",True)
            rdCoef.set_property("editable",True)
            rdComp.connect("edited", self.celluleÉditée, 2*i+1)
            rdCoef.connect("edited", self.celluleÉditée, 2*i+2)
            col.pack_start(rdComp,True)
            col.pack_start(rdCoef,False)
            col.add_attribute(rdComp, "text", 2*i+1)
            col.add_attribute(rdCoef, "text", 2*i+2)
            self.vue.append_column(col)
        self.vue.append_column(Gtk.TreeViewColumn("",Gtk.CellRendererText()))
        self.vue.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.gestionAffichage()
        # Lancement
        self.fenêtre.show_all()
        réponse = self.fenêtre.run()
        self.fenêtre.hide()

    def ajouterLigne(self) -> None:
        """
        Fonction interne pour ajouter une ligne vide au modèle, servant à créer une nouvelle question.
        """
        nom = ""
        cp_coeff = ["",0]*self.maxCompétenceParQuestion
        self.modèle.append([nom]+cp_coeff)

    def màjModèle(self) -> None:
        """
        Fonction interne pour ajouter une ligne à la grille interne.

        Si question est un tuple (nom_question,[(nom_compétence,coef)]), elle est ajoutée.
        Si question est None, une ligne vide est ajoutée.
        """
        self.modèle.clear()
        for q in self.devoir_save.get_listeQuestionsModèle(self.maxCompétenceParQuestion):
            self.modèle.append(q)
        self.ajouterLigne()

    def celluleÉditée(self, cellule, path, text, num):
        """
        Callback pour la mise à jour du modèle quand une case est éditée.
        """
        if num%2 == 0 and num > 0:
            text = int(text)
        self.modèle[path][num] = text
        if int(path) == len(self.modèle)-1:  # gestion de l'ajout de nouvelle ligne
            self.ajouterLigne()
        self.gestionAffichage()

    def gestionAffichage(self):
        """
        Fonction ayant pour rôle de définir les colonnes visibles ou non.
        """
        listeCompétences = [ [k for k in a[1:] if type(k) == str and k != ""] for a in self.modèle ]
        nbCols = max([ len(a) for a in listeCompétences ]) + 2
        for i in range(1,nbCols):
            self.vue.get_column(i).set_visible(True)
        for i in range(nbCols,self.maxCompétenceParQuestion+1):
            self.vue.get_column(i).set_visible(False)

    def sauvegarderCompétences(self,dummy):
        """
        Callback utilisé pour mettre à jour l'objet Devoir sous-jacent à partir du modèle.
        """
        listeModèle = [ ligne[:] for ligne in self.modèle]
        listeCompétences = [ ligne[0] for ligne in self.modèleCompétence ]
        self.devoir_save.set_questionsDepuisModèle(listeModèle, listeCompétences)
        self.màjModèle()


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

    def suppressionDepuisAfficheurListe(self, afficheur:str, texteConfirmation:'function', msgErr:str) -> None:
        """
        Fonction générique utilisée pour supprimer depuis une liste ordonnable et triable.

        - L'afficheur est identifié par son identifiant glade
        - texteConfirmation est une fonction à un paramètre qui construit la chaîne de caractère à partir
          de la ligne récupérée
        - msgErr est utilisée en cas d'absence de sélection de la part de l'utilisateur
        """
        modèle, it = self.sélectionDepuisAfficheurListe(afficheur, msgErr)
        if it is not None:
            msg = texteConfirmation(modèle[it])
            if FenêtresInformation.demandeConfirmation(self.fenêtrePrincipale,msg):
                modèle.remove(it)

    def créationNouvelObjet(self, label:str, demandes:list, modèle:Gtk.ListStore) -> list:
        """
        Fonction générique utilisée pour la création d'un nouvel objet.

        La liste demandes contient des paires (label, choix). Les possibilités sont documentées dans la
        docstring de FenetreDemande.__init__

        Les champs demandés doivent l'être dans l'ordre du modèle sous-jacent. modèle est le modèle à peupler.

        Si modèle contient des int, la conversion peut lever une ValueError. Elle doit être gérée par l'appelant.

        Renvoie la liste correspondant aux données ajoutées dans le modèle si l'ajout est réussi, None sinon.
        """
        # Préparation de la fenêtre
        dialogue = FenetreDemande(self.fenêtrePrincipale, label, demandes)
        réponse = dialogue.run()
        liste = dialogue.récupèreInfos()
        dialogue.destroy()
        if réponse == Gtk.ResponseType.OK:
            for i in range(len(liste)):
                if type(modèle[0][i]) == int:
                    try:
                        liste[i] = int(liste[i])
                    except(ValueError):
                        FenêtresInformation.affichageErreur(self.fenêtrePrincipale, \
                                                            "Un champ de type entier a été mal entré.")
            if "" in liste:
                FenêtresInformation.affichageErreur(dialogue,"Vous devez remplir tous les champs")
            elif liste in [a[:] for a in modèle]:
                FenêtresInformation.affichageErreur(dialogue,"Cet élément existe déjà")
            else:
                modèle.append(liste)
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
        Callback utilisé pour la création d'un étudiant.
        """
        filtre = self.modèleClasses.filter_new()
        filtre.set_visible_func(self.filtreModifiables)
        self.créationNouvelObjet("Entrez le nouvel étudiant",\
                                 [("Classe",(filtre,0)),("Nom","libre"),("Prénom","libre")], \
                                 self.modèleÉtudiants)

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
        dialogue = FenetreDemande(self.fenêtrePrincipale, "Ajouter une liste d'étudiants", \
                                  [("Classe",(filtre,0)),(explication,"fichier")])
        réponse = dialogue.run()
        classe, nomFichier = dialogue.récupèreInfos()
        dialogue.destroy()
        # Lecture du fichier
        séparateur = ";"
        fichier = open(nomFichier,'r')
        for ligne in fichier:
            nom,prénom = ligne.split(séparateur)
            self.modèleÉtudiants.append([classe,nom,prénom[:-1]])  # on exclut le '\n' de fin de ligne
        fichier.close()

    def supprimerÉtudiant(self,dummy):
        """
        Callback utilisé pour la suppression d'un étudiant.
        """
        constructionMsg = lambda a: "Voulez-vous supprimer l'étudiant {} {} ?".format(a[1],a[2])
        self.suppressionDepuisAfficheurListe("afficheurÉtudiants", constructionMsg, \
                                             "Vous n'avez pas sélectionné d'étudiant")

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
            self.modèleDevoir.append(dv)
            self.devoirs.append(Devoir(dv[0],dv[1],dv[2],dv[3]))
        self.devoirs[0].test_créerQuestionsDevoir()

    def créerNouveauDevoirType(self,dummy):
        """
        Callback pour créer un nouveau type de devoir.
        """
        self.créationNouvelObjet("Créez un nouveau type de devoir", \
                                 [("Nom","libre")], \
                                 self.modèleDevoirType)

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

    def créerDevoir(self,dummy):
        """
        Callback pour créer un nouveau devoir.
        """
        filtreC = self.modèleClasses.filter_new()
        filtreT = self.modèleDevoirType.filter_new()
        filtreC.set_visible_func(self.filtreModifiables)
        filtreT.set_visible_func(self.filtreModifiables)
        demandes = [("Classe",(filtreC,0)), ("Type",(filtreT,0)), ("Numéro","libre"), ("Date","date")]
        dv = self.créationNouvelObjet("Créez un nouveau devoir", demandes, self.modèleDevoir)
        if dv is not None:
            self.devoirs.append(Devoir(dv[0],dv[1],dv[2],dv[3]))
        print(self.devoirs)

    def supprimerDevoir(self,dummy):
        """
        Callback utilisé pour la suppression d'un devoir.
        """
        constructionMsg = lambda a: "Voulez-vous supprimer le devoir {} {} des {} ?".format(a[1],a[2],a[0])
        self.suppressionDepuisAfficheurListe("afficheurDevoirs", constructionMsg, \
                                             "Vous n'avez pas sélectionné de devoir")

    def modifierQuestionsDevoir(self,dummy):
        """
        Callback utilisé pour la modification des questions dans un devoir.
        Délègue à la classe FenetreQuestionsDevoir.
        """
        modèle,it = self.sélectionDepuisAfficheurListe("afficheurDevoirs", \
                                                       "Vous n'avez pas sélectionné de devoir")
        if it is not None:
            dev = [d for d in self.devoirs if d.correspondÀ(modèle[it])][0]
            fenêtreQuestions = FenetreQuestionsDevoir(dev, self.builder)

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
        self.chargerClasses()
        self.chargerCompétences()
        self.chargerDevoirs()
        # lancement
        self.fenêtrePrincipale.show()


## Tests
if __name__ == '__main__':
    f = FenêtrePrincipale()

Gtk.main()
