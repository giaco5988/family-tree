from typing import Dict, Tuple, List, Sequence, Set
import logging
import pandas as pd
import numpy as np

LOGGER = logging.getLogger(__name__)


class Person:
    """
    It defines one person with all direct family connections
    """
    def __init__(self, database_row: pd.Series):
        """
        Initialize person with anagraphic data
        :param database_row: one row of connections dataframe
        """
        self._person_id = int(database_row['id'])
        self._name = database_row['person_name']
        self._mother_id = Person._get_parent_id(database_row['mother_id'])
        self._father_id = Person._get_parent_id(database_row['father_id'])
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

    @staticmethod
    def _get_parent_id(db_value):
        try:
            return db_value if np.isnan(db_value) else int(db_value)
        except TypeError:
            return int(db_value)

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
        tmp = [str(y) for y in sorted(x.person_id for x in self.get_persons_in_node())]

        return "node-" + "-".join(tmp)

    def _list_spouses(self, visited_nodes: Set[int], node_persons: List["Person"], person: "Person") -> List["Person"]:
        """
        List all connection which form a node, also through multiple marriage
        :param visited_nodes: nodes already visited
        :param node_persons: persons in nodes already counted
        :param person: current person
        :return: list of persons already counted
        """
        for spouse in person.spouse:
            if spouse.person_id not in visited_nodes:
                node_persons.append(spouse)
                visited_nodes.add(spouse.person_id)
                node_persons = self._list_spouses(visited_nodes, node_persons, spouse)

        return node_persons

    def get_persons_in_node(self) -> Sequence["Person"]:
        """
        Get all persons in this node
        :return: persons belonging to same node as current person
        """
        return tuple(self._list_spouses({self.person_id}, [self], self))

    def _list_couples(self, visited_couples: Set[Sequence[int]], person: "Person") -> Set[Sequence[int]]:
        """
        Count couples
        :param visited_couples: couples already counted
        :param person: current person
        :return: couples already accounted for
        """
        for spouse in person.spouse:
            couple = tuple(sorted([person.person_id, spouse.person_id]))
            if couple not in visited_couples:
                visited_couples.add(couple)
                visited_couples = self._list_couples(visited_couples, spouse)

        return visited_couples

    def get_couples_in_node(self, persons: Dict[int, "Person"]) -> List[Sequence["Person"]]:
        """
        Get all couples in this node, where this person is
        :param persons: dictionary of (person_id, all-family-persons)
        :return: list of couples
        """
        tmp = self._list_couples(set(), self)

        return [tuple(sorted([persons[y] for y in x], key=lambda x: x.is_male, reverse=True)) for x in tmp]

    @property
    def spouse(self) -> Sequence["Person"]:
        return self._spouses

    def add_parents(self, persons: Dict[str, "Person"]) -> None:
        """
        Add parents among all persons in the family
        :param persons: list of all persons in the family
        :return: None
        """
        parents_ids = tuple([self._father_id, self._mother_id])
        if any(not np.isnan(x) for x in parents_ids):
            tmp = [persons[x] for x in filter(lambda x: not np.isnan(x), parents_ids)]
            self._parents = tuple(sorted(tmp, key=lambda x: x.is_male, reverse=True))
        else:
            self._parents = tuple()

    def add_spouse(self, persons: Dict[str, "Person"]) -> None:
        """
        Add spouse/s from all persons in the family
        :param persons: list of all persons in the family
        :return: None
        """
        self._spouses = tuple([persons[x] for x in self._spouse_ids])

    def add_children(self, persons: List["Person"]) -> None:
        """
        Add children from all persons in the family
        :param persons: list of all persons in the family
        :return: None
        """
        tmp = []
        for person in persons:
            if self._person_id in (person.father_id, person.mother_id):
                tmp.append(person)

        self._children = tuple(tmp)

    def add_siblings(self, persons: List["Person"]) -> None:
        """
        Add siblings and half-siblings from all persons in the family
        :param persons: list of all persons in the family
        :return: None
        """
        tmp_siblings, tmp_half_siblings = [], []
        these_parents = self._father_id, self._mother_id
        for person in persons:
            person_parents = person.father_id, person.mother_id
            if person.person_id != self.person_id:
                tmp = [x == y for x, y in zip(these_parents, person_parents) if not np.isnan(x)]
                if len(tmp) == 2 and all(tmp):
                    tmp_siblings.append(person)
                elif any(tmp):
                    tmp_half_siblings.append(person)

        self._siblings, self._half_siblings = tuple(tmp_siblings), tuple(tmp_half_siblings)


def create_family(df: pd.DataFrame) -> List[Person]:
    """
    Create family connections
    :param df: dataframe with family connections
    :return: list of persons containing connections
    """
    LOGGER.info(f"Create family connections.")
    persons = {row['id']: Person(database_row=row) for _, row in df.iterrows()}

    # create connections
    for person in persons.values():
        person.add_parents(persons)
        person.add_spouse(persons)
        person.add_children(list(persons.values()))
        person.add_siblings(list(persons.values()))

    # sanity checks
    for person in persons.values():
        if len(person.parents) > 0:
            assert persons[person.father_id].is_male, f'Father of {person.person_id} should be male.'
            assert not persons[person.mother_id].is_male, f'Mother of {person.person_id} should be female.'
            assert person.parents[0] in person.parents[1].get_persons_in_node(),\
                f'Parents {person.person_id} not in the same node! Check family connections.'
        if len(person.spouse) > 0:
            assert all(person in x.spouse for x in person.spouse),\
                f"Person id={person.person_id} might not be doubly linked with spouse/s."

    return list(persons.values())


def testing():
    print("ciao")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    testing()
