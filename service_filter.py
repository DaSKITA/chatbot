from config import service_list


class ServiceFilter:

    def __init__(self) -> None:
        self.service_list = service_list

    def filter_services(self, result_dict: list):
        return [node for node in result_dict if self.filter_node(node)]

    def filter_node(self, node: dict):
        return node["node"]["meta"]["name"] in service_list
