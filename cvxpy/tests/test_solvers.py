from cvxpy import *
from cvxpy.tests.base_test import BaseTest

class TestSolvers(BaseTest):
    """ Unit tests for solver specific behavior. """
    def setUp(self):
        self.a = Variable(name='a')
        self.b = Variable(name='b')
        self.c = Variable(name='c')

        self.x = Variable(2, name='x')
        self.y = Variable(3, name='y')
        self.z = Variable(2, name='z')

        self.A = Variable(2,2,name='A')
        self.B = Variable(2,2,name='B')
        self.C = Variable(3,2,name='C')

    def test_solver_errors(self):
        """Tests that solver errors throw an exception.
        """
        # For some reason CVXOPT can't handle this problem.
        expr = 500*self.a + square(self.a)
        prob = Problem(Minimize(expr))

        with self.assertRaises(Exception) as cm:
            prob.solve(solver=CVXOPT)
        self.assertEqual(str(cm.exception),
            "Solver 'CVXOPT' failed. Try another solver.")

    def test_ecos_options(self):
        """Test that all the ECOS solver options work.
        """
        # Test ecos
        # feastol, abstol, reltol, feastol_inacc, abstol_inacc, and reltol_inacc for tolerance values
        # max_iters for the maximum number of iterations,
        EPS = 1e-4
        prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
        for i in range(2):
            prob.solve(solver=ECOS, feastol=EPS, abstol=EPS, reltol=EPS,
                       feastol_inacc=EPS, abstol_inacc=EPS, reltol_inacc=EPS,
                       max_iters=20, verbose=True, warm_start=True)
        self.assertItemsAlmostEqual(self.x.value, [0, 0])

    def test_ecos_bb_options(self):
        """Test that all the ECOS BB solver options work.
        """
        # 'mi_maxiter'
        # maximum number of branch and bound iterations (default: 1000)
        # 'mi_abs_eps'
        # absolute tolerance between upper and lower bounds (default: 1e-6)
        # 'mi_rel_eps'
        EPS = 1e-4
        prob = Problem(Minimize(norm(self.x, 1)), [self.x == Bool(2)])
        for i in range(2):
            prob.solve(solver=ECOS_BB, mi_max_iters=100, mi_abs_eps=1e-6,
            mi_rel_eps=1e-5, verbose=True, warm_start=True)
        self.assertItemsAlmostEqual(self.x.value, [0, 0])

    def test_scs_options(self):
        """Test that all the SCS solver options work.
        """
        # Test SCS
        # MAX_ITERS, EPS, ALPHA, UNDET_TOL, VERBOSE, and NORMALIZE.
        # If opts is missing, then the algorithm uses default settings.
        # USE_INDIRECT = True
        EPS = 1e-4
        prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
        for i in range(2):
            prob.solve(solver=SCS, max_iters=50, eps=EPS, alpha=EPS,
                       verbose=True, normalize=True, use_indirect=False)
        self.assertItemsAlmostEqual(self.x.value, [0, 0])

    def test_cvxopt_options(self):
        """Test that all the CVXOPT solver options work.
        """
        # TODO race condition when changing these values.
        # 'maxiters'
        # maximum number of iterations (default: 100).
        # 'abstol'
        # absolute accuracy (default: 1e-7).
        # 'reltol'
        # relative accuracy (default: 1e-6).
        # 'feastol'
        # tolerance for feasibility conditions (default: 1e-7).
        # 'refinement'
        # number of iterative refinement steps when solving KKT equations (default: 0 if the problem has no second-order cone or matrix inequality constraints; 1 otherwise).
        EPS = 1e-7
        prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
        for i in range(2):
            prob.solve(solver=CVXOPT, feastol=EPS, abstol=EPS, reltol=EPS,
                       max_iters=20, verbose=True, kktsolver="chol",
                       refinement=2, warm_start=True)
        self.assertItemsAlmostEqual(self.x.value, [0, 0])

    def test_cvxopt_glpk(self):
        """Test a basic LP with GLPK.
        """
        # Either the problem is solved or GLPK is not installed.
        if GLPK in installed_solvers():
            prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
            prob.solve(solver = GLPK)
            self.assertItemsAlmostEqual(self.x.value, [0, 0])

            # Example from http://cvxopt.org/userguide/coneprog.html?highlight=solvers.lp#cvxopt.solvers.lp
            objective = Minimize(-4 * self.x[0] - 5 * self.x[1])
            constraints = [ 2 * self.x[0] + self.x[1] <= 3,
                            self.x[0] + 2 * self.x[1] <= 3,
                            self.x[0] >= 0,
                            self.x[1] >= 0]
            prob = Problem(objective, constraints)
            prob.solve(solver = GLPK)
            self.assertItemsAlmostEqual(self.x.value, [1, 1])
        else:
            with self.assertRaises(Exception) as cm:
                prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
                prob.solve(solver = GLPK)
            self.assertEqual(str(cm.exception), "The solver %s is not installed." % GLPK)

    def test_gurobi_lin(self):
        """Test a basic LP with Gurobi.
        """
        if GUROBI_LIN in installed_solvers():
            prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
            prob.solve(solver = GUROBI_LIN)
            self.assertItemsAlmostEqual(self.x.value, [0, 0])

            # Example from http://cvxopt.org/userguide/coneprog.html?highlight=solvers.lp#cvxopt.solvers.lp
            objective = Minimize(-4 * self.x[0] - 5 * self.x[1])
            constraints = [ 2 * self.x[0] + self.x[1] <= 3,
                            self.x[0] + 2 * self.x[1] <= 3,
                            self.x[0] >= 0,
                            self.x[1] >= 0]
            prob = Problem(objective, constraints)
            prob.solve(solver = GUROBI_LIN)
            self.assertItemsAlmostEqual(self.x.value, [1, 1])

            # Gurobi's default lower bound for a decision variable is zero
            # This quick test ensures that the cvxpy interface for GUROBI_LIN does *not* have that bound
            objective = Minimize(self.x[0])
            constraints = [self.x[0] >= -100, self.x[0] <= -10, self.x[1] == 1]
            prob = Problem(objective, constraints)
            prob.solve(solver = GUROBI_LIN)
            self.assertItemsAlmostEqual(self.x.value, [-100, 1])
        else:
            with self.assertRaises(Exception) as cm:
                prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
                prob.solve(solver = GUROBI_LIN)
            self.assertEqual(str(cm.exception), "The solver %s is not installed." % GUROBI_LIN)

    def test_gurobi_lin_dual(self):
        """Make sure Gurobi's dual result matches other solvers
        """
        if GUROBI_LIN in installed_solvers():
            constraints = [self.x == 0]
            prob = Problem(Minimize(norm(self.x, 1)))
            prob.solve(solver = GUROBI_LIN)
            duals_gurobi_lin = [x.dual_value for x in constraints]
            prob.solve(solver = ECOS)
            duals_ecos = [x.dual_value for x in constraints]
            self.assertItemsAlmostEqual(duals_gurobi_lin, duals_ecos)

            # Example from http://cvxopt.org/userguide/coneprog.html?highlight=solvers.lp#cvxopt.solvers.lp
            objective = Minimize(-4 * self.x[0] - 5 * self.x[1])
            constraints = [ 2 * self.x[0] + self.x[1] <= 3,
                            self.x[0] + 2 * self.x[1] <= 3,
                            self.x[0] >= 0,
                            self.x[1] >= 0]
            prob = Problem(objective, constraints)
            prob.solve(solver = GUROBI_LIN)
            duals_gurobi_lin = [x.dual_value for x in constraints]
            prob.solve(solver = ECOS)
            duals_ecos = [x.dual_value for x in constraints]
            self.assertItemsAlmostEqual(duals_gurobi_lin, duals_ecos)

        else:
            with self.assertRaises(Exception) as cm:
                prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
                prob.solve(solver = GUROBI_LIN)
            self.assertEqual(str(cm.exception), "The solver %s is not installed." % GUROBI_LIN)

    def test_gurobi_lin_warm_start(self):
        """Make sure that warm starting Gurobi behaves as expected
           Note: This only checks output, not whether or not Gurobi is warm starting internally
        """
        if GUROBI_LIN in installed_solvers():
            import numpy as np

            A = Parameter(2, 2)
            b = Parameter(2)
            h = Parameter(2)
            c = Parameter(2)

            A.value = np.matrix([[1, 0], [0, 0]])
            b.value = np.array([1, 0])
            h.value = np.array([2, 2])
            c.value = np.array([1, 1])

            objective = Maximize(c[0] * self.x[0] + c[1] * self.x[1])
            constraints = [ self.x[0] <= h[0],
                            self.x[1] <= h[1],
                            A * self.x == b]
            prob = Problem(objective, constraints)
            result = prob.solve(solver = GUROBI_LIN, warm_start = True)
            self.assertEqual(result, 3)
            self.assertItemsAlmostEqual(self.x.value, [1, 2])
            orig_objective = result
            orig_x = self.x.value


            # Change A and b from the original values
            A.value = np.matrix([[0, 0], [0, 1]])   # <----- Changed
            b.value = np.array([0, 1])              # <----- Changed
            h.value = np.array([2, 2])
            c.value = np.array([1, 1])

            # Without setting update_eq_constrs = False, the results should change to the correct answer
            result = prob.solve(solver = GUROBI_LIN, warm_start = True)
            self.assertEqual(result, 3)
            self.assertItemsAlmostEqual(self.x.value, [2, 1])


            # Change h from the original values
            A.value = np.matrix([[1, 0], [0, 0]])
            b.value = np.array([1, 0])
            h.value = np.array([1, 1])              # <----- Changed
            c.value = np.array([1, 1])

            # Without setting update_ineq_constrs = False, the results should change to the correct answer
            result = prob.solve(solver = GUROBI_LIN, warm_start = True)
            self.assertEqual(result, 2)
            self.assertItemsAlmostEqual(self.x.value, [1, 1])


            # Change c from the original values
            A.value = np.matrix([[1, 0], [0, 0]])
            b.value = np.array([1, 0])
            h.value = np.array([2, 2])
            c.value = np.array([2, 1])              # <----- Changed

            # Without setting update_objective = False, the results should change to the correct answer
            result = prob.solve(solver = GUROBI_LIN, warm_start = True)
            self.assertEqual(result, 4)
            self.assertItemsAlmostEqual(self.x.value, [1, 2])

        else:
            with self.assertRaises(Exception) as cm:
                prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
                prob.solve(solver = GUROBI_LIN, warm_start = True)
            self.assertEqual(str(cm.exception), "The solver %s is not installed." % GUROBI_LIN)

    def test_installed_solvers(self):
        """Test the list of installed solvers.
        """
        from cvxpy.problems.solvers.utilities import SOLVERS
        prob = Problem(Minimize(norm(self.x, 1)), [self.x == 0])
        for solver in SOLVERS.keys():
            if solver in installed_solvers():
                prob.solve(solver=solver)
                self.assertItemsAlmostEqual(self.x.value, [0, 0])
            else:
                with self.assertRaises(Exception) as cm:
                    prob.solve(solver = solver)
                self.assertEqual(str(cm.exception), "The solver %s is not installed." % solver)
