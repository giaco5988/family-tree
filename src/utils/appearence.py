"""
It defines family tree appearance
"""
from abc import abstractmethod
from typing import Tuple, Sequence, List


class AbstractAppearance:
    """
    Interface for family tree appearance
    """

    @staticmethod
    @abstractmethod
    def single_person(person_name: str) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def couple(male_name: str, female_name: str) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def multi_couple(couples: List[Sequence[str]]) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def edge_str(node_name: str, parents_node: str, is_male: bool, num_spouse: int) -> Tuple[str, str]:
        return "", ""


class SimpleAppearance(AbstractAppearance):

    @staticmethod
    def single_person(person_name: str) -> str:
        return f"<f0> {person_name}"

    @staticmethod
    def couple(male_name: str, female_name: str):
        return f'<f0> {male_name} |<f1>|<f2> {female_name}'

    @staticmethod
    def edge_str(node_name: str, parents_node: str, is_male: bool, num_spouse: int) -> Tuple[str, str]:
        place = 'f0' if is_male or num_spouse == 0 else 'f2'
        return f'{parents_node}:f1', f'{node_name}:{place}'

    @staticmethod
    def multi_couple(couples: List[Sequence[str]]) -> str:
        ans = ""
        for ind, (male, female) in enumerate(couples):
            ind_1, ind_2, ind_3 = 3*ind, 3*ind+1, 3*ind+2
            ans = ans + "|" + "{" + f'<f{ind_1}> {male} |<f{ind_2}>|<f{ind_3}> {female}' + "}"
        return "{" + ans[1:] + "}"
