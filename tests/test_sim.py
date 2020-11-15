# This file is part of the
#   SimulAI Project (https://github.com/carosaav/SimulAI).
# Copyright (c) 2020, Perez Colo Ivo, Pirozzo Bernardo Manuel,
# Carolina Saavedra Sueldo
# License: MIT
#   Full Text: https://github.com/carosaav/SimulAI/blob/master/LICENSE

# ============================================================================
# IMPORTS
# ============================================================================


import pytest
from unittest.mock import patch
import numpy as np
from numpy.testing import assert_equal
from simulai import sim


# ============================================================================
# TESTS
# ============================================================================


@pytest.fixture
def var_input(espera, stock, numviajes):
    vi = [espera, stock, numviajes]

    return vi


@pytest.fixture
def espera():
    espera = sim.DiscreteVariable("Espera", 60, 300, 10,
                                  "Models.Modelo.espera")
    return espera


@pytest.fixture
def stock():
    stock = sim.DiscreteVariable("Stock", 10, 50, 10, "Models.Modelo.stock")

    return stock


@pytest.fixture
def numviajes():
    numviajes = sim.DiscreteVariable(
        "Numero de viajes", 1, 5, 1, "Models.Modelo.numviajes"
    )

    return numviajes


@pytest.fixture
def transportes():
    transportes = sim.OutcomeVariable(
        "Distancia Transportes", "Models.Modelo.transportes", 2, 9
    )
    return transportes


@pytest.fixture
def buffers():
    buffers = sim.OutcomeVariable("Llenado buffers",
                                  "Models.Modelo.buffers", 3, 20)
    return buffers


@pytest.fixture
def salidas():
    salidas = sim.OutcomeVariable(
        "Espera en las Salidas", "Models.Modelo.salidas", 2, 20
    )
    return salidas


@pytest.fixture
def var_out(transportes, buffers, salidas):
    vo = [transportes, buffers, salidas]

    return vo


@pytest.fixture
def my_method_Q(var_input):
    method = sim.Qlearning(v_i=var_input, episodes_max=1, steps_max=10)

    return method


@pytest.fixture
def my_method_S(var_input):
    method = sim.Sarsa(v_i=var_input, episodes_max=1, steps_max=10)

    return method


@pytest.fixture
def base(var_input, var_out, my_method_Q):
    plant = sim.BasePlant(
        method=my_method_Q,
        v_i=var_input,
        v_o=var_out,
        filename="MaterialHandling.spp",
        modelname="Model",
    )

    return plant


@pytest.mark.parametrize(
    "namef, lowf, upf, stf, pathf",
    [
        ("Espera", 60.0, 300, 10, "Models.Modelo.espera"),
        ("Espera", 60, 300.0, 10, "Models.Modelo.espera"),
        ("Espera", 60, 300, 10.0, "Models.Modelo.espera"),
        (["Espera"], 60, 300, 10, "Models.Modelo.espera"),
        ({"e": "Espera"}, 60, 300, 10, "Models.Modelo.espera"),
        ("Espera", 60, 300, (4.5 + 3j), "Models.Modelo.espera"),
        ("Espera", 60, 300, 10, False),
    ],
)
def test_DiscreteVariable(namef, lowf, upf, stf, pathf):
    parm = sim.DiscreteVariable("Espera", 60, 300, 10, "Models.Modelo.espera")

    assert isinstance(parm.name, str), "Should be a string"
    assert isinstance(parm.lower_limit, int), "Should be an integer"
    assert isinstance(parm.upper_limit, int), "Should be an integer"
    assert isinstance(parm.step, int), "Should be an integer"
    assert isinstance(parm.path, str), "Should be a string"

    with pytest.raises(TypeError):
        sim.DiscreteVariable(namef, lowf, upf, stf, pathf)

    with pytest.raises(ValueError):
        sim.DiscreteVariable("Espera", -60, 300, 10, "Models.Modelo.espera")
    with pytest.raises(ValueError):
        sim.DiscreteVariable("Espera", 60, -300, 10, "Models.Modelo.espera")
    with pytest.raises(ValueError):
        sim.DiscreteVariable("Espera", 60, 300, -10, "Models.Modelo.espera")


@pytest.mark.parametrize(
    "namef, pathf, colf, rowf",
    [
        (False, "Model", 2, 9),
        ("Distance", "Model", 2.0, 9),
        ("Distance", True, 2, 9.0),
        (4.2, "Model", 2, 9),
        ("Distance", {"m": "Model"}, 2, 9),
        ("Distance", "Model", 2, "nine"),
    ],
)
def test_OutcomeVariable(namef, pathf, colf, rowf):
    parm = sim.OutcomeVariable("Time", "path", 5, 1)

    assert isinstance(parm.name, str), "Should be a string"
    assert isinstance(parm.path, str), "Should be a string"
    assert isinstance(parm.column, int), "Should be a integer"
    assert isinstance(parm.num_rows, int), "Should be a integer"

    with pytest.raises(TypeError):
        sim.OutcomeVariable(namef, pathf, colf, rowf)

    with pytest.raises(ValueError):
        sim.OutcomeVariable("Time", "path", -5, 1)
    with pytest.raises(ValueError):
        sim.OutcomeVariable("Time", "path", 5, -1)


def test_Plant():
    with pytest.raises(TypeError):
        sim.Plant()


def test_BasePlant(var_input, var_out, my_method_Q):
    b = sim.BasePlant(
        method=my_method_Q,
        v_i=var_input,
        v_o=var_out,
        filename="MaterialHandling.spp",
        modelname="Model",
    )

    assert isinstance(b.v_i, list), "Should be a list"
    assert isinstance(b.v_o, list), "Should be a list"
    assert isinstance(b.filename, str), "Should be a string"
    assert isinstance(b.modelname, str), "Should be a string"

    with pytest.raises(TypeError):
        sim.BasePlant(my_method_Q, 1, var_out, "MH.spp", "frame")
    with pytest.raises(TypeError):
        sim.BasePlant(my_method_Q, var_input, 2.0, "MH.spp", "frame")
    with pytest.raises(TypeError):
        sim.BasePlant(my_method_Q, var_input, var_out, 10, "frame")
    with pytest.raises(TypeError):
        sim.BasePlant(my_method_Q, var_input, var_out, "MH.spp", 10)


def test_get_file_name_plant(base):
    filename = base.get_file_name_plant()

    assert filename == "MaterialHandling.spp"
    assert isinstance(filename, str), "Should be a string"


@patch.object(sim.BasePlant, "update", return_value=np.random.uniform(0, 5))
def test_update(mock_method):
    value = sim.BasePlant.update([60, 10, 1])
    mock_method.assert_called_with([60, 10, 1])

    assert isinstance(value, float), "Should be a float"


def test_Qlearning(var_input):
    ql = sim.Qlearning(v_i=var_input, episodes_max=10, steps_max=10)

    assert isinstance(ql.s, list), "Should be a list"
    assert isinstance(ql.a, list), "Should be a list"
    assert isinstance(ql.v_i, list), "Should be a list"
    assert isinstance(ql.alfa, float), "Should be a float"
    assert isinstance(ql.gamma, float), "Should be a float"
    assert isinstance(ql.epsilon, float), "Should be a float"
    assert isinstance(ql.episodes_max, int), "Should be an integer"
    assert isinstance(ql.steps_max, int), "Should be an integer"
    assert isinstance(ql.r_episode, np.ndarray), "Should be an array"
    assert_equal(len(ql.s), 0)
    assert_equal(len(ql.a), 0)
    assert_equal(ql.alfa, 0.10)
    assert_equal(ql.gamma, 0.90)
    assert_equal(ql.epsilon, 0.10)
    assert_equal(ql.episodes_max, 10)
    assert_equal(ql.steps_max, 10)

    with pytest.raises(TypeError):
        sim.Qlearning("variable", 10, 10)
    with pytest.raises(TypeError):
        sim.Qlearning(var_input, 3.0, 10)
    with pytest.raises(TypeError):
        sim.Qlearning(var_input, 10, "nine")
    with pytest.raises(TypeError):
        sim.Qlearning(var_input, 10, 10, alfa=2)
    with pytest.raises(TypeError):
        sim.Qlearning(var_input, 10, 10, gamma=2)
    with pytest.raises(TypeError):
        sim.Qlearning(var_input, 10, epsilon=2)

    with pytest.raises(Exception):
        sim.Qlearning(
            10, 10, v_i=["espera", "stock", "numviajes",
                         "tiempo", "velocidad"]
        )

    with pytest.raises(ValueError):
        sim.Qlearning(var_input, -1, 10)
    with pytest.raises(ValueError):
        sim.Qlearning(var_input, 10, -1)
    with pytest.raises(ValueError):
        sim.Qlearning(var_input, 10, 10, alfa=-1.0)
    with pytest.raises(ValueError):
        sim.Qlearning(var_input, 10, 10, alfa=3.0)
    with pytest.raises(ValueError):
        sim.Qlearning(var_input, 10, 10, gamma=-1.0)
    with pytest.raises(ValueError):
        sim.Qlearning(var_input, 10, 10, gamma=3.0)
    with pytest.raises(ValueError):
        sim.Qlearning(var_input, 10, 10, epsilon=-1.0)
    with pytest.raises(ValueError):
        sim.Qlearning(var_input, 10, 10, epsilon=3.0)


def test_arrays(var_input):
    q = sim.Qlearning(v_i=var_input, episodes_max=1, steps_max=10)
    q.arrays()
    assert_equal(len(q.s), 3)
    assert_equal(len(q.a), 3)


@pytest.mark.parametrize(
    "var_input, expQ, expS, expA",
    [
        (
            [sim.DiscreteVariable("Espera", 60, 300, 10,
                                  "Models.Modelo.espera")],
            (25, 3),
            (25,),
            (3,),
        ),
        (
            [
                sim.DiscreteVariable("Espera", 60, 300, 10,
                                     "Models.Modelo.espera"),
                sim.DiscreteVariable("Stock", 10, 50, 10,
                                     "Models.Modelo.stock"),
            ],
            (125, 9),
            (125, 2),
            (9, 2),
        ),
        (
            [
                sim.DiscreteVariable("Espera", 60, 300, 10,
                                     "Models.Modelo.espera"),
                sim.DiscreteVariable("Stock", 10, 50, 10,
                                     "Models.Modelo.stock"),
                sim.DiscreteVariable(
                    "Numero de viajes", 1, 5, 1, "Models.Modelo.numviajes"
                ),
            ],
            (625, 27),
            (625, 3),
            (27, 3),
        ),
        (
            [
                sim.DiscreteVariable("Espera", 60, 300, 60,
                                     "Models.Modelo.espera"),
                sim.DiscreteVariable("Stock", 10, 50, 10,
                                     "Models.Modelo.stock"),
                sim.DiscreteVariable(
                    "Numero de viajes", 1, 5, 1, "Models.Modelo.numviajes"
                ),
                sim.DiscreteVariable("Espera", 60, 300, 60,
                                     "Models.Modelo.espera"),
            ],
            (625, 81),
            (625, 4),
            (81, 4),
        ),
    ],
)
def test_ini_saq(var_input, expQ, expS, expA):
    baseM = sim.Qlearning(v_i=var_input, episodes_max=1, steps_max=10)
    baseM.ini_saq()

    assert isinstance(baseM.Q, np.ndarray)
    assert isinstance(baseM.S, np.ndarray)
    assert isinstance(baseM.actions, np.ndarray)
    assert baseM.Q.shape == expQ
    assert baseM.S.shape == expS
    assert baseM.actions.shape == expA
    assert (baseM.Q == 0).all()
    assert bool((baseM.S == 0).all()) is False
    assert bool((baseM.actions == 0).all()) is False

    with pytest.raises(Exception):
        baseM.sim.Qlearning(
            v_i=[
                sim.DiscreteVariable("Espera", 60, 300, 10,
                                     "Models.Modelo.espera"),
                sim.DiscreteVariable("Stock", 10, 50, 10,
                                     "Models.Modelo.stock"),
                sim.DiscreteVariable(
                    "Numero de viajes", 1, 5, 1, "Models.Modelo.numviajes"
                ),
                sim.DiscreteVariable("Espera", 60, 300, 10,
                                     "Models.Modelo.espera"),
                sim.DiscreteVariable("Stock", 10, 50, 10,
                                     "Models.Modelo.stock"),
            ],
            episodes_max=1,
            steps_max=10,
        )
        baseM.ini_saq()


@pytest.mark.parametrize("seed_input, expected", [(24, 0), (20, 0), (12, 0)])
def test_choose_action(var_input, seed_input, expected):
    method = sim.Qlearning(v_i=var_input, episodes_max=1, steps_max=10,
                           seed=seed_input)
    method.ini_saq()
    i = method.choose_action(np.random.randint(624))

    assert_equal(i, expected)


@patch.object(sim.Qlearning, "process", return_value=np.random.uniform(0, 10))
def test_process(mock_method2):
    value = sim.Qlearning.process()
    mock_method2.assert_called_with()

    assert isinstance(value, float), "Should be a float"


def test_Sarsa(var_input):
    ss = sim.Sarsa(v_i=var_input, episodes_max=5, steps_max=20)

    assert isinstance(ss, sim.Qlearning)


@patch.object(sim.Sarsa, "process", return_value=np.random.uniform(0, 10))
def test_process_S(mock_method3):
    value = sim.Sarsa.process()
    mock_method3.assert_called_with()

    assert isinstance(value, float), "Should be a float"


def test_Q_SARSA(my_method_Q, my_method_S):
    method1 = my_method_Q
    method2 = my_method_S

    assert_equal(method1.v_i, method2.v_i)
    assert_equal(method1.episodes_max, method2.episodes_max)
    assert_equal(method1.steps_max, method2.steps_max)
    assert_equal(method1.s, method2.s)
    assert_equal(method1.a, method2.a)
    assert_equal(method1.seed, method2.seed)
    assert_equal(method1.alfa, method2.alfa)
    assert_equal(method1.gamma, method2.gamma)
    assert_equal(method1.epsilon, method2.epsilon)
    assert_equal(method1.r_episode, method2.r_episode)
