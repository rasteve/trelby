import config
import util
from wxPython.wx import *

class FindDlg(wxDialog):
    def __init__(self, parent, ctrl, cfg):
        wxDialog.__init__(self, parent, -1, "Find & Replace",
                          pos = wxDefaultPosition,
                          size = (400, 130),
                          style = wxDEFAULT_DIALOG_STYLE | wxWANTS_CHARS)

        self.ctrl = ctrl
        
        self.Center()

        panel = wxPanel(self, -1)
        
        hsizer = wxBoxSizer(wxHORIZONTAL)
        panel.SetSizer(hsizer)

        vsizer = wxBoxSizer(wxVERTICAL)
        
        gsizer = wxFlexGridSizer(2, 2, 5, 20)
        gsizer.AddGrowableCol(1)
        
        gsizer.Add(wxStaticText(panel, -1, "Find what:"))
        self.findEntry = wxTextCtrl(panel, -1)
        gsizer.Add(self.findEntry, 0, wxEXPAND)

        gsizer.Add(wxStaticText(panel, -1, "Replace with:"))
        self.replaceEntry = wxTextCtrl(panel, -1)
        gsizer.Add(self.replaceEntry, 0, wxEXPAND)
        
        vsizer.Add(gsizer, 0, wxEXPAND | wxBOTTOM, 10)

        hsizer2 = wxBoxSizer(wxHORIZONTAL)

        vsizer2 = wxBoxSizer(wxVERTICAL)

        self.matchWholeCb = wxCheckBox(panel, -1, "Match whole word only")
        vsizer2.Add(self.matchWholeCb)

        self.matchCaseCb = wxCheckBox(panel, -1, "Match case")
        vsizer2.Add(self.matchCaseCb)

        hsizer2.Add(vsizer2, 0, wxEXPAND)

        self.direction = wxRadioBox(panel, -1, "Direction",
                                    choices = ["Up", "Down"])
        self.direction.SetSelection(1)
        
        hsizer2.Add(self.direction, 1, 0)
        
        vsizer.Add(hsizer2, 0, wxEXPAND | wxBOTTOM, 10)

        self.extraLabel = wxStaticText(panel, -1, "Search in:")
        vsizer.Add(self.extraLabel)

        self.elements = wxCheckListBox(panel, -1)

        for t in cfg.types.values():
            self.elements.Append(t.name, t.type)

        for i in range(0, self.elements.GetCount()):
            self.elements.Check(i, True)
            
        vsizer.Add(self.elements, 1, wxEXPAND)
        
        hsizer.Add(vsizer, 1, wxEXPAND)
        
        vsizer = wxBoxSizer(wxVERTICAL)
        
        find = wxButton(panel, -1, "&Find next")
        vsizer.Add(find, 0, wxBOTTOM, 5)

        replace = wxButton(panel, -1, "&Replace")
        vsizer.Add(replace, 0, wxBOTTOM, 5)
        
        replaceAll = wxButton(panel, -1, "Replace &all")
        vsizer.Add(replaceAll, 0, wxBOTTOM, 5)

        self.moreButton = wxButton(panel, -1, "")
        vsizer.Add(self.moreButton, 0, wxBOTTOM, 5)

        hsizer.Add(vsizer, 0, wxEXPAND | wxLEFT, 30)

        EVT_BUTTON(self, find.GetId(), self.OnFind)
        EVT_BUTTON(self, replace.GetId(), self.OnReplace)
        EVT_BUTTON(self, replaceAll.GetId(), self.OnReplaceAll)
        EVT_BUTTON(self, self.moreButton.GetId(), self.OnMore)

        EVT_CHAR(panel, self.OnCharMisc)
        EVT_CHAR(self.findEntry, self.OnCharEntry)
        EVT_CHAR(self.replaceEntry, self.OnCharEntry)
        EVT_CHAR(find, self.OnCharButton)
        EVT_CHAR(replace, self.OnCharButton)
        EVT_CHAR(replaceAll, self.OnCharButton)
        EVT_CHAR(self.moreButton, self.OnCharButton)
        EVT_CHAR(self.matchWholeCb, self.OnCharMisc)
        EVT_CHAR(self.matchCaseCb, self.OnCharMisc)
        EVT_CHAR(self.direction, self.OnCharMisc)
        EVT_CHAR(self.elements, self.OnCharMisc)
        
        vmsizer = wxBoxSizer(wxVERTICAL)
        vmsizer.Add(panel, 1, wxEXPAND | wxALL, 10)

        self.showExtra(False)
        
        self.SetSizer(vmsizer)
        self.Layout()
        
        self.findEntry.SetFocus()

    def OnMore(self, event):
        self.showExtra(not self.useExtra)

    def OnCharEntry(self, event):
        self.OnChar(event, True, False)

    def OnCharButton(self, event):
        self.OnChar(event, False, True)

    def OnCharMisc(self, event):
        self.OnChar(event, False, False)

    def OnChar(self, event, isEntry, isButton):
        kc = event.GetKeyCode()

        if kc == WXK_ESCAPE:
            self.EndModal(wxID_OK)
            return

        if kc == WXK_RETURN:
            if isButton:
                event.Skip()
                return
            else:
                self.OnFind()
                return
            
        if isEntry:
            event.Skip()
        else:
            if kc < 256:
                if chr(kc) == "f":
                    self.OnFind()
                elif chr(kc) == "r":
                    self.OnReplace()
                elif chr(kc) == "a":
                    self.OnReplaceAll()
                else:
                    event.Skip()
            else:
                event.Skip()

    def showExtra(self, flag):
        self.extraLabel.Show(flag)
        self.elements.Show(flag)

        self.useExtra = flag

        if flag:
            self.moreButton.SetLabel("<<< Less")
            self.SetClientSizeWH(self.GetClientSize().width, 260)
        else:
            self.moreButton.SetLabel("More >>>")
            self.SetClientSizeWH(self.GetClientSize().width, 130)
            
    def getParams(self):
        self.dirUp = self.direction.GetSelection() == 0
        self.matchWhole = self.matchWholeCb.IsChecked()
        self.matchCase = self.matchCaseCb.IsChecked()

        if self.useExtra:
            self.elementMap = {}
            for i in range(0, self.elements.GetCount()):
                self.elementMap[self.elements.GetClientData(i)] = \
                    self.elements.IsChecked(i)
            
    def typeIncluded(self, type):
        if not self.useExtra:
            return True

        return self.elementMap[type]
        
    def OnFind(self, event = None):
        self.getParams()

        value = self.findEntry.GetValue()
        if not self.matchCase:
            value = value.upper()

        if value == "":
            return
        
        self.ctrl.searchWidth = len(value)
        
        if self.dirUp:
            inc = -1
        else:
            inc = 1
            
        line = self.ctrl.line
        col = self.ctrl.column
        ls = self.ctrl.sp.lines

        if (line == self.ctrl.searchLine) and (col == self.ctrl.searchColumn):
            text = ls[line].text
            
            col += inc
            if col >= len(text):
                line += 1
                col = 0
            elif col < 0:
                line -= 1
                if line >= 0:
                    col = max(len(ls[line].text) - 1, 0)

        fullSearch = False
        if inc > 0:
            if (line == 0) and (col == 0):
                fullSearch = True
        else:
            if (line == (len(ls) - 1)) and (col == (len(ls[line].text))):
                fullSearch = True

        self.ctrl.searchLine = -1
        
        while True:
            found = False

            while True:
                if (line >= len(ls)) or (line < 0):
                    break

                if self.typeIncluded(ls[line].type):
                    text = ls[line].text
                    if not self.matchCase:
                        text = text.upper()

                    if inc > 0:
                        res = text.find(value, col)
                    else:
                        res = text.rfind(value, 0, col + 1)

                    if res != -1:
                        if not self.matchWhole or (
                            util.isWordBoundary(text[res - 1 : res]) and
                            util.isWordBoundary(text[res + len(value) :
                                                     res + len(value) + 1])):

                            found = True

                            break

                line += inc
                if inc > 0:
                    col = 0
                else:
                    if line >= 0:
                        col = max(len(ls[line].text) - 1, 0)

            if found:
                self.ctrl.line = line
                self.ctrl.column = res
                self.ctrl.makeLineVisible(line)
                self.ctrl.searchLine = line
                self.ctrl.searchColumn = res
                self.ctrl.updateScreen()

                break
            else:
                if fullSearch:
                    wxMessageBox("Search finished without results.",
                                 "No matches", wxOK, self)

                    break
                
                if inc > 0: 
                    s1 = "end"
                    s2 = "start"
                    restart = 0
                else:
                    s1 = "start"
                    s2 = "end"
                    restart = len(ls) - 1

                if wxMessageBox("Search finished at the %s of the script. Do\n"
                                "you want to continue at the %s of the script?"
                                % (s1, s2), "Continue?",
                                wxYES_NO | wxYES_DEFAULT, self) == wxYES:
                    line = restart
                    fullSearch = True
                else:
                    break

        self.ctrl.updateScreen()

            
    def OnReplace(self, event = None):
        print "replace"
            
    def OnReplaceAll(self, event = None):
        print "replace all"