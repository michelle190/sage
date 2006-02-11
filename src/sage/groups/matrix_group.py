"""nodoctest
UNFINISHED / UNPROCESSED CODE - not tested and not exported
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@ucsd.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

"""
To do: Rework this and special_linear into MatrixGroup class for any field,
wrapping all of GAP's matrix group commands in chapter 41 Matrix Groups of
the GAP reference manual.

"""

from group import Group
from sage.rings.all import IntegerRing, is_Ring
from sage.misc.functional import is_field
from sage.rings.finite_field import is_FiniteField
from sage.interfaces.gap import gap, sage2gap_finite_field_string
from sage.matrix.matrix_space import MatrixSpace
import copy
import sage.rings.integer as integer


#################################################################

def MatGroup(gens):
    return MatrixGroup(gens)

class MatrixGroup(Group):
    def __init__(self, gens):
        #gens is a list of matrices generating the gp
        self.__n = len(gens[0].rows())
        self.__R = gens[0].base_ring()
        self.gens = gens
        if not is_Ring(self.__R):
            raise TypeError, "R (=%s) must be a ring"%self.__R

    def __repr__(self):
        return "The matrix group over %s generated by\n %s"%(self.__R, self.gens)

    def is_finite(self):
        """
        EXAMPLES:
        sage: G = GL(2,GF(3))
        sage: G.is_finite()
        True
        """
        return self.__R.is_finite()

    def conjugacy_class_representatives(self):
        """
        Wraps GAP Representative+ConjugactClasses.

        EXAMPLES:
        sage: F = GF(5); MS = MatrixSpace(F,2,2)
        sage: gens = [MS([[1,2],[-1,1]]),MS([[1,1],[0,1]])]
        sage: G = MatGroup(gens)
        sage: G.conjugacy_class_representatives()

        [[2 0]
         [0 2],
         [0 2]
         [1 1],
         [1 0]
         [0 1],
         [0 2]
         [1 2],
         [0 2]
         [1 0],
         [0 1]
         [1 2],
         [0 1]
         [1 1],
         [2 0]
         [0 1]]

        AUTHOR: David Joyner (1-2006)
        """
        from sage.misc.misc import add
        F = self.__R
        deg = self.__n
        gp_gens = self.gens
        L = [sage2gap_matrix_finite_field_string(A,deg,deg,F) for A in gp_gens]
        sL = "["+add([x+"," for x in L])[:-1]+"]"
        if is_FiniteField(F):
            q = F.order()
            gap.eval("cl:=ConjugacyClasses(MatGroup("+sL+"))")
            m = eval(gap.eval("Length(cl)"))
            gap.eval("reps:=List(cl,x->Representative(x))")
            sreps = [gap.eval("reps["+str(i+1)+"]") for i in range(m)]
            reps = [gap2sage_matrix_finite_field(s,deg,deg,F) for s in sreps]
            return reps
        raise TypeError, "R (=%s) must be a finite field"%R

    def conjugacy_class_representatives_gap(self):
        """
        Wraps GAP Representative+ConjugactClasses but returns a list of
        strings representing the GAP matrices which form a complete
        set of representatives of the conjugacy classes of the group.

        EXAMPLES:
        sage: G = GL(2,GF(3))
        sage: G.conjugacy_class_representatives_gap()

        ['[ [ Z(3), 0*Z(3) ], [ 0*Z(3), Z(3) ] ]',
         '[ [ 0*Z(3), Z(3) ], [ Z(3)^0, Z(3)^0 ] ]',
         '[ [ Z(3)^0, 0*Z(3) ], [ 0*Z(3), Z(3)^0 ] ]',
         '[ [ 0*Z(3), Z(3) ], [ Z(3)^0, Z(3) ] ]',
         '[ [ 0*Z(3), Z(3) ], [ Z(3)^0, 0*Z(3) ] ]',
         '[ [ 0*Z(3), Z(3)^0 ], [ Z(3)^0, Z(3) ] ]',
         '[ [ 0*Z(3), Z(3)^0 ], [ Z(3)^0, Z(3)^0 ] ]',
         '[ [ Z(3), 0*Z(3) ], [ 0*Z(3), Z(3)^0 ] ]']

        AUTHOR: David Joyner (1-2006)
        """
        F = self.__R
        deg = self.__n
        gp_gens = self.gens()
        L = [sage2gap_matrix_finite_field_string(A,deg,deg,F) for A in gens]
        sL = "["+add([x+"," for x in L])[:-1]+"]"
        if is_FiniteField(F):
            q = F.order()
            gap.eval("cl:=ConjugacyClasses(MatGroup("+sL+"))")
            m = eval(gap.eval("Length(cl)"))
            gap.eval("reps:=List(cl,x->Representative(x))")
            sreps = [gap.eval("reps["+str(i+1)+"]") for i in range(m)]
            return sreps
        raise TypeError, "R (=%s) must be a finite field"%R


def brauer_lift(mat):
    """
    Wraps BrauerCharacterValue. The GAP function chooses a correspondence
    between the eigenvalues of mat and elements of a suitable cyclotomic
    field.

    For an invertible matrix mat over a finite field F, brauer_lift
    returns the Brauer character value of mat if the order of mat is coprime
    to the characteristic of F, and fail otherwise. This will always
    be an element of some cyclotomic field, since over a finite
    field any invertible matrix mat is finite order, so will be
    a polynomial in zeta_n, for some n.

    EXAMPLES:
    sage: F = GF(3); MS = MatrixSpace(F,2,2)
    sage: a = F.gen(); mat = MS([[0*a,-a],[a,-a]])
    sage: mat = MS([[0*a,-a],[a,-a]])
    sage: brauer_lift(mat)
    'fail'
    sage: mat^3

    [1 0]
    [0 1]
    sage: mat = MS([[0*a,a],[a,-a]])
    sage: mat^3

    [2 2]
    [2 0]
    sage: brauer_lift(mat)
    -zeta_8^3 - zeta_8
    sage: F = GF(11); a = F.multiplicative_generator()
    sage: D = [[1,1,1],[a^2,a^3,a^7]]
    sage: G = automorphism_group_divisor_P1(D); G[0]
    [60, 11]
    sage: g = G[1].gens[39]
    sage: g

    [10  6]
    [ 9  0]
    sage: rho = matrix_repn_on_riemann_roch_space_P1(g,D); rho

    [ 0  9  0  6]
    [ 0  0  3 10]
    [ 9  0  0  5]
    [ 0  0  0  1]
    sage: brauer_lift(rho)
    1

    """
    F = mat[1][1].parent()
    q = F.order()
    m = len(mat.rows())
    M = sage2gap_matrix_finite_field_string(mat,m,m,F)
    #print M
    s=gap.eval("BrauerCharacterValue("+M+");")
    if s=="fail":
        return TypeError, "BrauerCharacterValue returned 'fail' (does mat have order prime to char(F)-1 ?)"
    #print s
    return gap2sage_cyclotomic_field(s)


from sage.misc.misc import add

def automorphism_group_divisor_P1(D):
    """
    Wraps GUAVA's DivisorAutomorphismGroupP1. Must have
    guava 2.4 or better installed.
    Idea: (a) convert D to a gap Divisor record div
    (b) get agp=DivisorAutomorphismGroupP1(div)
    (c) use GAP for loop to compute SAGE matrices
        corresponding to each g in agp
    (d) return the list of such SAGE matrices.

    INPUT:
    A divisor D on the projective line $P^1(F)$ represented
    by a pair of lists [m,pts], where
    m is a list of integer multiplicities, and
    pts is a list of points on P^1(F), F a finite field
    OUTPUT:
    The subgroup of GL(2,F) which stabilizes D. Actually, the
    group_id list of all group elements is returned since SAGE
    does not have a matrix group class (yet).
    Requires GAP's (optional) database package be installed.

    EXAMPLES:
    sage: F = GF(11); a = F.multiplicative_generator()
    sage: D = [[1,1,1,1],[a^2,a^3,a^7,a]]
    sage: G = automorphism_group_divisor_P1(D); G[0]
    [80, 26]

    AUTHOR: David Joyner (1-2006)
    """
    from sage.groups.general_linear import MatGroup
    F = D[1][1].parent()
    q = F.order()
    #cmd = 'LoadPackage("guava")'
    #print cmd
    #gap.eval(cmd)
    cmd = 'R1:=PolynomialRing(GF('+str(q)+'));'
    #print cmd
    gap.eval(cmd)
    cmd = "var1:=IndeterminatesOfPolynomialRing(R1);; a:=var1[1];"
    #print cmd
    gap.eval(cmd)
    cmd = 'b:=X(GF('+str(q)+'),var1); var2:=Concatenation(var1,[b]);'
    #print cmd
    gap.eval(cmd)
    cmd = "R2:=PolynomialRing(GF("+str(q)+"),var2);"
    #print cmd
    gap.eval(cmd)
    cmd = "crvP1:=AffineCurve(b,R2);"
    #print cmd
    gap.eval(cmd)
    m = D[0]
    pts = D[1]
    gap_pts = [sage2gap_finite_field_string(a) for a in pts]
    sgap_pts = "["+add([x+"," for x in gap_pts])
    sgps = sgap_pts[:-1]+"]"
    cmd = "div:=DivisorOnAffineCurve("+str(m)+","+sgps+",crvP1);"
    #print cmd
    gap.eval(cmd)
    cmd = "agp:=DivisorAutomorphismGroupP1(div);"
    #print cmd
    gap.eval(cmd)
    cmd = "IdGroup(agp); "
    #print cmd
    gp_id = eval(gap.eval(cmd))
    cmd = "L:=Elements(agp);"
    #print cmd
    gap.eval(cmd)
    sL = [gap.eval("L["+str(i+1)+"]") for i in range(gp_id[0])]
    gp_elmts = [gap2sage_matrix_finite_field(A,2,2,F) for A in sL]
    return gp_id,MatGroup(gp_elmts)

def matrix_repn_on_riemann_roch_space_P1(g,D):
    """
    Wraps GUAVA's MatrixRepresentationOnRiemannRochSpaceP1. Must have
    guava 2.4 or better installed.

    INPUT:
    A divisor D on the projective line $P^1(F)$ represented
    by a pair of lists [m,pts], where
    m is a list of integer multiplicities, and
    pts is a list of points on $P^1(F)$, F a finite field.
    An element g of GL(2,F) is represented by an invertible element of
    MatrixSpace(F,2,2). The command assumes g is in the list obtained
    from G = divisor_automorphism_group_P1(D). No error checking is
    performed.

    OUTPUT:
    The d x d matrix over F (where d is the dimension of the Riemann-Roch
    space of D, L(D)) which represents the action of g on L(D).

    To this matrix, $\rho_D(g)$, say, one may apply brauer_lift
    for each g in a complete set of representatives of
    the conjugacy classes of the image of G in $PGL(2,F)$. (The same
    ordering as given by GAP's ConjugacyClasses must be used.)
    If all these g have orders relatively prime to char(F) (the
    "good characteristic case") then these character values will
    determine the decomposition of rho into irreducible representations
    of G.

    EXAMPLES:
    sage: F = GF(11); a = F.multiplicative_generator()
    sage: D = [[1,1,1,1],[a^2,a^3,a^7,a]]
    sage: G = automorphism_group_divisor_P1(D); G[0]
    [80, 26]
    sage: rho = matrix_repn_on_riemann_roch_space_P1(G[1][2],D); rho

    [10  0  0  0  8]
    [ 0 10  0  0  3]
    [ 0  0  0  8  4]
    [ 0  0  7  0  5]
    [ 0  0  0  0  1]

    AUTHOR: David Joyner
    """
    F = D[1][1].parent()
    MS = g.parent() # = MatrixSpace(F,2,2)
    q = F.order()
    #cmd = 'LoadPackage("guava")'
    #print cmd
    #gap.eval(cmd)
    cmd = 'R1:=PolynomialRing(GF('+str(q)+'));'
    #print cmd
    gap.eval(cmd)
    cmd = "var1:=IndeterminatesOfPolynomialRing(R1);; a:=var1[1];"
    #print cmd
    gap.eval(cmd)
    cmd = 'b:=X(GF('+str(q)+'),var1); var2:=Concatenation(var1,[b]);'
    #print cmd
    gap.eval(cmd)
    cmd = "R2:=PolynomialRing(GF("+str(q)+"),var2);"
    #print cmd
    gap.eval(cmd)
    cmd = "crvP1:=AffineCurve(b,R2);"
    #print cmd
    gap.eval(cmd)
    m = D[0]
    pts = D[1]
    gap_pts = [sage2gap_finite_field_string(a) for a in pts]
    sgap_pts = "["+add([x+"," for x in gap_pts])
    sgps = sgap_pts[:-1]+"]"
    cmd = "div:=DivisorOnAffineCurve("+str(m)+","+sgps+",crvP1);"
    #print cmd
    gap.eval(cmd)
    A = sage2gap_matrix_finite_field_string(g,2,2,F)
    rho=gap.eval("MatrixRepresentationOnRiemannRochSpaceP1("+A+",div)")
    deg = eval(gap.eval("Length(RiemannRochSpaceBasisP1(div))"))
    #return rho,deg
    #return rho
    return gap2sage_matrix_finite_field(rho,deg,deg,F)


