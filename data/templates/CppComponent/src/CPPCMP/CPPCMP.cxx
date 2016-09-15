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

#include ":sat:{CPPCMP}.hxx"
#include ":sat:{CPPCMP}_version.h"

#include <SALOMEconfig.h>
#include CORBA_CLIENT_HEADER(SALOMEDS)
#include CORBA_CLIENT_HEADER(SALOMEDS_Attributes)

#include <Utils_ExceptHandlers.hxx>

#include <string>

namespace {
    static std::string studyName(const std::string& name)
    {
        std::string fullName = "/:sat:{CPPCMP}/";
        fullName += name;
        return fullName;
    }
}

/*!
  \brief Constructor

  Creates an instance of the :sat:{CPPCMP} component engine

  \param orb reference to the ORB
  \param poa reference to the POA
  \param contId CORBA object ID, pointing to the owner SALOME container
  \param instanceName SALOME component instance name
  \param interfaceName SALOME component interface name
*/
:sat:{CPPCMP}:::sat:{CPPCMP}(CORBA::ORB_ptr orb,
          PortableServer::POA_ptr poa,
          PortableServer::ObjectId* contId,
          const char* instanceName,
          const char* interfaceName)
    : Engines_Component_i(orb, poa, contId, instanceName, interfaceName)
{
    _thisObj = this;
    _id = _poa->activate_object(_thisObj); // register and activate this servant object
}

/*!
  \brief Destructor

  Clean up allocated resources
*/
:sat:{CPPCMP}::~:sat:{CPPCMP}()
{
  // nothing to do
}

/*!
  \brief Say hello to \a name
  \param study SALOME study
  \param name person's name
  \return operation status
*/
:sat:{CPPCMP}_ORB::status :sat:{CPPCMP}::hello(SALOMEDS::Study_ptr study, const char* name)
{
    // set exception handler to catch unexpected CORBA exceptions
    Unexpect aCatch(SALOME_SalomeException);

    // set result status to error initially
    :sat:{CPPCMP}_ORB::status result = :sat:{CPPCMP}_ORB::OP_ERR_UNKNOWN;

    // check if reference to study is valid
    if (!CORBA::is_nil(study))
    {
        // get full object path
        std::string fullName = studyName(name);
        // check if the object with the same name is already registered in the study
        SALOMEDS::SObject_var sobj = study->FindObjectByPath(fullName.c_str());
        if (!CORBA::is_nil(sobj))
        {
            // person is already registered in the study -> ERROR
            result = :sat:{CPPCMP}_ORB::OP_ERR_ALREADY_MET;
        }
        else
        {
            // person is not registered yet -> register
            SALOMEDS::StudyBuilder_var     studyBuilder   = study->NewBuilder();          // study builder
            SALOMEDS::UseCaseBuilder_var   useCaseBuilder = study->GetUseCaseBuilder();   // use case builder

            // find :sat:{CPPCMP} component; create it if not found
            SALOMEDS::SComponent_var father = study->FindComponent(":sat:{CPPCMP}");
            if (CORBA::is_nil(father))
            {
                // create component
                father = studyBuilder->NewComponent(":sat:{CPPCMP}");
                // set name attribute
                father->SetAttrString("AttributeName", ":sat:{CPPCMP}");
                // set icon attribute
                father->SetAttrString("AttributePixMap", "ICON_HELLO");
                // register component in the study
                studyBuilder->DefineComponentInstance(father, :sat:{CPPCMP}_Gen::_this());
                // add component to the use case tree
                // (to support tree representation customization and drag-n-drop)
                useCaseBuilder->SetRootCurrent();
                useCaseBuilder->Append(father); // component object is added as the top level item
            }

            // create new sub-object, as a child of the component object
            sobj = studyBuilder->NewObject(father);
            sobj->SetAttrString("AttributeName", name);
            // add object to the use case tree
            // (to support tree representation customization and drag-n-drop)
            useCaseBuilder->AppendTo(father, sobj);

            // cleanup
            father->UnRegister();
            sobj->UnRegister();

            // set operation status
            result = :sat:{CPPCMP}_ORB::OP_OK;
        }
    }

    // return result of the operation
    return result;
}

/*!
  \brief Say goodbye to \a name
  \param study SALOME study
  \param name person's name
  \return operation status
*/
:sat:{CPPCMP}_ORB::status :sat:{CPPCMP}::goodbye(SALOMEDS::Study_ptr study, const char* name)
{
    // set exception handler to catch unexpected CORBA exceptions
    Unexpect aCatch(SALOME_SalomeException);

    // set result status to error initially
    :sat:{CPPCMP}_ORB::status result = :sat:{CPPCMP}_ORB::OP_ERR_UNKNOWN;

    // check if reference to study is valid
    if (!CORBA::is_nil(study))
    {
        // get full object path
        std::string fullName = studyName(name);

        // initially set error status: person is not registered
        result = :sat:{CPPCMP}_ORB::OP_ERR_DID_NOT_MEET;

        // check if the object with the same name is registered in the study
        // find all objects with same name
        SALOMEDS::StudyBuilder_var studyBuilder = study->NewBuilder();            // study builder
        SALOMEDS::UseCaseBuilder_var useCaseBuilder = study->GetUseCaseBuilder(); // use case builder
        SALOMEDS::SObject_var sobj = study->FindObjectByPath(fullName.c_str());
        while (!CORBA::is_nil(sobj))
        {
            std::list<SALOMEDS::SObject_var> toRemove;
            toRemove.push_back(sobj);
            SALOMEDS::UseCaseIterator_var useCaseIt = useCaseBuilder->GetUseCaseIterator(sobj); // use case iterator
            for (useCaseIt->Init(true); useCaseIt->More(); useCaseIt->Next())
                toRemove.push_back(useCaseIt->Value());

            // perform removing of all found objects (recursively with children)
            std::list<SALOMEDS::SObject_var>::const_iterator it;
            for(it = toRemove.begin(); it != toRemove.end(); ++it)
            {
                sobj = *it;
                // remove object from the study
                // - normally it's enough to call RemoveObject() method
                // RemoveObject`WithChildren() also removes all children recursively if there are any
                // - it's not necessary to remove it from use case builder, it is done automatically
                studyBuilder->RemoveObjectWithChildren(sobj);

                // cleanup
                sobj->UnRegister();

                // set operation status to OK as at least one object is removed
                result = :sat:{CPPCMP}_ORB::OP_OK;
            }

            sobj = study->FindObjectByPath(fullName.c_str());
        }
    }

    // return result of the operation
    return result;
}

/*!
  \brief Copy or move objects to the specified position

  This function is used in the drag-n-drop functionality.

  \param what objects being copied/moved
  \param where parent object where objects are copied/moved to
  \param row position in the parent object's children list at which objects are copied/moved
  \param isCopy \c true if object are copied or \c false otherwise
*/
void :sat:{CPPCMP}::copyOrMove(const :sat:{CPPCMP}_ORB::object_list& what,
            SALOMEDS::SObject_ptr where,
            CORBA::Long row, CORBA::Boolean isCopy)
{
    if (CORBA::is_nil(where)) return; // bad parent

    SALOMEDS::Study_var study = where->GetStudy();                               // study
    SALOMEDS::StudyBuilder_var studyBuilder = study->NewBuilder();               // study builder
    SALOMEDS::UseCaseBuilder_var useCaseBuilder = study->GetUseCaseBuilder();    // use case builder
    SALOMEDS::SComponent_var father = where->GetFatherComponent();               // father component
    std::string dataType = father->ComponentDataType();
    if (dataType != ":sat:{CPPCMP}") return; // not a :sat:{CPPCMP} component

    SALOMEDS::SObject_var objAfter;
    if (row >= 0 && useCaseBuilder->HasChildren(where))
    {
        // insert at given row -> find insertion position
        SALOMEDS::UseCaseIterator_var useCaseIt = useCaseBuilder->GetUseCaseIterator(where);
        int i;
        for (i = 0; i < row && useCaseIt->More(); i++, useCaseIt->Next());
        {
            if (i == row && useCaseIt->More())
                objAfter = useCaseIt->Value();
        }
    }

    for (int i = 0; i < what.length(); i++)
    {
        SALOMEDS::SObject_var sobj = what[i];
        if (CORBA::is_nil(sobj)) continue; // skip bad object

        if (isCopy)
        {
            // copying is performed
            // get name of the object
            CORBA::String_var name = sobj->GetName();
            // create new object, as a child of the component object
            SALOMEDS::SObject_var new_sobj = studyBuilder->NewObject(father);
            new_sobj->SetAttrString("AttributeName", name.in());
            sobj = new_sobj;
        }

        // insert the object or its copy to the use case tree
        if (!CORBA::is_nil(objAfter))
            useCaseBuilder->InsertBefore(sobj, objAfter); // insert at given row
        else
            useCaseBuilder->AppendTo(where, sobj);        // append to the end of list
    }
}

// Version information
char* :sat:{CPPCMP}::getVersion()
{
#if :sat:{CPPCMP}_DEVELOPMENT
    return CORBA::string_dup(:sat:{CPPCMP}_VERSION_STR"dev");
#else
    return CORBA::string_dup(:sat:{CPPCMP}_VERSION_STR);
#endif
}

extern "C"
{
    /*!
      \brief Exportable factory function: create an instance of the :sat:{CPPCMP} component engine
      \param orb reference to the ORB
      \param poa reference to the POA
      \param contId CORBA object ID, pointing to the owner SALOME container
      \param instanceName SALOME component instance name
      \param interfaceName SALOME component interface name
      \return CORBA object identifier of the registered servant
    */
    PortableServer::ObjectId* :sat:{CPPCMP}Engine_factory(CORBA::ORB_ptr orb,
                         PortableServer::POA_ptr poa,
                         PortableServer::ObjectId* contId,
                         const char* instanceName,
                         const char* interfaceName)
    {
        :sat:{CPPCMP}* component = new :sat:{CPPCMP}(orb, poa, contId, instanceName, interfaceName);
        return component->getId();
    }
}
