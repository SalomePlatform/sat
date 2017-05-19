#!/usr/bin/env python
#-*- coding:utf-8 -*-

# CEA/LGLS 2007-2008, Francis KLOSS (OCC)
# =======================================

# Caractériser le cas VER pour Pléïades
# -------------------------------------

# La géométrie d'un combustible à particules est définie par:
#   - un cube représentant une partie du combustible,
#   - ce cube contenant des éléments, ces éléments représentent les particules.
# Chaque élément est constitué d'une écorce sphérique contenant un noyau sphérique et concentrique.
# La matrice est le cube d'ou sont exclus tous les éléments.

# Les relations entre le cube et les éléments sont:
#   - pas d'intersection entre les éléments entre-eux (tolérance),
#   - un élément peut ne pas intersecter le cube (tolérance),
#   - un élément peut intersecter un sommet unique du cube et avec uniquement les 3 arêtes et les 3 faces reliés à ce sommet,
#   - un élément peut intersecter une arête unique du cube et avec uniquement les 2 faces reliées à cette arête (et sans sommet),
#   - un élément peut intersecter une face  unique du cube (et sans sommet, ni arête).

# De plus, toutes les intersections sont:
#   - sans aucun cas de tangence (tolérance),
#   - si un élément est coupé par une face, alors son noyau est aussi coupé par cette même face.

# Si un élément touche le cube, alors les éléments symétriques sont créés automatiquement.

# Les faces en vis à vis du cube sont maillées de manière identique afin d'assurer la périodicité.
# La matrice et les noyaux sont maillés avec des tétraèdres, et les écorces sont maillées avec des prismes.

# Les groupes 2D à constituer sont:
#   - les 6 groupes correspondant aux 6 faces du cube (triangles et quadrangles),
#   - pour chaque noyau , avoir un groupe de son enveloppe (triangles),
#   - pour chaque écorce, avoir un groupe de son enveloppe (triangles),
#   - le groupe de l'ensemble des enveloppes de tous les noyaux,
#   - le groupe de l'ensemble des enveloppes de toutes les écorces.

# Les groupes 3D à constituer sont:
#   - un groupe pour la matrice (tétraèdres),
#   - pour chaque noyau , avoir un groupe (tétraèdres),
#   - pour chaque écorce, avoir un groupe (couches de prismes),
#   - le groupe de l'ensemble des noyaux,
#   - le groupe de l'ensemble des écorces.

# Mode d'emploi
# -------------

# Pour créer une étude avec ce fichier python,
# il faut créer un fichier contenant la ligne "import ver", puis:
#   - construire une géométrie,
#   - mailler cette géométrie.

# Pour construire une géométrie, il y a 2 étapes:
#   - construire le cube,
#   - construire les éléments.

# Pour construire le cube, il y a 4 manières différentes:
#   - cas_1 = ver.geometrie()
#   - cas_2 = ver.geometrie("cas")
#   - cas_3 = ver.geometrie("kas", 200)
#   - cas_4 = ver.geometrie("qua", 400, 1)

# La description des 3 paramètres est dans l'ordre:
#   - le nom de la géométrie (par défaut: "VER"),
#   - le coté du cube        (par défaut: 100),
#   - la tolérance           (par défaut: 1).

# Pour construire les éléments, il existe 2 fonctions de base:
#   - element,
#   - elements.

# Pour construire un élement précis, la fonction "element" a pour syntaxe:
#   status = cas_2.element(x, y, z,  nr, er)
#   - x, y, z : les coordonnées du centre de l'élément,
#   - nr      : rayon du noyau,
#   - er      : rayon de l'élément,
#   - status  : vaut True  quand l'élément est correct (respect de la tolérance, pas de collision et coupe du noyau si nécessaire),
#               vaut False quand l'élément n'est pas correct et dans ce cas, il n'est pas construit dans le géométrie.

# Pour effectuer un tirage aléatoire d'éléments, la fonction "elements" a 2 syntaxes:
#   cas_4.elements(sommet, arete, face, solide,  rmin, rmax)
#   cas_4.elements(sommet, arete, face, solide,  rmin, rmax, ratio)
#   - sommet : booléen pour indiquer si l'on veut couper le sommet du cube,
#   - arete  : nombre d'éléments à générer coupant une arête,
#   - face   : nombre d'éléments à générer coupant une face,
#   - solide : nombre d'éléments à générer ne coupant pas le cube,
#   - rmin   : rayon minimum pour le noyau,
#   - rmax   : rayon minimum pour l'élément,
#   - ratio  : a pour valeur par défaut 0.5 et permet de borner le rayon maximun du noyau selon la formule: rmin + (rmax-rmin)*ratio.
# Nota: dans le cas des paramètres "arete" et "face", les éléments symétriques générés automatiquement ne compte pas.

# Il existe quelques méthodes complémentaires sur la géométrie:
#   - n = cas_1.nom()       donne le nom de la géométrie,
#   - c = cas_2.cote()      donne le coté du cube,
#   - t = cas_3.tolerance() donne la tolérance,
#   - b = cas_0.infos()     dit si des traces sont affichées ou pas,
#   - cas_0.infos(bool)     affiche ou pas des traces lors du traitement (par défaut: pas de traces),
#   - s = cas_4.obtenir()   donne la shape correspondant à la géométrie,
#   - cas_1.valeurs()       donne les caractéristiques de tous les éléments ou:
#                           le résultat est de la forme: [ [<solide>, ...], [<face>, ...], [<arête>, ...], [<sommmet>, ...] ],
#                           avec <solide> pour un élément inclus dans le cube,
#                           avec <face>   pour un élément qui coupe une face  du cube,
#                           avec <arête>  pour un élément qui coupe une arête du cube,
#                           avec <sommet> pour un élément qui coupe un sommet du cube,
#                           et chaque élément est une liste de la forme [ x-centre, y-centre, z-centre,  rayon-noyau, rayon-ecorce ],
#   - cas_2.sauver()        sauve la géométrie au format BREP dans le répertoire courant,
#   - cas_3.sauver(rep)     sauve la géométrie au format BREP dans le répertoire passé en argument,
#   - cas_6.tous()          donne tous les éléments englobants sans tenir compte des éventuelles intersections.

# Pour mailler une géométrie, il faut utiliser la fonction "maillage":
#   mesh = ver.maillage(cas_3)
#   - cas_3 est une géométrie définie comme ci-avant,
#   - mesh est la définition du maillage de cette géometrie.

# Avant de générer le maillage, il est possible de donner les différentes options suivantes:
#   - mesh.longueur(4)     permet de donner la longueur moyenne des cotés des triangles            (défaut: 20),
#   - mesh.couches(5)      permet de donner le nombre de couche de prismes pour toutes les écorces (défaut:  2),
#   - mesh.fichier("file") permet de sauver automatiquement le maillage dans ce fichier            (défaut: "" (soit pas de fichier)).

# Pour connaitre les valeurs des options, il suffit de réaliser les appels suivants:
#   - mesh.longueur() permet d'obtenir la longueur moyenne des cotés des triangles,
#   - mesh.couches()  permet d'obtenir le nombre de couche de prismes pour toutes les écorces,
#   - mesh.fichier()  permet d'obtenir le fichier correspondant au maillage (si "" alors soit pas de fichier).

# Pour générer le maillage et ses groupes paramétré par ses éventuelles options, il suffit de faire:
#   - mesh.generer()

# Il est possible de sauver le maillage après génération:
#   - mesh.sauver(fichier)

# Voir aussi des exemples programmés dans le fichier ver_exemples.py

# Importer
# --------

import math
import random
import string

import geompy
import smesh

geo = geompy

# Définir des constantes
# ----------------------

random.seed(0)


#######################
angle_e   = math.pi/90
angle_ee   = math.pi/180


angle_30  = math.pi/6
angle_45  = math.pi/4
angle_60  = math.pi/3
angle_90  = math.pi/2
angle_120 = angle_60*2
angle_135 = angle_45*3
angle_180 = math.pi
angle_360 = math.pi*2

geo_origine = geo.MakeVertex(0, 0, 0)

geo_vertex = geo.ShapeType["VERTEX"]
geo_edge   = geo.ShapeType["EDGE"]
geo_wire   = geo.ShapeType["WIRE"]
geo_face   = geo.ShapeType["FACE"]
geo_shell  = geo.ShapeType["SHELL"]
geo_solid  = geo.ShapeType["SOLID"]

# Définir la géométrie
# ====================

class geometrie:

    # Initialiser
    # -----------

    def __init__(self, nom="VER", cote=100, tolerance=1, mox="mox"):
        self.nom(nom)
        self.tolerance(tolerance)
        self.cote(cote)
        self.infos(False)

        self.element_solides([])
        self.element_faces([])
        self.element_aretes([])
        self.element_sommets([])

        self._shape = None
        self._tous  = []

        self.nom_noyau   = "noy"
        self.nom_ecorce  = "eco"
        self.nom_matrice = "mat"
        self.nom_xy      = "xy"
        self.nom_xz      = "xz"
        self.nom_yz      = "yz"
        self.nom_coupees = "coupe"
        self._type = mox


    # Donner le nom du combustible
    # ---------------------

    def type_comb(self, type=None):
        if type!=None:
            self._type = type

        return self._type



    # Donner le nom du cube
    # ---------------------

    def nom(self, nom=None):
        if nom!=None:
            self._nom = nom

        return self._nom

    # Donner la tolérance
    # -------------------

    def tolerance(self, t=None):
        if t!=None:
            self._tolerance = t

        return self._tolerance

    # Donner le coté du cube
    # ----------------------

    def cote(self, c=None):
        if c!=None:
            self._cote = c

            self._boite_e = geo.MakeBox(0, 0, 0,  c, c, c)
            mi = -c/1000.
            ma = c-mi
            self._boite_t = geo.MakeBox(mi, mi, mi,  ma, ma, ma)

            self.axe_x = geo.MakeVectorDXDYDZ(c, 0, 0)
            self.axe_y = geo.MakeVectorDXDYDZ(0, c, 0)
            self.axe_z = geo.MakeVectorDXDYDZ(0, 0, c)

        return self._cote

    # Donner tous les éléments englobants sans tenir compte des intersections
    # -----------------------------------------------------------------------

    def tous(self, x=None, y=None, z=None, r=None):
        if x==None:
            t = geo.MakeCompound(self._tous)
            geo.addToStudy(t, self.nom() + ":tous")
            return t
        else:
            s = geo.MakeSphere(x, y, z, r)
            self._tous.append(s)

    # Tracer ou pas des messages
    # --------------------------

    def infos(self, b=None):
        if b!=None:
            self._infos = b

        return self._infos

    # Donner la boite
    # ---------------

    def boite(self, b=True):
        if b:
            return self._boite_e
        else:
            return self._boite_t

    # Donner les valeurs caractérisant tous les éléments
    # --------------------------------------------------

    def valeurs(self):
        sol = []
        fac = []
        are = []
        som = []

        for c, nr, er,  ax, an in self.element_solides():
            x, y, z = geo.PointCoordinates(c)
            sol.append( [x, y, z,  nr, er] )

        for c, nr, er,  ax, an in self.element_faces():
            x, y, z = geo.PointCoordinates(c)
            fac.append( [x, y, z,  nr, er] )

        for c, nr, er,  ax, an in self.element_aretes():
            x, y, z = geo.PointCoordinates(c)
            are.append( [x, y, z,  nr, er] )

        for c, nr, er,  ax, an in self.element_sommets():
            x, y, z = geo.PointCoordinates(c)
            som.append( [x, y, z,  nr, er] )

        return [ sol, fac, are, som ]

    # Calculer l'union de 2 listes
    # ----------------------------

    def union(self, a, b):
        r = b
        for e in a:
            if not (e in r):
                r.append(e)

        return r

    # Calculer l'intersection de 2 listes
    # -----------------------------------

    def intersection(self, a, b):
        r = []
        for e in a:
            if e in b:
                r.append(e)

        return r

    # Calculer la différence de 2 listes
    # ----------------------------------

    def difference(self, a, b):
        r = []
        for e in a:
            if not (e in b):
                r.append(e)

        return r

    # Calculer la distance entre 2 points
    # -----------------------------------

    def distance(self, x1, y1, z1,  p):
        x2, y2, z2 = geo.PointCoordinates(p)

        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1

        return math.sqrt(dx*dx + dy*dy + dz*dz)

    # Dire si un edge est dégénéré
    # ----------------------------

    def edge_degenere(self, e):
        return geo.KindOfShape(e) == [geo.kind.EDGE, 1]

    # Récupérer une shape ou une liste de shape à partir d'un ID ou d'une liste d'IDs
    # -------------------------------------------------------------------------------

    def donner_shapes(self, l):
        if type(l)==type(0):
            return geo.GetSubShape(self._shape, [l])

        r = []
        for i in l:
            s = geo.GetSubShape(self._shape, [i])
            r.append(s)

        return r

    # Dire si 2 points sont identiques
    # --------------------------------

    def point_egal(self, v1, v2):
        t = self.tolerance()*0.01

        if ( type(v1)==type([]) ) or ( type(v1)==type(()) ):
            x1, y1, z1 = v1
        else:
            x1, y1, z1 = geo.PointCoordinates(v1)

        if ( type(v2)==type([]) ) or ( type(v2)==type(()) ):
            x2, y2, z2 = v2
        else:
            x2, y2, z2 = geo.PointCoordinates(v2)

        return ( abs(x1-x2)<t ) and ( abs(y1-y2)<t ) and ( abs(z1-z2)<t )

    # Définir les éléments géométriques de la shape
    # =============================================

    # Déterminer l'élément symétrique
    # -------------------------------

    def element_symetrique(self, ix, iy, iz,  x1, y1, z1):
        if ix==1:
            x2 = x1 + self.cote()
        else:
            x2 = x1 - self.cote()

        if iy==1:
            y2 = y1 + self.cote()
        else:
            y2 = y1 - self.cote()

        if iz==1:
            z2 = z1 + self.cote()
        else:
            z2 = z1 - self.cote()

        return x2, y2, z2

    # Dire si le nouvel élément intersecte les autres éléments déjà choisis
    # ---------------------------------------------------------------------

    def element_intersecter(self, x, y, z, r):
        rt = r + self.tolerance()

        for c, nr, er,  ax, an in self.element_solides():
            if self.distance(x, y, z,  c) < (rt + er):
                return True

        for c, nr, er,  ax, an in self.element_faces():
            if self.distance(x, y, z,  c) < (rt + er):
                return True

        for c, nr, er,  ax, an in self.element_aretes():
            if self.distance(x, y, z,  c) < (rt + er):
                return True

        for c, nr, er,  ax, an in self.element_sommets():
            if self.distance(x, y, z,  c) < (rt + er):
                return True

        return False

    # Ajouter un élément, s'il n'en intersecte aucun autre
    # ----------------------------------------------------

    def ajouter(self, r, l,  x, y, z,  nr, er,  ax=None, an=None):
        self.tous(x, y, z, er)
        if self.infos():
            print "VER: x = ", x, ", y = ", y, " , z = ", z, " , nr = ", nr, " , er = ", er

        b, n = r
        if b:
            if self.element_intersecter(x, y, z, er):
                if n!=0:
                    del l[-n:]
                return [False, 0]
            else:
                c = geo.MakeVertex(x, y, z)
                l.append( [c, nr, er, ax, an] )
                return [True, n+1]
        else:
            return r

    # Donner les sphères entières
    # ---------------------------

    def element_solides(self, l=None):
        if l!=None:
            self._solides = l

        return self._solides

    # Ajouter une sphère entière
    # --------------------------

    def element_solide(self, x, y, z,  nr, er):
        r = [True, 0]
        r = self.ajouter(r, self._solides,  x, y, z,  nr, er)

        return r[0]

    # Donner les sphères coupées par une face
    # ---------------------------------------

    def element_faces(self, l=None):
        if l!=None:
            self._faces = l

        return self._faces

    # Ajouter une sphère coupée par une face avec sa symétrique
    # ---------------------------------------------------------

    def element_face(self, ix, iy, iz,  x1, y1, z1,  nr, er):
        r = [True, 0]
        x2, y2, z2 = self.element_symetrique(ix, iy, iz,  x1, y1, z1)

        if ix!=0:
            r = self.ajouter(r, self._faces,  x1, y1, z1,  nr, er,  self.axe_x, -angle_45)
            r = self.ajouter(r, self._faces,  x2, y1, z1,  nr, er,  self.axe_x, -angle_45)

        elif iy!=0:
            if iy==1:
                a = -angle_90
            else:
                a = +angle_90

            r = self.ajouter(r, self._faces,  x1, y1, z1,  nr, er, [self.axe_z, self.axe_y], [a, -angle_45])
            r = self.ajouter(r, self._faces,  x1, y2, z1,  nr, er, [self.axe_z, self.axe_y], [a, -angle_45])

        else:
            r = self.ajouter(r, self._faces,  x1, y1, z1,  nr, er, [self.axe_y, self.axe_z], [-angle_90, -angle_45])
            r = self.ajouter(r, self._faces,  x1, y1, z2,  nr, er, [self.axe_y, self.axe_z], [-angle_90, -angle_45])

        return r[0]

    # Calculer l'angle de rotation
    # ----------------------------

    def element_angle(self, x, y, z, v, nr, er):
        b = self.boite(False)

        if v==self.axe_z:
            s = geo.MakeVertex(x   , y-er, z)
            m = geo.MakeVertex(x+er, y   , z)
            e = geo.MakeVertex(x   , y+er, z)
        elif v==self.axe_y:
            s = geo.MakeVertex(x, y, z+er)
            m = geo.MakeVertex(x+er, y, z)
            e = geo.MakeVertex(x, y, z-er)
        else:
            s = geo.MakeVertex(x, y   , z+er)
            m = geo.MakeVertex(x, y+er, z   )
            e = geo.MakeVertex(x, y   , z-er)

        c  = geo.MakeVertex(x, y, z)
        a1 = geo.MakeArc(s, m, e)
        a2 = geo.MakeScaleTransform(a1, c, nr/er)
        as_compound = geo.MakeCompound([a1, a2])

        an = angle_ee
        print " an1 : ", an
        ax = geo.MakeLine(c, v)
        ro = geo.MakeRotation(as_compound, ax, an)
        pa = geo.MakePartition([b], [ro], [], [], geo_vertex)

        i = 1
        n = 1800
        while (( len(geo.SubShapeAll(pa, geo_vertex))!=8 ) and ( i<=n )):
            if self.infos() and ( (i%int(n/10)) == 0 ):
                print " (i%int(n/10)", (i%int(n/10))
                print "VER: echantillon: nombre de vertex = ", len(geo.SubShapeAll(pa, geo_vertex))
            an = an + angle_ee
            #an = random.uniform(0, angle_360)
            ro = geo.MakeRotation(as_compound, ax, an)
            pa = geo.MakePartition([b], [ro], [], [], geo_vertex)
            i = i + 1
        print "VER: echantillon: nombre de vertex = ", len(geo.SubShapeAll(pa, geo_vertex))
        if i==n+1 :
            print "WARNING: element_angle: nombre d'essai: ", n            
        print " an2 : ", an
        geo.addToStudy(pa, " pa" )
        geo.addToStudy(as_compound, " as" )
        geo.addToStudy(ro, " ro" )

        return an

    # Donner les sphères coupées par une arête
    # ----------------------------------------

    def element_aretes(self, l=None):
        if l!=None:
            self._aretes = l

        return self._aretes

    # Ajouter une sphère coupée par une arête et ses 3 autres symétriques
    # -------------------------------------------------------------------

    def element_arete(self, ix, iy, iz,  x1, y1, z1,  nr, er):
        r = [True, 0]
        x2, y2, z2 = self.element_symetrique(ix, iy, iz,  x1, y1, z1)

        if iz==0:
            a1 = self.element_angle(x1, y1, z1, self.axe_z, nr, er)
            a2 = self.element_angle(x1, y2, z1, self.axe_z, nr, er)
            a3 = self.element_angle(x2, y1, z1, self.axe_z, nr, er)
            a4 = self.element_angle(x2, y2, z1, self.axe_z, nr, er)

            r = self.ajouter(r, self._aretes,  x1, y1, z1,  nr, er,  [self.axe_x, self.axe_z], [angle_90, a1])
            r = self.ajouter(r, self._aretes,  x1, y2, z1,  nr, er,  [self.axe_x, self.axe_z], [angle_90, a2])
            r = self.ajouter(r, self._aretes,  x2, y1, z1,  nr, er,  [self.axe_x, self.axe_z], [angle_90, a3])
            r = self.ajouter(r, self._aretes,  x2, y2, z1,  nr, er,  [self.axe_x, self.axe_z], [angle_90, a4])

        elif iy==0:
            a1 = self.element_angle(x1, y1, z1, self.axe_y, nr, er)
            a2 = self.element_angle(x1, y1, z2, self.axe_y, nr, er)
            a3 = self.element_angle(x2, y1, z1, self.axe_y, nr, er)
            a4 = self.element_angle(x2, y1, z2, self.axe_y, nr, er)

            r = self.ajouter(r, self._aretes,  x1, y1, z1,  nr, er,  self.axe_y, a1)
            r = self.ajouter(r, self._aretes,  x1, y1, z2,  nr, er,  self.axe_y, a2)
            r = self.ajouter(r, self._aretes,  x2, y1, z1,  nr, er,  self.axe_y, a3)
            r = self.ajouter(r, self._aretes,  x2, y1, z2,  nr, er,  self.axe_y, a4)

        else:
            a1 = self.element_angle(x1, y1, z1, self.axe_x, nr, er)
            a2 = self.element_angle(x1, y1, z2, self.axe_x, nr, er)
            a3 = self.element_angle(x1, y2, z1, self.axe_x, nr, er)
            a4 = self.element_angle(x1, y2, z2, self.axe_x, nr, er)

            r = self.ajouter(r, self._aretes,  x1, y1, z1,  nr, er,  [self.axe_z, self.axe_x], [angle_90, a1])
            r = self.ajouter(r, self._aretes,  x1, y1, z2,  nr, er,  [self.axe_z, self.axe_x], [angle_90, a2])
            r = self.ajouter(r, self._aretes,  x1, y2, z1,  nr, er,  [self.axe_z, self.axe_x], [angle_90, a3])
            r = self.ajouter(r, self._aretes,  x1, y2, z2,  nr, er,  [self.axe_z, self.axe_x], [angle_90, a4])

        return r[0]

    # Donner les sphères coupées par un sommet
    # ----------------------------------------

    def element_sommets(self, l=None):
        if l!=None:
            self._sommets = l

        return self._sommets

    # Ajouter une sphère coupée par un sommet et ses 7 autres symétriques
    # -------------------------------------------------------------------

    def element_sommet(self, ix, iy, iz,  x1, y1, z1,  nr, er):
        r = [True, 0]
        x2, y2, z2 = self.element_symetrique(ix, iy, iz,  x1, y1, z1)

        if ( ix==1 and iz==1 ) or ( ix==2 and iz==2 ):
            a = angle_135
            b = angle_45
        else:
            a = angle_45
            b = angle_135

        r = self.ajouter(r, self._sommets,  x1, y1, z1,  nr, er,  self.axe_y, +a)
        r = self.ajouter(r, self._sommets,  x1, y1, z2,  nr, er,  self.axe_y, -a)
        r = self.ajouter(r, self._sommets,  x1, y2, z1,  nr, er,  self.axe_y, +a)
        r = self.ajouter(r, self._sommets,  x1, y2, z2,  nr, er,  self.axe_y, -a)

        r = self.ajouter(r, self._sommets,  x2, y1, z1,  nr, er,  self.axe_y, +b)
        r = self.ajouter(r, self._sommets,  x2, y1, z2,  nr, er,  self.axe_y, -b)
        r = self.ajouter(r, self._sommets,  x2, y2, z1,  nr, er,  self.axe_y, +b)
        r = self.ajouter(r, self._sommets,  x2, y2, z2,  nr, er,  self.axe_y, -b)

        return r[0]

    # Dire si l'élément touche le cube
    # --------------------------------

    def element_toucher(self, x, r):
        if x < r:
            return 1
        elif x > (self.cote()-r):
            return 2
        else:
            return 0

    # Définir un élément dans un cube qui ne touchent les éléments déjà définis, retourne True si l'élément a été créé
    # ----------------------------------------------------------------------------------------------------------------

    def element(self, x, y, z,  nr, er):
        x  = float(x)
        y  = float(y)
        z  = float(z)
        nr = float(nr)
        er = float(er)

        ix = self.element_toucher(x, er)
        iy = self.element_toucher(y, er)
        iz = self.element_toucher(z, er)

        if (ix==0) and (iy==0) and (iz==0):
            return self.element_solide(x, y, z,  nr, er)

        if (ix!=0) and (iy!=0) and (iz!=0):
            return self.element_sommet(ix, iy, iz,  x, y, z,  nr, er)

        if ( (ix==0) and (iy==0) ) or ( (ix==0) and (iz==0) ) or ( (iy==0) and (iz==0) ):
            return self.element_face(ix, iy, iz,  x, y, z,  nr, er)

        return self.element_arete(ix, iy, iz,  x, y, z,  nr, er)

    # Choisir les rayons de l'élément
    # -------------------------------

    def element_choisir_rayons(self, rmin, rmax, ratio):
        t = self.tolerance()

        nr = random.uniform(rmin, rmin+ratio*(rmax-rmin)-t)
        er = random.uniform(nr+t, rmax)

        mi = er + t
        ma = self.cote() - mi

        r = random.uniform(0, nr-t*2)
        a = random.uniform(0, angle_360)

        return nr, er,  mi, ma,  r, a

    # Choisir un nouvel élément qui coupe un sommet
    # ---------------------------------------------

    def element_choisir_sommet(self, rmin, rmax, ratio):
        nr, er,  mi, ma,  r, a = self.element_choisir_rayons(rmin, rmax, ratio)

        x = random.uniform(-r, +r)
        s = math.sqrt(r*r - x*x)
        y = s * math.cos(a)
        z = s * math.sin(a)

        return x, y, z,  nr, er

    # Choisir un nouvel élément qui coupe une arête
    # ---------------------------------------------

    def element_choisir_arete(self, rmin, rmax, ratio):
        nr, er,  mi, ma,  r, a = self.element_choisir_rayons(rmin, rmax, ratio)

        d = random.randint(1, 3)

        if d==1:
            x = random.uniform(mi, ma)
            y = r * math.cos(a)
            z = r * math.sin(a)
        elif d==2:
            y = random.uniform(mi, ma)
            x = r * math.cos(a)
            z = r * math.sin(a)
        else:
            z = random.uniform(mi, ma)
            x = r * math.cos(a)
            y = r * math.sin(a)

        return x, y, z,  nr, er

    # Choisir un nouvel élément qui coupe une face
    # --------------------------------------------

    def element_choisir_face(self, rmin, rmax, ratio):
        nr, er,  mi, ma,  r, a = self.element_choisir_rayons(rmin, rmax, ratio)

        d = random.randint(1, 3)

        if d==1:
            x = random.uniform(mi, ma)
            y = random.uniform(mi, ma)
            z = random.uniform(-r, +r)
        elif d==2:
            x = random.uniform(mi, ma)
            y = random.uniform(-r, +r)
            z = random.uniform(mi, ma)
        else:
            x = random.uniform(-r, +r)
            y = random.uniform(mi, ma)
            z = random.uniform(mi, ma)

        return x, y, z,  nr, er

    # Choisir un nouvel élément qui ne coupe pas le cube
    # --------------------------------------------------

    def element_choisir_solide(self, rmin, rmax, ratio):
        nr, er,  mi, ma,  r, a = self.element_choisir_rayons(rmin, rmax, ratio)

        x = random.uniform(mi, ma)
        y = random.uniform(mi, ma)
        z = random.uniform(mi, ma)

        return x, y, z,  nr, er

    # Choisir de nouveaux éléments
    # ----------------------------

    def elements_choisir(self, choisir, n,  rmin, rmax, ratio):
        i = 0
        while i<n:
            x, y, z,  nr, er = choisir(rmin, rmax, ratio)
            if self.element(x, y, z,  nr, er):
                i = i + 1

    # Construire automatiquement des éléments
    # ---------------------------------------

    def elements(self, s, na, nf, ns,  rmin, rmax, ratio=0.5):
        self.elements_choisir(self.element_choisir_sommet, int(s), rmin, rmax, ratio)
        self.elements_choisir(self.element_choisir_arete , na    , rmin, rmax, ratio)
        self.elements_choisir(self.element_choisir_face  , nf    , rmin, rmax, ratio)
        self.elements_choisir(self.element_choisir_solide, ns    , rmin, rmax, ratio)

    # Définir la shape
    # ================

    # Construire un élément qui coupe une face
    # ----------------------------------------

    def construire_element_face(self, c, nr, er,  ax, an,  n, e):
        if ax==self.axe_x:
            a = self.axe_y
            b = self.axe_z
        elif ax==self.axe_y:
            a = self.axe_x
            b = self.axe_z
        else:
            a = self.axe_x
            b = self.axe_y

        l = 4*self.cote()
        p = geo.MakePlane(c, a, l)
        q = geo.MakePlane(c, b, l)
        s = geo.MakePartition([e, n], [p, q], [], [], geo_solid)

        o = False
        for e in geo.SubShapeAll(s, geo_solid):
            k = string.split(geo.WhatIs(e))
            print "k cas HTR", k
            if (int(k[6])==6) and (int(k[9])==9) and (int(k[15])==5):
                o = True
                break

        if not o:
            raise "construire_element_face"

        a = geo.MakeLine(c, ax)
        f = geo.MakeRotation(e, a, +angle_90)
        g = geo.MakeRotation(e, a, -angle_90)
        h = geo.MakeMirrorByAxis(e, a)

        return [e, f, g, h]


    # Construire un élément qui coupe une face sans couches(mox)
    # ---------------------------------------------------------

    def construire_element_face_mox(self, c, nr, er,  ax, an, e):
        if ax==self.axe_x:
            a = self.axe_y
            b = self.axe_z
        elif ax==self.axe_y:
            a = self.axe_z
            b = self.axe_x
        else:
            a = self.axe_x
            b = self.axe_y

        l = 4*self.cote()
        p = geo.MakePlane(c, a, l)
        q = geo.MakePlane(c, b, l)
        s = geo.MakePartition([e], [p, q], [], [], geo_solid)
        
        o = False
        for e in geo.SubShapeAll(s, geo_solid):
            k = string.split(geo.WhatIs(e))
            print k
            if (int(k[6])==4) and (int(k[9])==6) and (int(k[15])==4):
                o = True
                break
        if not o:
             raise "construire_element_face_mox"
        
        a = geo.MakeLine(c, ax)
        f = geo.MakeRotation(e, a, +angle_90)
        g = geo.MakeRotation(e, a, -angle_90)
        h = geo.MakeMirrorByAxis(e, a)

        return [e, f, g, h]

    # Construire un élément
    # ---------------------

    def construire_element(self, s, b, g=False):
        c, nr, er,  ax, an = s

        n = geo.MakeSpherePntR(c, nr)
        e = geo.MakeSpherePntR(c, er)

        if ax!=None:
            if type(ax)==type([]):
                ax1, ax = ax
                an1, an = an

                l = geo.MakeLine(c, ax1)

                n = geo.MakeRotation(n, l, an1)
                e = geo.MakeRotation(e, l, an1)

            l = geo.MakeLine(c, ax)

            n = geo.MakeRotation(n, l, an)
            e = geo.MakeRotation(e, l, an)

        n = geo.MakeCommon(n, b)
        e = geo.MakeCommon(e, b)

        if self._type!="mox":
            if g:
                return self.construire_element_face(c, nr, er,  ax, an,  n, e)
            else:
                return [e, n]
        else:
            if g:
                return self.construire_element_face_mox(c, nr, er,  ax, an, e)
            else:
                return [e]
        
    # Construire un élément sphérique
    # -------------------------------

    def construire_element_sphere(self, s):
        c, nr, er,  ax, an = s
        
        t = 4*self.cote()

        x = math.cos(angle_30)
        z = math.sin(angle_30)

        u = geo.MakeVectorDXDYDZ(-x, 0, +z)
        v = geo.MakeVectorDXDYDZ(-x, 0, -z)

        p = geo.MakePlane(c, u, t)
        q = geo.MakePlane(c, v, t)

        s = geo.MakeSpherePntR(c, er)

        d = geo.MakePartition([s], [p, q], [], [], geo_solid)

        p1 = geo.MakeTranslation(c, -er, 0, 0)
        f1 = geo.GetFaceNearPoint(d, p1)

        a  = geo.MakeLine(c, self.axe_y)
        f2 = geo.MakeRotation(f1, a, +angle_120)
        f3 = geo.MakeRotation(f1, a, -angle_120)

        e = geo.MakeShell([f1, f2, f3])
        
        #add VB test cas sans ecorces:
        if er==nr :
            n = geo.MakeSolid([e])
            return [n]
        else :
            e = geo.MakeSolid([e])
            n = geo.MakeScaleTransform(e, c, nr/er)
            return [e,n]
        #endadd

    # Construire la shape
    # -------------------

    def construire(self):
        b = self.boite()
        l = [b]

        for s in self.element_solides():
            l = l + self.construire_element_sphere(s)

        for s in self.element_faces():
            l = l + self.construire_element(s, b, True)

        for s in self.element_aretes():
            l = l + self.construire_element(s, b)

        for s in self.element_sommets():
            l = l + self.construire_element(s, b)

        r = geo.MakePartition(l, [], [], [], geo_solid)
        geo.addToStudy(r, self.nom())

        return r

    # Obtenir la shape
    # ----------------

    def obtenir(self):
        if self._shape==None:
            self._shape = self.construire()
            self.groupes()

        return self._shape

    # Sauver la shape
    # ---------------

    def sauver(self, rep="./"):
        s = self.obtenir()
        f = rep + self.nom() + ".brep"
        geo.ExportBREP(s, f)

        return f

    # Définir les groupes
    # ===================

    # Définir un groupe géométrique
    # -----------------------------

    def groupe(self, t, nom, l=[]):
        g = geo.CreateGroup(self._shape, t)
        geo.addToStudyInFather(self._shape, g, nom)
        g.SetName(nom)

        if l!=[]:
            if type(l[0])==type(0):
                geo.UnionIDs(g, l)
            else:
                geo.UnionList(g, l)

        return g

    # Construire la liste translatée d'une liste de shape
    # ---------------------------------------------------

    def groupe__trans(self, l,  dx, dy=None, dz=None):
        if dy==None:
            v = dx
        else:
            v = geo.MakeVectorDXDYDZ(dx, dy, dz)

        r = []
        for s in l:
            t = geo.MakeTranslationVector(s, v)
            o = geo.GetInPlace(self._shape, t)
            if o==None:
                geo.addToStudy(t, "Error:GetInPlace")
            r.append(o)

        return r

    # Construire la liste des edges passant par les axes et les plans des axes
    # ------------------------------------------------------------------------

    def groupe1_faces_aretes(self):
        xy0 = geo.GetShapesOnPlaneWithLocationIDs(self._shape, geo_edge, self.axe_z, geo_origine, geo.GEOM.ST_ON)
        xz0 = geo.GetShapesOnPlaneWithLocationIDs(self._shape, geo_edge, self.axe_y, geo_origine, geo.GEOM.ST_ON)
        yz0 = geo.GetShapesOnPlaneWithLocationIDs(self._shape, geo_edge, self.axe_x, geo_origine, geo.GEOM.ST_ON)

        x0 = self.intersection(xy0, xz0)
        y0 = self.intersection(xy0, yz0)
        z0 = self.intersection(xz0, yz0)

        p = geo.MakeVertex(self.cote(), self.cote(), self.cote())

        xy1 = geo.GetShapesOnPlaneWithLocationIDs(self._shape, geo_edge, self.axe_z, p, geo.GEOM.ST_ON)
        xz1 = geo.GetShapesOnPlaneWithLocationIDs(self._shape, geo_edge, self.axe_y, p, geo.GEOM.ST_ON)
        yz1 = geo.GetShapesOnPlaneWithLocationIDs(self._shape, geo_edge, self.axe_x, p, geo.GEOM.ST_ON)

        a = xy1 + xz1 + yz1

        xy = self.difference(xy0, xz0)
        xy = self.difference(xy , xz1)
        xy = self.difference(xy , yz0)
        xy = self.difference(xy , yz1)

        xz = self.difference(xz0, xy0)
        xz = self.difference(xz , xy1)
        xz = self.difference(xz , yz0)
        xz = self.difference(xz , yz1)

        yz = self.difference(yz0, xy0)
        yz = self.difference(yz , xy1)
        yz = self.difference(yz , xz0)
        yz = self.difference(yz , xz1)

        x0 = self.donner_shapes(x0)
        y0 = self.donner_shapes(y0)
        z0 = self.donner_shapes(z0)

        xy = self.donner_shapes(xy)
        xz = self.donner_shapes(xz)
        yz = self.donner_shapes(yz)

        return a,  x0, y0, z0,  xy, xz, yz

    # Construire la liste des edges sur les plans des axes entre les écorces et les noyaux coupés
    # -------------------------------------------------------------------------------------------

    def groupe1_coupees(self, a):
        l = self.element_faces() + self.element_aretes() + self.element_sommets()
        r = []
        for c, nr, er,  ax, an in l:
            e = geo.GetShapesOnSphereIDs(self._shape, geo_edge, c, er, geo.GEOM.ST_IN)
            n = geo.GetShapesOnSphereIDs(self._shape, geo_edge, c, nr, geo.GEOM.ST_ONIN)
            if (er!=nr) and (self._type!="mox"):
                d = self.difference(e, n)
                r = r + self.difference(d, a)
            else :
                d = e
                r = r + self.difference(d,a)
                      
        return self.groupe(geo_edge, self.nom_coupees+"1", r)

    # Récupérer les génératrices
    # --------------------------

    def groupe1_filter(self, c, r, a):
        l = geo.GetShapesOnSphereIDs(self._shape, geo_edge, c, r, geo.GEOM.ST_ON)
        l = self.difference(l, a)

        r = []
        for i in l:
            e = self.donner_shapes(i)
            if not self.edge_degenere(e):
                r.append(e)

        return r

    # Construire les listes des génératrices des écorces et des noyaux
    # ----------------------------------------------------------------

    def groupe1_ecorces_noyaux(self, a):
        l = self.element_solides() + self.element_faces() + self.element_aretes() + self.element_sommets()
        e = []
        n = []
        for c, nr, er,  ax, an in l:
            el = self.groupe1_filter(c, er, a)
            nl = self.groupe1_filter(c, nr, a)

            for ee in el:
                ev = geo.MakeVertexOnCurve(ee, 0.5)
                mi = self.cote()
                for ed in nl:
                    nv = geo.MakeVertexOnCurve(ed, 0.5)
                    di = geo.MinDistance(ev, nv)
                    if mi>di:
                        mi = di
                        ne = ed
                e.append(ee)
                n.append(ne)
# adds RL-VB
        if (er!=nr) and (self._type!="mox"):
            
            return e,n
        else:
            print " groupe 1 mox"
            return e

    # Construire la liste des faces passant par un plan
    # -------------------------------------------------

    def groupe2_faces(self, normale):
        return geo.GetShapesOnPlaneWithLocation(self._shape, geo_face, normale, geo_origine, geo.GEOM.ST_ON)

    # Construire la liste des faces des plans axiaux entre les écorces et les noyaux coupés
    # -------------------------------------------------------------------------------------

    def groupe2_coupees(self, p):
        a = []
        for s in p:
            i = geo.GetSubShapeID(self._shape, s)
            a.append(i)

        l = self.element_faces() + self.element_aretes() + self.element_sommets()
        r = []
        if self._type!="mox":
            for c, nr, er,  ax, an in l:
                e = geo.GetShapesOnSphereIDs(self._shape, geo_face, c, er, geo.GEOM.ST_IN)
                n = geo.GetShapesOnSphereIDs(self._shape, geo_face, c, nr, geo.GEOM.ST_ONIN)
                d = self.difference(e, n)
                r = r + self.difference(d, a)
        else:
            for c, nr, er,  ax, an in l:
                e = geo.GetShapesOnSphereIDs(self._shape, geo_face, c, er, geo.GEOM.ST_ONIN)
                r = r + self.difference(e, a)
                
        return self.groupe(geo_face, self.nom_coupees+"2", r)

    # Construire les listes des groupes des enveloppes des écorces entières et coupées et de même pour les noyaux
    # -----------------------------------------------------------------------------------------------------------

    def groupe2_ecorces_noyaux(self):
        l = self.element_solides() + self.element_faces() + self.element_aretes() + self.element_sommets()
        i = 0
        e = []
        n = []

        for c, nr, er,  ax, an in l:
            i = i + 1

            el = geo.GetShapesOnSphere(self._shape, geo_face, c, er, geo.GEOM.ST_ON)

            e.append(self.groupe(geo_face, self.nom_ecorce+"2"+str(i), el))
           
            # adds RL-VB
            if (er!=nr) and (self._type!="mox"):
                nl = geo.GetShapesOnSphere(self._shape, geo_face, c, nr, geo.GEOM.ST_ON)
                n.append(self.groupe(geo_face, self.nom_noyau +"2"+str(i), nl))
                
        
        if (er!=nr) and (self._type!="mox"):
            return e, n
        else:
            print "groupe 2 mox"
            return e

    # Construire les listes des groupes des écorces coupées, des groupes des écorces entières et des groupes des noyaux entiers et coupés
    # -----------------------------------------------------------------------------------------------------------------------------------

    def groupe3_ecorces_noyaux(self):
        i = 0
        c = []
        e = []
        n = []
        e1 = []
        c1=[]
        
        for ce, nr, er,  ax, an in self.element_solides():
            i = i + 1
            
            pl = geo.GetShapesOnSphereIDs(self._shape, geo_solid, ce, er, geo.GEOM.ST_ONIN)
            e1.append(self.groupe(geo_solid, self.nom_ecorce+"3"+str(i), pl))

            if er<>nr:
                
                nl = geo.GetShapesOnSphereIDs(self._shape, geo_solid, ce, nr, geo.GEOM.ST_ONIN)
                el = self.difference(pl, nl)
                e.append(self.groupe(geo_solid, self.nom_ecorce+"3"+str(i), el))
                n.append(self.groupe(geo_solid, self.nom_noyau +"3"+str(i), nl))
                
        l = self.element_faces() + self.element_aretes() + self.element_sommets()
        
        for ce, nr, er,  ax, an in l:
            i = i + 1
            pl = geo.GetShapesOnSphereIDs(self._shape, geo_solid, ce, er, geo.GEOM.ST_ONIN)
            c1.append(self.groupe(geo_solid, self.nom_ecorce+"3"+str(i), pl))
            
                        
            if (er!=nr) and (self._type!="mox") :
                nl = geo.GetShapesOnSphereIDs(self._shape, geo_solid, ce, nr, geo.GEOM.ST_ONIN)
                el = self.difference(pl, nl)
                c.append(self.groupe(geo_solid, self.nom_ecorce+"3"+str(i), el))
                n.append(self.groupe(geo_solid, self.nom_noyau +"3"+str(i), nl))
                
# adds RL-VB
        if (er!=nr) and (self._type!="mox"):
            return c,e,n
        else:
            return c1, e1

    # Construire le groupe de la matrice
    # ----------------------------------

    def groupe3_matrice(self):
        l = geo.SubShapeAll(self._shape, geo_solid)
        for s in l:
            f = geo.SubShapeAllIDs(s, geo_face)
            if len(f) > 6:
                return self.groupe(geo_solid, self.nom_matrice, [s])

        raise "groupe3_matrice"

    # Construire les groupes
    # ----------------------

    def groupes(self):
        a,  self.g1_x0, self.g1_y0, self.g1_z0,  self.g1_xy0, self.g1_xz0, self.g1_yz0 = self.groupe1_faces_aretes()

        self.g1_x1  = self.groupe__trans(self.g1_x0, self.axe_y)
        self.g1_x2  = self.groupe__trans(self.g1_x0, self.axe_z)
        self.g1_x3  = self.groupe__trans(self.g1_x0, 0, self.cote(), self.cote())

        self.g1_y1  = self.groupe__trans(self.g1_y0, self.axe_x)
        self.g1_y2  = self.groupe__trans(self.g1_y0, self.axe_z)
        self.g1_y3  = self.groupe__trans(self.g1_y0, self.cote(), 0, self.cote())

        self.g1_z1  = self.groupe__trans(self.g1_z0, self.axe_x)
        self.g1_z2  = self.groupe__trans(self.g1_z0, self.axe_y)
        self.g1_z3  = self.groupe__trans(self.g1_z0, self.cote(), self.cote(), 0)

        self.g1_xy1 = self.groupe__trans(self.g1_xy0, self.axe_z)
        self.g1_xz1 = self.groupe__trans(self.g1_xz0, self.axe_y)
        self.g1_yz1 = self.groupe__trans(self.g1_yz0, self.axe_x)

        
        self.g2_xy0 = self.groupe2_faces(self.axe_z)
        self.g2_xy1 = self.groupe__trans(self.g2_xy0, self.axe_z)
        self.g2_xz0 = self.groupe2_faces(self.axe_y)
        self.g2_xz1 = self.groupe__trans(self.g2_xz0, self.axe_y)
        self.g2_yz0 = self.groupe2_faces(self.axe_x)
        self.g2_yz1 = self.groupe__trans(self.g2_yz0, self.axe_x)

       
        if self._type!="mox":
            self.g1_coupees = self.groupe1_coupees(a)
            self.g1_ecorces, self.g1_noyaux = self.groupe1_ecorces_noyaux(a)
            self.g2_coupees = self.groupe2_coupees(self.g2_xy1 + self.g2_xz1 + self.g2_yz1)
            self.g2_ecorces, self.g2_noyaux = self.groupe2_ecorces_noyaux()
            self.g3_coupees, self.g3_ecorces, self.g3_noyaux = self.groupe3_ecorces_noyaux()

        else:
            self.g1_coupees = self.groupe1_coupees(a)
            self.g1_ecorces = self.groupe1_ecorces_noyaux(a)
            self.g2_coupees = self.groupe2_coupees(self.g2_xy1 + self.g2_xz1 + self.g2_yz1)
            self.g2_ecorces = self.groupe2_ecorces_noyaux()
            self.g3_coupees, self.g3_ecorces = self.groupe3_ecorces_noyaux()
            
       
        
        
        self.g3_matrice = self.groupe3_matrice()

        

        
# Définir le maillage du VER
# ==========================

class maillage:

    # Initialiser le maillage
    # -----------------------

    def __init__(self, shape,mox="mox"):
        self.shape = shape
        print " type de structure", mox
        self._type = mox
        self.mesh = smesh.Mesh(self.shape.obtenir(), self.shape.nom())

        self.couches(2)
        self.longueur(20)
        self.triangle(smesh.NETGEN_2D)
        self.tetra(smesh.NETGEN, 1000)
        self.fichier("")

    def type_comb(self, type=None):
        if type!=None:
            self._type = type
            
        return self._type

    # Donner le nombre de couches de prismes
    # --------------------------------------

    def couches(self, c=None):
        if c!=None:
            self._couches = c

        return self._couches

    # Donner la longueur moyenne des cotés des triangles
    # --------------------------------------------------

    def longueur(self, l=None):
        if l!=None:
            self._longueur = l

        return self._longueur

    # Donner l'algorithme pour générer les triangles
    # ----------------------------------------------

    def triangle(self, a=None):
        if a!=None:
            self._triangle = a

        return self._triangle

    # Donner l'algorithme et ses éventuelles options pour générer les tétraèdres
    # --------------------------------------------------------------------------

    def tetra(self, a=None, o=None):
        if a!=None:
            self._tetra = [a, o]

        return self._tetra

    # Donner le fichier med pour sauver le maillage
    # ---------------------------------------------

    def fichier(self, f=None):
        if f!=None:
            self._fichier = f

        return self._fichier

    # Projeter le maillage d'une liste d'edges vers une autre liste d'edges
    # ---------------------------------------------------------------------

    def projeter_1d_liste(self, s, d):
        i = 0
        n = len(s)
        while i<n:
            a = self.mesh.Projection1D(d[i])
            a.SourceEdge(s[i])
            i = i + 1

    # Mailler avec des segments
    # -------------------------

    def segments(self):
        a = self.mesh.Segment()
        a.LocalLength(self.longueur())

        if self._type!="mox":
            a = self.mesh.Segment(self.shape.g1_coupees)
            a.NumberOfSegments(self.couches())
            self.projeter_1d_liste(self.shape.g1_ecorces, self.shape.g1_noyaux)
        else :
            a = self.mesh.Segment(self.shape.g1_coupees)
            a.NumberOfSegments(10)
        self.projeter_1d_liste(self.shape.g1_x0, self.shape.g1_x1)
        self.projeter_1d_liste(self.shape.g1_x0, self.shape.g1_x2)
        self.projeter_1d_liste(self.shape.g1_x0, self.shape.g1_x3)

        self.projeter_1d_liste(self.shape.g1_y0, self.shape.g1_y1)
        self.projeter_1d_liste(self.shape.g1_y0, self.shape.g1_y2)
        self.projeter_1d_liste(self.shape.g1_y0, self.shape.g1_y3)

        self.projeter_1d_liste(self.shape.g1_z0, self.shape.g1_z1)
        self.projeter_1d_liste(self.shape.g1_z0, self.shape.g1_z2)
        self.projeter_1d_liste(self.shape.g1_z0, self.shape.g1_z3)

        self.projeter_1d_liste(self.shape.g1_xy0, self.shape.g1_xy1)
        self.projeter_1d_liste(self.shape.g1_xz0, self.shape.g1_xz1)
        self.projeter_1d_liste(self.shape.g1_yz0, self.shape.g1_yz1)

    # Projeter le maillage d'une liste de faces vers une autre liste de faces
    # -----------------------------------------------------------------------

    def projeter_2d_liste(self, s, d):
        i = 0
        n = len(s)
        while i<n:
            a = self.mesh.Projection2D(d[i])
            a.SourceFace(s[i])
            i = i + 1

    # Mailler avec des triangles
    # --------------------------

    def triangles(self):
        a = self.mesh.Triangle(self.triangle())
        a.LengthFromEdges()

        if self._type!="mox":
            self.projeter_2d_liste(self.shape.g2_ecorces, self.shape.g2_noyaux)

        self.projeter_2d_liste(self.shape.g2_xy0, self.shape.g2_xy1)
        self.projeter_2d_liste(self.shape.g2_xz0, self.shape.g2_xz1)
        self.projeter_2d_liste(self.shape.g2_yz0, self.shape.g2_yz1)

    # Mailler avec des quadrangles
    # ----------------------------

    def quadrangles(self):
        self.mesh.Quadrangle(self.shape.g2_coupees)

    # Mailler avec des tétraèdres
    # ---------------------------

    def tetraedres(self):
        a, o = self.tetra()
        t = self.mesh.Tetrahedron(a)
        if o!=None:
            t.MaxElementVolume(o)

    # Mailler avec des prismes
    # ------------------------

    def prismes(self):
        for g in self.shape.g3_ecorces:
            a = self.mesh.Prism(g)
            a.NumberOfSegments(self.couches())

        for g in self.shape.g3_coupees:
            self.mesh.Prism(g)

    # Construire les groupes de maille
    # --------------------------------

    def groupes(self):
        self.mesh.Group(self.shape.groupe(geo_face, self.shape.nom_xy+"0", self.shape.g2_xy0))
        self.mesh.Group(self.shape.groupe(geo_face, self.shape.nom_xy+"1", self.shape.g2_xy1))
        self.mesh.Group(self.shape.groupe(geo_face, self.shape.nom_xz+"0", self.shape.g2_xz0))
        self.mesh.Group(self.shape.groupe(geo_face, self.shape.nom_xz+"1", self.shape.g2_xz1))
        self.mesh.Group(self.shape.groupe(geo_face, self.shape.nom_yz+"0", self.shape.g2_yz0))
        self.mesh.Group(self.shape.groupe(geo_face, self.shape.nom_yz+"1", self.shape.g2_yz1))

        el = []
        for g in self.shape.g2_ecorces:
            self.mesh.Group(g)
            el = el + geo.GetObjectIDs(g)
        self.mesh.Group(self.shape.groupe(geo_face, self.shape.nom_ecorce+"2", el))

        if self._type!="mox":
            nl = []
            for g in self.shape.g2_noyaux:
                self.mesh.Group(g)
                nl = nl + geo.GetObjectIDs(g)
            self.mesh.Group(self.shape.groupe(geo_face, self.shape.nom_noyau +"2", nl))

        el = []
        for g in self.shape.g3_ecorces:
            self.mesh.Group(g)
            el = el + geo.GetObjectIDs(g)

        for g in self.shape.g3_coupees:
            self.mesh.Group(g)
            el = el + geo.GetObjectIDs(g)

        self.mesh.Group(self.shape.groupe(geo_solid, self.shape.nom_ecorce+"3", el))
        
        if self._type!="mox":
            nl = []
            for g in self.shape.g3_noyaux:
                self.mesh.Group(g)
                nl = nl + geo.GetObjectIDs(g)
            self.mesh.Group(self.shape.groupe(geo_solid, self.shape.nom_noyau +"3", nl))

        self.mesh.Group(self.shape.g3_matrice)

    # Sauver le maillage
    # ------------------

    def sauver(self, fic=None):
        if fic==None:
            f = self.fichier()
        else:
            f = fic

        if f=="":
            return False
        else:
            self.mesh.ExportToMED(f, smesh.SMESH.MED_V2_2)
            return True

    # Générer le maillage
    # -------------------

    def generer(self):
        
        self.segments()

        self.triangles()
        
        if self._type!="mox":
            print "maillage par des quadrangles"
            self.quadrangles()

        self.tetraedres()

        if self._type!="mox":
            print "maillage par des prismes"
            self.prismes()

        self.groupes()

        self.mesh.Compute()

        self.sauver()
