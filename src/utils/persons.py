from typing import Dict, Tuple, List, Sequence, Type
import pandas as pd
import numpy as np
import os
from config import path_config
from graphviz import Digraph, nohtml
from utils.appearence import AbstractAppearance, SimpleAppearance


def test_dot():
    g = Digraph('g',
                filename=os.path.join(path_config.OUTPUT_PATH, 'btree.gv'),
                node_attr={'shape': 'record', 'height': '.1'})

    g.node('node0', nohtml('<f0> NP |<f1>|<f2> NE'))

    g.node('node1', nohtml('<f0> Armando'))
    g.node('node2', nohtml('<f0> Piero|<f1> |<f2> Pina'))
    g.node('node3', nohtml('<f0> Alessandro|<f1> |<f2> Aurora'))

    g.edge('node0:f1', 'node2:f0')
    g.edge('node0:f1', 'node1:f0')
    g.edge('node0:f1', 'node3:f2')

    g.node('node4', nohtml('<f0> Domenico |<f1>|<f2> Patrizia'))
    g.node('node5', nohtml('<f0> Adolfo |<f1>|<f2> Paola'))
    g.node('node6', nohtml('<f0> Umberto |<f1>|<f2> Valentina'))

    g.edge('node3:f1', 'node4:f2')
    g.edge('node3:f1', 'node5:f2')
    g.edge('node3:f1', 'node6:f2')

    g.node('node7', nohtml('<f0> Giacomo'))
    g.node('node8', nohtml('<f0> Giovanni'))
    g.node('node9', nohtml('<f0> Carolina'))
    g.node('node10', nohtml('<f0> Sofia'))

    g.edge('node4:f1', 'node7:f0')
    g.edge('node4:f1', 'node8:f0')
    g.edge('node5:f1', 'node9:f0')
    g.edge('node5:f1', 'node10:f0')

    g.view()


def test_fdo():
    from graphviz import Graph

    g = Graph('G', filename=os.path.join(path_config.OUTPUT_PATH, 'fdpclust.gv'), engine='fdp')

    with g.subgraph(name='cluster_A') as a:
        a.node('NP')
        a.node('NE')

    with g.subgraph(name='clusterB') as c:
        c.node('Alessandro')
        c.node('Aurora')

    with g.subgraph(name='clusterC') as c:
        c.node('Piero')
        c.node('Pina')

    g.edge('Armando', 'cluster_A')
    g.edge('Piero', 'cluster_A')
    g.edge('Aurora', 'cluster_A')

    g.edge('Patrizia', 'clusterB')
    g.edge('Paola', 'clusterB')
    g.edge('Valentina', 'clusterB')

    with g.subgraph(name='clusterD') as c:
        c.node('Domenico')
        c.node('Patrizia')

    g.edge('Giacomo', 'clusterD')
    g.edge('Giovanni', 'clusterD')

    with g.subgraph(name='clusterE') as c:
        c.node('Adolfo')
        c.node('Paola')

    g.edge('Carolina', 'clusterE')
    g.edge('Sofia', 'clusterE')

    with g.subgraph(name='clusterF') as c:
        c.node('Umberto')
        c.node('Valentina')

    g.view()


class Person:
    """"""
    def __init__(self, database_row: pd.Series):
        """"""
        self._person_id = int(database_row['id'])
        self._name = database_row['person_name']
        tmp = database_row['mother_id']
        self._mother_id = tmp if np.isnan(tmp) else int(tmp)
        tmp = database_row['father_id']
        self._father_id = tmp if np.isnan(tmp) else int(tmp)
        self._is_male = database_row['sex'] == "M"
        self._children = None
        self._siblings = None
        self._half_siblings = None
        self._parents = None
        self._spouses = None
        self._spouse_ids = []
        count = 0
        while True:
            count += 1
            col = f"marriage_{count}"
            if col not in database_row.keys():
                break
            else:
                tmp = database_row[col]
                tmp = tmp if np.isnan(tmp) else int(tmp)
                if not np.isnan(tmp):
                    self._spouse_ids.append(tmp)
        self._spouse_ids = tuple(self._spouse_ids)

    @property
    def person_id(self) -> int:
        return self._person_id

    @property
    def is_male(self) -> bool:
        return self._is_male

    @property
    def name(self) -> str:
        return self._name

    @property
    def parents(self) -> Tuple["Person", "Person"]:
        return self._parents

    @property
    def father_id(self) -> int:
        return self._father_id

    @property
    def mother_id(self) -> int:
        return self._mother_id

    def get_node_name(self) -> str:
        """
        Get node name from male to female
        :return:
        """
        tmp = map(lambda x: str(x.person_id), sorted([self, *self._spouses], key=lambda x: x.is_male, reverse=True))

        return "node-" + "-".join(tmp)

    @property
    def spouse(self) -> Sequence["Person"]:
        return self._spouses

    def add_parents(self, persons: Dict[str, "Person"]) -> None:
        """"""
        parents_ids = tuple([self._father_id, self._mother_id])
        if any(not np.isnan(x) for x in parents_ids):
            self._parents = tuple([persons[x] for x in parents_ids])

    def add_spouse(self, persons: Dict[str, "Person"]) -> None:
        """"""
        self._spouses = tuple([persons[x] for x in self._spouse_ids])

    def add_children(self, persons: List["Person"]) -> None:
        """"""
        # TODO: add sanity checks
        tmp = []
        for person in persons:
            if self._person_id in (person.father_id, person.mother_id):
                tmp.append(person)
        self._children = tuple(tmp)

    def add_siblings(self, persons: List["Person"]) -> None:
        """"""
        # TODO: add sanity checks
        tmp_siblings, tmp_half_siblings = [], []
        for person in persons:
            if person.parents is not None and self._parents is not None and person.person_id != self.person_id:
                if all(x is y for x, y in zip(self._parents, person.parents)):
                    tmp_siblings.append(person)
                elif any(x is y for x, y in zip(self._parents, person.parents)):
                    tmp_half_siblings.append(person)

        self._siblings, self._half_siblings = tuple(tmp_siblings), tuple(tmp_half_siblings)


def create_family(df: pd.DataFrame) -> List[Person]:
    """"""
    persons = {}
    for _, row in df.iterrows():
        persons[row['id']] = Person(database_row=row)

    for person in persons.values():
        person.add_parents(persons)
        person.add_spouse(persons)

    for person in persons.values():
        person.add_children(list(persons.values()))

    for person in persons.values():
        person.add_siblings(list(persons.values()))

    return list(persons.values())


def assembly_graph(persons: List[Person], appearance: Type[AbstractAppearance], g: Digraph):
    """"""
    # create nodes
    nodes = set()
    for person in persons:
        tmp = person.get_node_name()
        if tmp not in nodes:
            if len(person.spouse) == 1:
                male = person.name if person.is_male else person.spouse[0].name
                female = person.name if not person.is_male else person.spouse[0].name
                g.node(tmp, nohtml(appearance.couple(male_name=male, female_name=female)))
                nodes.add(tmp)
            elif len(person.spouse) == 0:
                g.node(tmp, nohtml(appearance.single_person(person.name)))
                nodes.add(tmp)
            else:
                return NotImplementedError

    # create edges
    for person in persons:
        if person.parents is not None:
            node_name, parents_node = person.get_node_name(), person.parents[0].get_node_name()
            edge_str = SimpleAppearance.edge_str(node_name, parents_node, person.is_male, len(person.spouse))
            g.edge(edge_str[0], edge_str[1])


def testing():
    df = pd.read_csv('/Users/Giacomo/Downloads/family-tree - connections.csv')
    g = Digraph('g',
                filename=os.path.join(path_config.OUTPUT_PATH, 'btree_custom.gv'),
                node_attr={'shape': 'record', 'height': '.1'})

    # create family
    persons = create_family(df=df)

    # create graph
    assembly_graph(persons, SimpleAppearance, g)

    g.view()


if __name__ == "__main__":
    testing()
