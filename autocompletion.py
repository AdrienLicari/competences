#!/usr/bin/python3

"""
Module étendant les capacités de Gtk pour créer des entrées avec autocomplétion adaptées.
"""

## imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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
