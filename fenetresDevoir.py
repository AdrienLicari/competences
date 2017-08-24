#!/usr/bin/python3

"""
Module gérant l'interface graphique des fenêtres liées à la gestion des devoirs.
"""

## imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from autocompletion import *
from traitements.traitements import *
from dbManagement.dbManagement import BaseDeDonnées

## Classe pour la création des questions d'un devoir
class FenêtreQuestionsDevoir(object):
    """
    Classe gérant la construction d'une fenêtre popup pour la définition des questions /
    compétences associées à un devoir.

    Doit reçevoir un objet Devoir en paramètre.

    Ne gère pas l'attachement de plus de 10 compétences à chaque question.
    """
    maxCompétenceParQuestion = 10
    def __init__(self, devoir:Devoir, builder:Gtk.Builder, bdd:BaseDeDonnées, idDev:int):
        """
        Constructeur de la fenêtre.

        Utilise le patron disponible dans le .glade, donné par le Gtk.Builder, puis modifie
        les lignes en fonction des besoins du devoir considéré.
        """
        self.devoir_save = devoir
        self.fenêtre = builder.get_object("fenêtreQuestionsDevoir")
        self.vue = builder.get_object("fenêtreQuestionsDevoirAfficheur")
        self.vueModificateurs = builder.get_object("fenêtreQuestionsDevoirModificateurs")
        self.modèleModificateurs = builder.get_object("modèleModificateursDevoir")
        self.modèleCompétence = builder.get_object("modèleCompétence")
        self.saisieNoteMax = builder.get_object("fenêtreQuestionsDevoirSaisieNoteMax")
        self.saisieNvxComp = builder.get_object("fenêtreQuestionsDevoirSaisieNvxComp")
        self.fenêtre.set_title("Mise en place des questions du " + devoir.get_enTêteDevoir())
        builder.get_object("fenêtreQuestionsDevoirAppliquer").connect("clicked",self.sauvegarderCompétences)
        # Mise en place du modèle - doit être cohérent avec FenêtreQuestionsDevoir.maxCompétenceParQuestion
        self.modèle = Gtk.ListStore(str, \
                                    str,int,str,int,str,int,str,int,str,int,str,int,str,int,str,int,str,int,str,int)
        # Mise en place de la vue principale
        while self.vue.get_n_columns() > 0:
            self.vue.remove_column(self.vue.get_column(0))
        self.vue.set_model(self.modèle)
        rdNuméro = Gtk.CellRendererText()
        rdNuméro.set_property("editable",True)
        rdNuméro.connect("edited", self.celluleÉditée, (self.modèle,0,str))
        self.vue.append_column(Gtk.TreeViewColumn("N°",rdNuméro,text=0))
        for i in range(FenêtreQuestionsDevoir.maxCompétenceParQuestion):
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
            rdComp.connect("edited", self.celluleÉditée, (self.modèle,2*i+1,str))
            rdCoef.connect("edited", self.celluleÉditée, (self.modèle,2*i+2,int))
            col.pack_start(rdComp,True)
            col.pack_start(rdCoef,False)
            col.add_attribute(rdComp, "text", 2*i+1)
            col.add_attribute(rdCoef, "text", 2*i+2)
            self.vue.append_column(col)
        self.vue.append_column(Gtk.TreeViewColumn("",Gtk.CellRendererText()))
        self.vue.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        # Mise en place de la vue des modificateurs
        while self.vueModificateurs.get_n_columns() > 0:
            self.vueModificateurs.remove_column(self.vueModificateurs.get_column(0))
        typesModifs = Gtk.ListStore(str)
        [ typesModifs.append([typ]) for typ in devoir.get_listeCatégoriesModificateurs() ]
        col1, col2, col3 = Gtk.TreeViewColumn("Type de modificateur"), \
                           Gtk.TreeViewColumn("Nom"), Gtk.TreeViewColumn("Valeur")
        completion = Gtk.EntryCompletion()
        rdCatMod, rdNomMod, rdValMod = CellRendererAutoComplete(completion), \
                                       Gtk.CellRendererText(), Gtk.CellRendererText()
        completion.set_model(typesModifs)
        completion.pack_start(rdCatMod, True)
        completion.add_attribute(rdCatMod,"text",0)
        completion.props.text_column = 0
        completion.set_match_func(match_anywhere, None)
        rdCatMod.set_property("editable",True)
        rdNomMod.set_property("editable",True)
        rdValMod.set_property("editable",True)
        rdCatMod.connect("edited", self.celluleÉditée, (self.modèleModificateurs,0,str))
        rdNomMod.connect("edited", self.celluleÉditée, (self.modèleModificateurs,1,str))
        rdValMod.connect("edited", self.celluleÉditée, (self.modèleModificateurs,2,float))
        col1.pack_start(rdCatMod,True)
        col2.pack_start(rdNomMod,True)
        col3.pack_start(rdValMod,True)
        col1.add_attribute(rdCatMod, "text", 0)
        col2.add_attribute(rdNomMod, "text", 1)
        col3.add_attribute(rdValMod, "text", 2)
        col2.set_expand(True)
        col3.set_cell_data_func(rdValMod, \
                                lambda col, cell, model, iter, unused:
                                cell.set_property("text", "{:.2f}".format(model.get(iter, 2)[0])))
        self.vueModificateurs.append_column(col1)
        self.vueModificateurs.append_column(col2)
        self.vueModificateurs.append_column(col3)
        self.vue.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.ajouterLigne(self.modèleModificateurs)
        # Initialisation des données
        self.bdd = bdd
        self.idDev = idDev
        self.màjModèle()
        self.gestionAffichage()
        # Lancement
        self.fenêtre.show_all()
        réponse = self.fenêtre.run()
        if réponse == Gtk.ResponseType.OK:
            self.sauvegarderCompétences(None)
        self.fenêtre.hide()

    def ajouterLigne(self,modèle) -> None:
        """
        Fonction interne pour ajouter une ligne vide au modèle, servant à créer une nouvelle question.
        """
        if modèle == self.modèle:
            nom = ""
            cp_coeff = ["",0]*FenêtreQuestionsDevoir.maxCompétenceParQuestion
            self.modèle.append([nom]+cp_coeff)
        elif modèle == self.modèleModificateurs:
            self.modèleModificateurs.append(["","",0])

    def màjModèle(self) -> None:
        """
        Fonction interne qui reset les modèles à partir des données du self.devoir_save
        """
        self.modèle.clear()
        for q in self.devoir_save.get_listeQuestionsModèle(FenêtreQuestionsDevoir.maxCompétenceParQuestion):
            self.modèle.append(q)
        self.ajouterLigne(self.modèle)
        self.modèleModificateurs.clear()
        for m in self.devoir_save.get_listeModificateursModèle():
            self.modèleModificateurs.append(m)
        self.ajouterLigne(self.modèleModificateurs)
        self.saisieNoteMax.set_text(str(self.devoir_save.get_noteMax()))
        self.saisieNvxComp.set_text(str(self.devoir_save.get_niveauxAcquisition()))

    def celluleÉditée(self, cellule, path, text, data):
        """
        Callback pour la mise à jour du modèle quand une case est éditée.
        """
        modèle,num,typ = data
        text = typ(text)
        modèle[path][num] = text
        if int(path) == len(modèle)-1:  # gestion de l'ajout de nouvelle ligne
            self.ajouterLigne(modèle)
        self.gestionAffichage()

    def gestionAffichage(self):
        """
        Fonction ayant pour rôle de définir les colonnes visibles ou non.
        """
        listeCompétences = [ [k for k in a[1:] if type(k) == str and k != ""] for a in self.modèle ]
        nbCols = max([ len(a) for a in listeCompétences ]) + 2
        for i in range(1,nbCols):
            self.vue.get_column(i).set_visible(True)
        for i in range(nbCols,FenêtreQuestionsDevoir.maxCompétenceParQuestion+1):
            self.vue.get_column(i).set_visible(False)

    def sauvegarderCompétences(self,dummy):
        """
        Callback utilisé pour mettre à jour l'objet Devoir sous-jacent à partir du modèle.
        """
        listeModèle = [ ligne[:] for ligne in self.modèle ]
        listeModèle.pop()  # on enlève la ligne vide
        listeCompétences = [ ligne[0] for ligne in self.modèleCompétence ]
        self.devoir_save.set_questionsDepuisModèle(listeModèle, listeCompétences)
        listeModèle = [ ligne[:] for ligne in self.modèleModificateurs ]
        listeModèle.pop()  # on enlève la ligne vide
        self.devoir_save.set_modificateursDepuisModèle(listeModèle)
        self.devoir_save.set_noteMax(self.saisieNoteMax.get_text())
        self.devoir_save.set_niveauxAcquisition(self.saisieNvxComp.get_text())
        # Gestion de la BDD
        [ self.bdd.retraitQuestion(self.idDev, nom[0]) for nom in self.bdd.récupérerQuestions(self.idDev) ]
        questions = []
        for l in self.devoir_save.get_listeQuestionsModèle(FenêtreQuestionsDevoir.maxCompétenceParQuestion):
            n = l[0]
            comps = [ (l[2*i+1],l[2*i+2]) for i in range(len(l)//2) if l[2*i+1] != "" ]
            questions.append((n,comps))
        self.bdd.créerQuestions(self.idDev, questions)
        [ self.bdd.retraitModificateur(self.idDev,a[1]) for a in self.bdd.récupèreModificateurs(self.idDev) ]
        for mod in listeModèle:
            self.bdd.ajoutModificateur(self.idDev,mod[0],mod[1],mod[2])
        self.bdd.modifieNoteEtNiveauxDevoir(self.idDev, self.devoir_save.get_noteMax(), \
                                            self.devoir_save.get_niveauxAcquisition())
        self.màjModèle()


## Classe pour la saisie des évaluations lors d'un devoir
class FenêtreÉvaluationDevoir(object):
    """
    Classe gérant la construction d'une fenêtre popup pour l'évaluation d'un devoir
    par compétences.

    Doit reçevoir un objet Devoir en paramètre.
    """
    colÉtNo, colÉtNom, colÉtPrésence, colÉtÉvalué = 0,1,2,3
    colQuest, colComp, colCoef, colÉval = 0,1,2,3
    def __init__(self, devoir:Devoir, builder:Gtk.Builder):
        """
        Constructeur de la fenêtre.

        Utilise le patron disponible dans le .glade, donné par le Gtk.Builder, puis modifie
        les lignes en fonction des besoins du devoir considéré.
        """
        # Récupération de la fenêtre et des objets
        self.fenêtre = builder.get_object("fenêtreÉvaluationDevoir")
        self.modèle = builder.get_object("fenêtreÉvaluationDevoirModèle")
        self.vue = builder.get_object("fenêtreÉvaluationDevoirTreeView")
        self.sélecteurÉtudiant = builder.get_object("fenêtreÉvaluationDevoirSélecteurÉtudiant")
        self.switchPrésence = builder.get_object("fenêtreÉvaluationDevoirSwitchPrésence")
        self.modèlePointsFixes = builder.get_object("fenêtreÉvaluationDevoirModèlePointsFixes")
        self.modèleModificateurs = builder.get_object("fenêtreÉvaluationDevoirModèleModificateurs")
        self.vuePointsFixes = {'label':builder.get_object("fenêtreÉvaluationDevoirLabelPointsFixes"),
                               'tv':builder.get_object("fenêtreÉvaluationDevoirTreeViewPointsFixes"),
                               'rd':builder.get_object("fenêtreÉvaluationDevoirRdPointsFixes")}
        self.vueModificateurs = {'label':builder.get_object("fenêtreÉvaluationDevoirLabelModifs"),
                               'tv':builder.get_object("fenêtreÉvaluationDevoirTreeviewModifs"),
                               'rd':builder.get_object("fenêtreÉvaluationDevoirRdModifs")}
        self.fenêtre.set_title("Évaluation du " + devoir.get_enTêteDevoir())
        # Préparation des attributs autres
        self.devoir_save = devoir
        self.étudiantActif = 0
        # Sélection des étudiants
        self.modèleÉtudiants = Gtk.ListStore(int,str,bool,bool)
        for ét in devoir.get_listeÉtudiantsModèle():
            self.modèleÉtudiants.append(ét)
        self.sélecteurÉtudiant.set_model(self.modèleÉtudiants)
        renderer_étudiant = Gtk.CellRendererText()
        renderer_étudiant.set_property("foreground","grey")
        self.sélecteurÉtudiant.pack_start(renderer_étudiant, True)
        self.sélecteurÉtudiant.add_attribute(renderer_étudiant, "text", FenêtreÉvaluationDevoir.colÉtNom)
        self.sélecteurÉtudiant.set_active(self.étudiantActif)
        self.sélecteurÉtudiant.add_attribute(renderer_étudiant,'foreground-set',FenêtreÉvaluationDevoir.colÉtÉvalué)
        # Autres infos
        texte_nvx = "Niveaux d'acquisition : {}".format(devoir.get_niveauxAcquisition())
        builder.get_object("fenêtreÉvaluationDevoirLabelNvxComp").set_text(texte_nvx)
        builder.get_object("fenêtreÉvaluationDevoirTreeViewColonneÉval").\
            set_title("Éval (/{})".format(devoir.get_niveauxAcquisition()-1))
        col = builder.get_object("fenêtreÉvaluationDevoirColModifsVal")
        col.set_cell_data_func(builder.get_object("fenêtreÉvaluationDevoirColModifsValRd"), \
                               lambda col, cell, model, iter, unused:
                               cell.set_property("text", "{:.2f}".format(model.get(iter, 1)[0])))
        col = builder.get_object("fenêtreÉvaluationDevoirColPointsFixes")
        col.set_cell_data_func(builder.get_object("fenêtreÉvaluationDevoirRdPointsFixes"), \
                               lambda col, cell, model, iter, unused:
                               cell.set_property("text", "{:.2f}".format(model.get(iter, 2)[0])))
        col = builder.get_object("fenêtreÉvaluationDevoirColPointsFixes1")
        col.set_cell_data_func(builder.get_object("fenêtreÉvaluationDevoirRdPointsFixes1"), \
                               lambda col, cell, model, iter, unused:
                               cell.set_property("text", "{:.2f}".format(model.get(iter, 1)[0])))
        # Mise en place du modèle
        self.changeÉtudiant(self.sélecteurÉtudiant)
        rdr = builder.get_object("fenêtreÉvaluationDevoirTreeViewColonneNomRenderer")
        builder.get_object("fenêtreÉvaluationDevoirTreeViewColonneNom").add_attribute(rdr,'visible',4)
        # Connection des signaux
        builder.get_object("fenêtreÉvaluationDevoirÉditeurÉval").connect("edited", self.évaluationÉditée, \
                                                                         (self.modèle,int))
        builder.get_object("fenêtreÉvaluationDevoirSélecteurÉtudiant").connect("changed", self.changeÉtudiant)
        builder.get_object("fenêtreÉvaluationDevoirBoutonAppliquer").connect("clicked", self.sauvegarderÉvaluation)
        builder.get_object("fenêtreÉvaluationDevoirÉditeurÉval").connect("edited", self.évaluationÉditée,
                                                                         (self.modèle,int))
        self.switchPrésence.connect("state_set", self.switchPrésenceÉtudiant)
        builder.get_object("fenêtreÉvaluationDevoirColModifsÉval").connect("edited",self.évaluationÉditée, \
                                                                           (self.modèleModificateurs,int))
        builder.get_object("fenêtreÉvaluationDevoirRdPointsFixes").connect("edited",self.évaluationÉditée, \
                                                                           (self.modèlePointsFixes,float))
        # Lancement
        self.fenêtre.show()
        réponse = self.fenêtre.run()
        if réponse == Gtk.ResponseType.OK:
            self.sauvegarderÉvaluation(None)
        self.fenêtre.hide()

    def évaluationÉditée(self, cellule, path, text, data):
        """
        Callback pour la mise à jour du modèle quand une case est éditée.
        """
        modèle,typ = data
        try:
            val = typ(text)
            if modèle == self.modèle and val < self.devoir_save.get_niveauxAcquisition() and val > -2:
                modèle[path][FenêtreÉvaluationDevoir.colÉval] = val
            elif modèle == self.modèlePointsFixes and val <= modèle[path][1]:
                modèle[path][2] = val
            elif modèle == self.modèleModificateurs:
                modèle[path][2] = val
        except ValueError:  # cas d'un non-entier proposé
            pass

    def switchPrésenceÉtudiant(self, switch:Gtk.Switch, data:object) -> None:
        """
        Callback pour la modification du statut présent ou non de l'étudiant.
        """
        self.modèleÉtudiants[self.étudiantActif][FenêtreÉvaluationDevoir.colÉtPrésence] = switch.get_active()

    def changeÉtudiant(self, sélecteur:Gtk.ComboBox) -> None:
        """
        Callback pour le changement d'étudiant.
        """
        self.sauvegarderÉvaluation()
        self.étudiantActif = self.sélecteurÉtudiant.get_active()
        self.modèle.clear()
        self.modèlePointsFixes.clear()
        self.modèleModificateurs.clear()
        évaluation = self.devoir_save.get_évaluationÉtudiantModèle(self.étudiantActif)
        self.switchPrésence.set_active(évaluation[1])
        self.modèleÉtudiants[self.étudiantActif][FenêtreÉvaluationDevoir.colÉtPrésence] = évaluation[1]
        for row in évaluation[0]:
            if row[0] == "points fixes":
                self.modèlePointsFixes.append(row[1:])
            elif row[0] == "pourcentage":
                self.modèleModificateurs.append(row[1:])
            else:
                self.modèle.append(row + [True])
                if len(self.modèle) > 1 and self.modèle[-1][0] == self.modèle[-2][0]:
                    self.modèle[-1][-1] = False
        if len(self.modèlePointsFixes) == 0:
            self.vuePointsFixes['label'].set_visible(False)
            self.vuePointsFixes['tv'].set_visible(False)
        else:
            self.vuePointsFixes['label'].set_visible(True)
            self.vuePointsFixes['tv'].set_visible(True)
        if len(self.modèleModificateurs) == 0:
            self.vueModificateurs['label'].set_visible(False)
            self.vueModificateurs['tv'].set_visible(False)
        else:
            self.vueModificateurs['label'].set_visible(True)
            self.vueModificateurs['tv'].set_visible(True)

    def sauvegarderÉvaluation(self, data:object=None):
        """
        Callback pour sauvegarder l'évaluation de l'étudiant.
        """
        liste = [ ["points fixes"]+row[:] for row in self.modèlePointsFixes ] + \
                [ ["pourcentage"] +row[:] for row in self.modèleModificateurs] + \
                [ row[:] for row in self.modèle ]
        présence = self.modèleÉtudiants[self.étudiantActif][FenêtreÉvaluationDevoir.colÉtPrésence]
        self.devoir_save.set_évaluationÉtudiantModèle(self.étudiantActif, liste, présence)
        uneÉval = (np.array([ row[FenêtreÉvaluationDevoir.colÉval] for row in self.modèle ]) > -1).any()
        présence = self.modèleÉtudiants[self.étudiantActif][FenêtreÉvaluationDevoir.colÉtPrésence]
        self.modèleÉtudiants[self.étudiantActif][FenêtreÉvaluationDevoir.colÉtÉvalué] = uneÉval or not présence
