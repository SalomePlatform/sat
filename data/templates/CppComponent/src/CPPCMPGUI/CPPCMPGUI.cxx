// Copyright (C) 2007-2012  CEA/DEN, EDF R&D, OPEN CASCADE
//
// Copyright (C) 2003-2007  OPEN CASCADE, EADS/CCR, LIP6, CEA/DEN,
// CEDRAT, EDF R&D, LEG, PRINCIPIA R&D, BUREAU VERITAS
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
//
// See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
//

#include ":sat:{CPPCMP}GUI.h"
#include ":sat:{CPPCMP}_version.h"

#include <SalomeApp_Application.h>
#include <SalomeApp_Study.h>
#include <SalomeApp_DataObject.h>

#include <LightApp_SelectionMgr.h>

#include <SUIT_MessageBox.h>
#include <SUIT_ResourceMgr.h>
#include <SUIT_Desktop.h>

#include <QtxPopupMgr.h>

#include <SALOME_ListIO.hxx>

#include <SALOME_LifeCycleCORBA.hxx>
#include <SALOMEDS_SObject.hxx>
#include <SALOMEDS_Study.hxx>

#include <QInputDialog>

//! The only instance of the reference to engine
:sat:{CPPCMP}_ORB:::sat:{CPPCMP}_Gen_var :sat:{CPPCMP}GUI::myEngine;

/*!
  \brief Constructor

  Creates an instance of the :sat:{CPPCMP} GUI module.
  Initializes (loads if necessary) :sat:{CPPCMP} module engine.

  \note Since SalomeApp_Module uses virtual inheritance
  from LightApp_Module class, it's necessary to call both
  base classes constructors, even though :sat:{CPPCMP}GUI class
  inherits directly only SalomeApp_Module.
*/
:sat:{CPPCMP}GUI:::sat:{CPPCMP}GUI() :
    SalomeApp_Module(":sat:{CPPCMP}"), // module name
    LightApp_Module(":sat:{CPPCMP}")   // module name
{
    init(); // internal initialization
}

/*!
  \brief Destructor

  Destroys any allocated resources.
*/
:sat:{CPPCMP}GUI::~:sat:{CPPCMP}GUI()
{
    // nothing to do
}

/*!
  \brief Get a reference to the :sat:{CPPCMP} module CORBA engine

  \note This function returns vartype in order to minimize possible crashes
  when using this function with assignment operations.
  On the other hand, this simplifies usage of this function when using it outside
  the assignment operations, to minimize memory leaks caused by orphan CORBA
  references (no need to take care of reference counting).

  \return reference to the module engine
*/
:sat:{CPPCMP}_ORB:::sat:{CPPCMP}_Gen_var :sat:{CPPCMP}GUI::engine()
{
    init(); // initialize engine, if necessary
    return myEngine;
}

/*!
  \brief Module initialization.

  Overloaded from CAM_Module class.

  Perform general module initialization (like creation of actions,
  menus, toolbars, etc).

  \note This function is invoked only once per study, when the module
  is first time activated by the user.
  The study associated with the application might not exist
  (created or opened) when this function is invoked, so it is not
  recommended to perform any study-dependant actions here.

  \param app pointer to the current application instance
*/
void :sat:{CPPCMP}GUI::initialize(CAM_Application* app)
{
    // call the parent implementation
    SalomeApp_Module::initialize(app);

    // get reference to the desktop (used as a parent for actions)
    QWidget* dsk = app->desktop();
    // get resources manager
    SUIT_ResourceMgr* resMgr = app->resourceMgr();

    // create actions
    // ... Test me operation
    createAction(OpTestMe,                                       // operation id
        tr("TLT_OP_TESTME"),                                  // tooltip
        resMgr->loadPixmap(":sat:{CPPCMP}",tr("ICON_OP_TESTME")),   // icon
        tr("MEN_OP_TESTME"),                                  // menu title
        tr("STS_OP_TESTME"),                                  // status tip
        0,                                                      // accelerator (not set)
        dsk,                                                    // parent
        false,                                                  // togglable flag (no)
        this,                                                   // action receiver
        SLOT(testMe()));                                     // action slot
    // ... Hello operation
    createAction(OpHello,                                                // operation id
        tr("TLT_OP_HELLO"),                                   // tooltip
        resMgr->loadPixmap(":sat:{CPPCMP}",tr("ICON_OP_HELLO")),    // icon
        tr("MEN_OP_HELLO"),                                   // menu title
        tr("STS_OP_HELLO"),                                   // status tip
        0,                                                      // accelerator (not set)
        dsk,                                                    // parent
        false,                                                  // togglable flag (no)
        this,                                                   // action receiver
        SLOT(hello()));                                      // action slot
    // ... Goodbye operation
    createAction(OpGoodbye,                                              // operation id
        tr("TLT_OP_GOODBYE"),                                 // tooltip
        resMgr->loadPixmap(":sat:{CPPCMP}",tr("ICON_OP_GOODBYE")),  // icon
        tr("MEN_OP_GOODBYE"),                                 // menu title
        tr("STS_OP_GOODBYE"),                                 // status tip
        0,                                                      // accelerator (not set)
        dsk,                                                    // parent
        false,                                                  // togglable flag (no)
        this,                                                   // action receiver
        SLOT(goodbye()));                                    // action slot

    // create menus
    int menuId;
    menuId = createMenu(tr("MEN_FILE"), -1, -1);                      // File menu
    createMenu(separator(), menuId, -1, 10);                            // add separator to File menu
    menuId = createMenu(tr("MEN_FILE_HELLO"), menuId, -1, 10);        // File - Hello submenu
    createMenu(OpTestMe, menuId);                                       // File - Hello - Test me
    menuId = createMenu(tr("MEN_HELLO"), -1, -1, 30);                 // Hello menu
    createMenu(OpHello, menuId, 10);                                    // Hello - Hello
    createMenu(OpGoodbye, menuId, 10);                                  // Hello - Goodbye

    // create toolbars
    int aToolId;
    aToolId = createTool (tr("TOOL_TEST"));                           // Test toolbar
    createTool(OpTestMe, aToolId);                                      // Test - Test me
    aToolId = createTool (tr("TOOL_HELLO"));                          // Hello toolbar
    createTool(OpHello, aToolId);                                       // Hello - Hello
    createTool(OpGoodbye, aToolId);                                     // Hello - Goodbye

    // set-up popup menu
    QtxPopupMgr* mgr = popupMgr();
    mgr->insert(action(OpHello),   -1, -1);                           // Hello
    mgr->insert(action(OpGoodbye), -1, -1);                           // Goodbye
    mgr->insert(separator(),         -1, -1);                           // -----------
    mgr->insert(action(OpTestMe),  -1, -1);                           // Test me
    QString baseRule = "client='ObjectBrowser' and selcount=1 and $component={':sat:{CPPCMP}'}";
    mgr->setRule(action(OpHello),   baseRule + " and isComponent",  QtxPopupMgr::VisibleRule);
    mgr->setRule(action(OpGoodbye), baseRule + " and !isComponent", QtxPopupMgr::VisibleRule);
}

/*!
  \brief Get module engine IOR

  Overloaded from SalomeApp_Module class.

  \return string representing module engine IOR
*/
QString :sat:{CPPCMP}GUI::engineIOR() const
{
    init(); // initialize engine, if necessary
    CORBA::String_var anIOR = getApp()->orb()->object_to_string(myEngine.in());
    return QString(anIOR.in());
}

/*!
  \brief Get module icon.

  Overloaded from CAM_Module class.

  Load and return the module icon pixmap. This icon is shown
  in the Object browser, in modules toolbar, etc.

  Default implementation uses iconName() function to retrieve the name
  of the image file to be used as the module icon; tries to load this
  file from module's resources and create pixmap from it.
  Returns valid QPixmap instance if image is loaded correctly.
  This function can be customized to provide another way to get module icon.

  \return module icon pixmap
  \sa iconName()
*/
QPixmap :sat:{CPPCMP}GUI::moduleIcon() const
{
    // nothing to do, in this example just call the parent implementation
    return SalomeApp_Module::moduleIcon();
}

/*!
  \brief Get module icon's file name.

  Overloaded from CAM_Module class.

  This function is used to get module icon image file name.
  Default implementation tries to retrieve the name of the
  icon file from the application using moduleIcon() function, which
  in its turn retrieves the information about the module icon
  from the configuration file (e.g. SalomeApp.xml, LightApp.xml).
  This function can be customized to provide another way to get module icon's
  file name.

  \return module icon file name
  \sa moduleIcon()
*/
QString :sat:{CPPCMP}GUI::iconName() const
{
    // nothing to do, in this example just call the parent implementation
    return SalomeApp_Module::iconName();
}

/*!
  \brief Request dockable windows to be available when module is active.

  Overloaded from LightApp_Module class.

  Fills and returns the list of dockable windows which should be
  available when the module is active. It is a map of integer values
  where \c key is an enumerator from LightApp_Application::WindowTypes
  enumeration, specifying window type, and \c value is an enumerator
  from Qt::DockWidgetArea, specifying the window's default position
  in the main window layout.

  Empty map means no dockable windows available when the module is active.

  \param theMap this map should be filled to specify the list of
                required dockable windows withe their default positions
*/
void :sat:{CPPCMP}GUI::windows(QMap<int, int>& theMap) const
{
    // want Object browser, in the left area
    theMap.insert(SalomeApp_Application::WT_ObjectBrowser,
         Qt::LeftDockWidgetArea);
    // want Python console, in the bottom area
    theMap.insert(SalomeApp_Application::WT_PyConsole,
         Qt::BottomDockWidgetArea);
}

/*!
  \brief Request view windows (types) to be activated when module is activated..

  Overloaded from LightApp_Module class.

  Fills and returns the list of 3D/2D view windows types compatible
  with this module. The views of the specified type(s) will be automatically
  activated (raised to the top of view stack) each time when the module
  is activated by the user (the views will be automatically created if they
  do not exist at the module activation).
  Empty list means no compatible view windows for the module.

  Example:
  \code
  theList.append(OCCViewer_Viewer::Type());
  theList.append(SVTK_Viewer::Type());
  \endcode

  \param theList this list should be filled to specify the list of
                 compatible view window types
*/
void :sat:{CPPCMP}GUI::viewManagers(QStringList& /*theList*/) const
{
    // no compatible view managers, nothing to do here
}

/*!
  \brief Create popup selection handler.

  Overloaded from LightApp_Module class.

  This function can be used to create custom popup menu handler.
  The application takes ownership over the returned pointer,
  so you should not destroy it.

  This function is part of the context popup menu management mechanism.
  Selection object (instance of LightApp_Selection class or its successor)
  analizes the currently selected items and defines selection-dependant
  variables which are processed by the popup manager (QtxPopupMgr class).

  These variables can be included into the lexical constructions, named
  "rules", which are associated with the popup menu actions (refer to the
  QtxPopupMgr class for more details).

  Exampe:
  \code
  // obtain popup manager
  QtxPopupMgr* mgr = popupMgr();
  // create new action, with ID = 100
  createAction(100, "Action", QIcon(), "Action", "My action", 0, application()->desktop(),
                false, this, SLOT(OnMyAction()));
  // define popup rule for action
  QString rule = "client='ObjectBrowser' and $type in {'MyType1' 'MyType2'} and selcount=1";
  // set visibility rule for action
  mgr->setRule(100, rule, QtxPopupMgr::VisibleRule);
  \endcode

  In the above code, \a selcount variable is automatically defined
  by LightApp_Selection class, but \a type variable should be set by
  the successor class. Note, that LightApp_Selection class implements
  several useful variables which can be used in the lexical rules.

  \return new selection object
  \sa contextMenuPopup()
*/
LightApp_Selection* :sat:{CPPCMP}GUI::createSelection() const
{
    // nothing to do, in this example just call the parent implementation
    // see also initialize()
    return SalomeApp_Module::createSelection();
}

/*!
  \brief Create displayer object.

  Overloaded from LightApp_Module class.

  This function can be used to create and return custom displayer object.
  The application does not take the ownership over the returned value.

  Displayer is a part of the presentations management system.
  If can be used to implement visualization operations, like create, show
  or hide presentation in the viewer of specific type, etc.

  \return pointer to the module displayer
 */
LightApp_Displayer* :sat:{CPPCMP}GUI::displayer()
{
    // nothing to do, in this example just call the parent implementation
    return SalomeApp_Module::displayer();
}

/*!
  \brief Create context popup menu.

  Overloaded from CAM_Module class.

  This function can be used to customize context popup menu management.
  The module should fill \a menu with the items (e.g. by inserting own
  QAction items). The menu contents can be context-depending, the parameter
  \a type can be used to test the context of the popup menu invocation
  (e.g. "ObjectBrowser").
  Parameter \a title can be used to return the string value to be used
  popup menu title if required.

  Default implementation from LightApp_Module class calls createSelection()
  function to create popup selection handler and initialized the popup menu
  using popup manager.

  \param type popup menu context
  \param menu pointer to the popup menu
  \param title custom popup menu title can be returned here
  \sa createSelection()
*/
void :sat:{CPPCMP}GUI::contextMenuPopup(const QString& type, QMenu* menu, QString& title)
{
    // nothing to do, in this example just call the parent implementation
    // see also initialize()
    return SalomeApp_Module::contextMenuPopup(type, menu, title);
}

/*!
  \brief Export module preferences.

  Overloaded from LightApp_Module class.

  This function is invoked only once when the common "Preferences"
  dialog box is first time activated by the user (via the "File/Preferences"
  menu command) or when module is first time activated.

  This function should be used to export module preferences to the
  common "Preferences" dialog box and associate them with the corresponding
  widgets. The preferences items are arranged to the tree-like structure, where
  top-level items represent just a containers for the underlying items.
  Each low-level preferences item is linked to the resources item (via "section"
  and "parameter" attributes). See QtxResourceMgr class for more details about
  resources management.

  Example:
  \code
  // create top-level preferences tab page
  int settingsId = addPreference("Settings");
  // create general settings group box
  int generalId = addPreference(tr("General"), settingsId);
  // set group box property - number of columns - to 2
  setPreferenceProperty(generalId, "columns", 2);
  // create shading color preferences item (color button)
  addPreference("Shading color", generalId, LightApp_Preferences::Color,
                 ":sat:{CPPCMP}", "shading_color");
  // create precision preferences item (spin box)
  int precisionId = addPreference(tr("GEOM_PREF_length_precision"), generalId,
                 LightApp_Preferences::IntSpin, ":sat:{CPPCMP}", "precision");
  // set precision preferences item properties
  setPreferenceProperty(precisionId, "min", 0);
  setPreferenceProperty(precisionId, "max", 10);
  \endcode

  \sa preferencesChanged()
*/
void :sat:{CPPCMP}GUI::createPreferences()
{
    // no module preferences, nothing to do here
}

/*!
  \brief Process preference item change event.

  Overloaded from LightApp_Module class.

  This function is called every time when the preference item
  owned by this module is changed by the user (usually this occurs when
  the user presses "OK" or "Apply" button in the "Preferences" dialog box).

  The module can perform any specific actions if necessary to response
  to the preferences changes.

  \param section resources item section name
  \param parameter resources item parameter name

  \sa createPreferences()
*/
void :sat:{CPPCMP}GUI::preferencesChanged(const QString& section, const QString& parameter)
{
    // nothing to do, in this example just call the parent implementation
    SalomeApp_Module::preferencesChanged(section, parameter);
}

/*!
  \brief Store visual state.

  Overloaded from SalomeApp_Module class.

  This method is called just before the study document is saved,
  so the module has a possibility to store any visual parameters
  in the AttributeParameter study attribute (if required).

  \param savePoint save point unique identifier
*/
void :sat:{CPPCMP}GUI::storeVisualParameters(int /*savePoint*/)
{
    // no specific visual state, nothing to do here
}

/*!
  \brief Restore visual state.

  Overloaded from SalomeApp_Module class.

  This method is called after the study document is opened,
  so the module has a possibility to restore the visual parameters
  from the AttributeParameter study attribute (if required).

  \param savePoint save point unique identifier
*/
void :sat:{CPPCMP}GUI::restoreVisualParameters(int /*savePoint*/)
{
    // no specific visual state, nothing to do here
}

/*!
  \brief Handle active study changing action.

  Overloaded from LightApp_Module class.

  This function is called each time when the active study is changed
  (usually this happens when users switches between different studies'
  desktops).

  Can be used to perform any relevant actions.
*/
void :sat:{CPPCMP}GUI::studyActivated()
{
    // no any specific action required, nothing to do here
}

/*!
  \brief Check if the module can perform "copy" operation.

  Overloaded from LightApp_Module class.

  This function is a part of the general copy/paste mechanism.

  Can be re-implemented to customize the copy/paste handling
  in the module. Default implementation returns \c false.

  \return \c true if the module can perform "copy" operation or \c false otherwise
  \sa canPaste(), copy(), paste()
*/
bool :sat:{CPPCMP}GUI::canCopy() const
{
    // copy/paste is not supported, in this example just call the parent implementation
    return SalomeApp_Module::canCopy();
}

/*!
  \brief Check if the module can perform "paste" operation.

  Overloaded from LightApp_Module class.

  This function is a part of the general copy/paste mechanism.

  Can be re-implemented to customize the copy/paste handling
  in the module. Default implementation returns \c false.

  \return \c true if the module can perform "paste" operation or \c false otherwise
  \sa canCopy(), copy(), paste()
*/
bool :sat:{CPPCMP}GUI::canPaste() const
{
    // copy/paste is not supported, in this example just call the parent implementation
    return SalomeApp_Module::canPaste();
}

/*!
  \brief Perform "copy" operation.

  Overloaded from LightApp_Module class.

  This function is a part of the general copy/paste mechanism.

  Can be re-implemented to customize the copy/paste handling
  in the module. Default implementation does nothing.

  \sa canCopy(), canPaste(), paste()
*/
void :sat:{CPPCMP}GUI::copy()
{
    // copy/paste is not supported, nothing to do here
}

/*!
  \brief Perform "paste" operation.

  Overloaded from LightApp_Module class.

  This function is a part of the general copy/paste mechanism.

  Can be re-implemented to customize the copy/paste handling
  in the module. Default implementation does nothing.

  \sa canCopy(), canPaste(), copy()
*/
void :sat:{CPPCMP}GUI::paste()
{
    // copy/paste is not supported, nothing to do here
}

/*!
  \brief Check if the module allows "drag" operation of its objects.

  Overloaded from LightApp_Module class.

  This function is a part of the general drag-n-drop mechanism.
  The goal of this function is to check data object passed as a parameter
  and decide if it can be dragged or no.

  \param what data object being tested for drag operation
  \return \c true if module allows dragging of the specified object
  \sa isDropAccepted(), dropObjects()
*/
bool :sat:{CPPCMP}GUI::isDraggable(const SUIT_DataObject* what) const
{
    // we allow dragging any :sat:{CPPCMP} object, except the top-level component
    const SalomeApp_ModuleObject* aModObj = dynamic_cast<const SalomeApp_ModuleObject*>(what);
    return (aModObj == 0);
}

/*!
  \brief Check if the module allows "drop" operation on the given object.

  Overloaded from LightApp_Module class.

  This function is a part of the general drag-n-drop mechanism.
  The goal of this function is to check data object passed as a parameter
  and decide if it can be used as a target for the "drop" operation.
  The processing of the drop operation itself is done in the dropObjects() function.

  \param where target data object
  \return \c true if module supports dropping on the \a where data object
  \sa isDraggable(), dropObjects()
*/
bool :sat:{CPPCMP}GUI::isDropAccepted(const SUIT_DataObject* where) const
{
    // we allow dropping of all objects
    // (temporarily implementation, we also need to check objects being dragged)
    return true;
}

/*!
  \brief Complete drag-n-drop operation.

  Overloaded from LightApp_Module class.

  This function is a part of the general drag-n-drop mechanism.
  Its goal is to handle dropping of the objects being dragged according
  to the chosen operation (copy or move). The dropping is performed in the
  context of the parent data object \a where and the \a row (position in the
  children index) at which the data should be dropped. If \a row is equal to -1,
  this means that objects are added to the end of the children list.

  \param what objects being dropped
  \param where target data object
  \param row child index at which the drop operation is performed
  \param action drag-n-drop operation (Qt::DropAction) - copy or move

  \sa isDraggable(), isDropAccepted()
*/
void :sat:{CPPCMP}GUI::dropObjects(const DataObjectList& what, SUIT_DataObject* where,
                const int row, Qt::DropAction action)
{
    if (action != Qt::CopyAction && action != Qt::MoveAction)
        return; // unsupported action

    // get parent object
    SalomeApp_DataObject* dataObj = dynamic_cast<SalomeApp_DataObject*>(where);
    if (!dataObj) return; // wrong parent
    _PTR(SObject) parentObj = dataObj->object();

    // collect objects being dropped
    :sat:{CPPCMP}_ORB::object_list_var objects = new :sat:{CPPCMP}_ORB::object_list();
    objects->length(what.count());
    int count = 0;
    for (int i = 0; i < what.count(); i++)
    {
        dataObj = dynamic_cast<SalomeApp_DataObject*>(what[i]);
        if (!dataObj) continue;  // skip wrong objects
        _PTR(SObject) sobj = dataObj->object();
        objects[i] = _CAST(SObject, sobj)->GetSObject();
        count++;
    }
    objects->length(count);

    // call engine function
    engine()->copyOrMove(objects.in(),                              // what
                         _CAST(SObject, parentObj)->GetSObject(),   // where
                         row,                                       // row
                         action == Qt::CopyAction);                // isCopy

    // update Object browser
    getApp()->updateObjectBrowser(false);
}

/*!
  \brief Module activation.

  Overloaded from CAM_Module class.

  This function is called each time the module is activated
  by the user. It is usually used to perform any relevant actions,
  like displaying menus and toolbars, connecting specific signals/slots, etc.

  \param theStudy current study object
  \return \c true if activation is completed correctly or \c false
          if module activation fails

  \sa deactivateModule()
*/
bool :sat:{CPPCMP}GUI::activateModule(SUIT_Study* theStudy)
{
    // call parent implementation
    bool bOk = SalomeApp_Module::activateModule(theStudy);

    // show own menus
    setMenuShown(true);
    // show own toolbars
    setToolShown(true);

    // return the activation status
    return bOk;
}

/*!
  \brief Module deactivation.

  Overloaded from CAM_Module class.

  This function is called each time the module is deactivated
  by the user. It is usually used to perform any relevant actions,
  like hiding menus and toolbars, disconnecting specific signals/slots, etc.

  \param theStudy current study object
  \return \c true if deactivation is completed correctly or \c false
          if module deactivation fails

  \sa activateModule()
*/
bool :sat:{CPPCMP}GUI::deactivateModule(SUIT_Study* theStudy)
{
    // hide own menus
    setMenuShown(false);
    // hide own toolbars
    setToolShown(false);

    // call parent implementation and return the activation status
    return SalomeApp_Module::deactivateModule(theStudy);
}

/*!
  \brief Create specific operation object.

  Overloaded from LightApp_Module class.

  This function is a part of operation management mechanism.
  It can be used to create module specific operations, if module
  implements transaction handling basing on the GUI operations instances.

  This function is automatically called from startOperation() function.
  After operation is created, it can be started/stopped/paused/resumed etc.
  Compatibility between diferent simultaneously running operations is also
  checked by invoking of the corresponding methods of the LightApp_Operation
  class.

  The application takes ownership over the returned pointer,
  so you should not destroy it.

  Default implementation in LightApp_Module class processes common Show/Hide
  operations.

  \param id unique operation identifier
  \return new operation object
*/
LightApp_Operation* :sat:{CPPCMP}GUI::createOperation(const int id) const
{
    // no specific operations, in this example just call the parent implementation
    return SalomeApp_Module::createOperation(id);
}

/*!
  \brief Action slot: Test me
*/
void :sat:{CPPCMP}GUI::testMe()
{
    SUIT_MessageBox::information(getApp()->desktop(),
                tr("INF_TESTME_TITLE"),
                tr("INF_TESTME_MSG"),
                tr("BUT_OK"));
}

/*!
  \brief Action slot: Hello
*/
void :sat:{CPPCMP}GUI::hello()
{
    SalomeApp_Study* study = dynamic_cast<SalomeApp_Study*>(application()->activeStudy());
    _PTR(Study) studyDS = study->studyDS();

    // request user name
    bool ok;
    QString name = QInputDialog::getText(getApp()->desktop(), tr("QUE_HELLO_TITLE"), tr("QUE_ENTER_NAME"),
                    QLineEdit::Normal, QString::null, &ok);

    if (ok && !name.trimmed().isEmpty())
    {
        // say hello to SALOME
        :sat:{CPPCMP}_ORB::status status = engine()->hello(_CAST(Study, studyDS)->GetStudy(), (const char*)name.toLatin1());

        // update Object browser
        getApp()->updateObjectBrowser(true);

        // process operation status
        switch(status)
        {
            case :sat:{CPPCMP}_ORB::OP_OK:
                // everything's OK
                SUIT_MessageBox::information(getApp()->desktop(),
                    tr("INF_HELLO_TITLE"),
                    tr("INF_HELLO_MSG").arg(name),
                    tr("BUT_OK"));
                break;
            case :sat:{CPPCMP}_ORB::OP_ERR_ALREADY_MET:
                // error: already said hello
                SUIT_MessageBox::warning(getApp()->desktop(),
                    tr("INF_HELLO_TITLE"),
                    tr("ERR_HELLO_ALREADY_MET").arg(name),
                    tr("BUT_OK"));
                break;
            case :sat:{CPPCMP}_ORB::OP_ERR_UNKNOWN:
            default:
                // other errors
                SUIT_MessageBox::critical(getApp()->desktop(),
                    tr("INF_HELLO_TITLE"),
                    tr("ERR_ERROR"),
                    tr("BUT_OK"));
                break;
        }
    }
}

/*!
  \brief Action slot: Goodbye
*/
void :sat:{CPPCMP}GUI::goodbye()
{
    SalomeApp_Application* app = dynamic_cast<SalomeApp_Application*>(application());
    SalomeApp_Study* study = dynamic_cast<SalomeApp_Study*>(application()->activeStudy());
    _PTR(Study) studyDS = study->studyDS();
    LightApp_SelectionMgr* aSelMgr = app->selectionMgr();

    QString name;

    // get selection
    SALOME_ListIO selected;
    aSelMgr->selectedObjects(selected);
    if (selected.Extent() == 1)
    {
        Handle(SALOME_InteractiveObject) io = selected.First();
        _PTR(SObject) so = studyDS->FindObjectID(io->getEntry());
        if (so)
        {
            _PTR(SComponent) comp = so->GetFatherComponent();
            if (comp && comp->ComponentDataType() == "HELLO" && io->getEntry() != comp->GetID())
            {
                name = so->GetName().c_str();
            }
        }
    }

    // request user name if not specified
    if (name.isEmpty())
    {
        bool ok;
        name = QInputDialog::getText(getApp()->desktop(), tr("QUE_GOODBYE_TITLE"), tr("QUE_ENTER_NAME"),
                  QLineEdit::Normal, QString::null, &ok);
    }

    if (!name.trimmed().isEmpty())
    {
        // say goodby to SALOME
        :sat:{CPPCMP}_ORB::status status = engine()->goodbye(_CAST(Study, studyDS)->GetStudy(), (const char*)name.toLatin1());

        // update Object browser
        getApp()->updateObjectBrowser(true);

        // process operation status
        switch(status)
        {
            case :sat:{CPPCMP}_ORB::OP_OK:
                // everything's OK
                SUIT_MessageBox::information(getApp()->desktop(),
                    tr("INF_GOODBYE_TITLE"),
                    tr("INF_GOODBYE_MSG").arg(name),
                    tr("BUT_OK"));
                break;
            case :sat:{CPPCMP}_ORB::OP_ERR_DID_NOT_MEET:
                // error: did not say hello yet
                SUIT_MessageBox::warning(getApp()->desktop(),
                    tr("INF_GOODBYE_TITLE"),
                    tr("ERR_GOODBYE_DID_NOT_MEET").arg(name),
                    tr("BUT_OK"));
                break;
            case :sat:{CPPCMP}_ORB::OP_ERR_UNKNOWN:
            default:
                // other errors
                SUIT_MessageBox::critical(getApp()->desktop(),
                tr("INF_GOODBYE_TITLE"),
                tr("ERR_ERROR"),
                tr("BUT_OK"));
                break;
        }
    }
}

/*!
  \brief Perform internal initialization

  In particular, this function initializes module engine.
*/
void :sat:{CPPCMP}GUI::init()
{
    // initialize :sat:{CPPCMP} module engine (load, if necessary)
    if (CORBA::is_nil(myEngine))
    {
        Engines::EngineComponent_var comp =
            SalomeApp_Application::lcc()->FindOrLoad_Component("FactoryServer", ":sat:{CPPCMP}");
        myEngine = :sat:{CPPCMP}_ORB:::sat:{CPPCMP}_Gen::_narrow(comp);
    }
}

// Export the module
extern "C" {
    // FACTORY FUNCTION: create an instance of the :sat:{CPPCMP} module GUI
    CAM_Module* createModule()
    {
        return new :sat:{CPPCMP}GUI();
    }
    // VERSIONING FUNCTION: get :sat:{CPPCMP} module's version identifier
    char* getModuleVersion()
    {
        return (char*):sat:{CPPCMP}_VERSION_STR; // HELLO_VERSION_STR is defined in :sat:{CPPCMP}_version.h
    }
}
