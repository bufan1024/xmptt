
from sqlalchemy import desc
from sqlalchemy_mptt.mixins import BaseNestedSets
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import object_session


class XBaseNestedSets(BaseNestedSets):
    def __init__(self):
        BaseNestedSets.__init__(self)
        self._level = None

    def get_children_nodes(self, session=None):
        """
        get children nodes
        :param session:
        :return: [node1, node2, ...]
        """
        return self.get_children(session=session).all()

    def get_siblings_nodes(self, include_self=False, session=None):
        """
        get siblings nodes
        :param include_self:
        :param session:
        :return: [node1, node2, ...]
        """
        return self.get_siblings(include_self=include_self, session=session).all()

    def leftsibling_node_in_level(self):
        """
        Node to the left of the current node at the same level
        :return:
        """
        return self.leftsibling_in_level()

    @hybrid_method
    def is_descendant_of(self, other):
        """
        Determine whether the current node is a descendant of another node
        :param other:
        :return:
        """
        if self._level is None:
            return (
                    (self.tree_id == other.tree_id)
                    & (self.left <= other.left)
                    & (other.right <= self.right)
            )
        return (
                (self.tree_id == other.tree_id)
                & (self.left <= other.left)
                & (other.right <= self.right)
                & (other.level <= self._level)
        )

    def _drilldown_query_by_level(self, nodes=None):
        """
        get drilldown query by level
        :param nodes:
        :return:
        """
        table = self.__class__
        if not nodes:
            nodes = self._base_query_obj()
        return nodes.filter(self.is_descendant_of(table))

    def drilldown_tree_by_level(self, session=None, json=False, json_fields=None, level=None):
        """
        get drilldown tree by level
        :param session:
        :param json:
        :param json_fields:
        :param level:
        :return:
        """
        if not session:
            session = object_session(self)
        self._level = level
        return self.get_tree(session, json=json, json_fields=json_fields, query=self._drilldown_query_by_level)

    def get_subtree_nodes(self, session=None, include_self=False):
        """
        get subtree nodes
        :param session:
        :param include_self:
        :return:
        """
        table = self.__class__
        query = self._base_query_obj(session=session)
        query = query.filter(table.tree_id == self.tree_id,
                             table.left >= self.left,
                             table.right <= self.right)
        if not include_self:
            query = query.filter(self.get_pk_column() != self.get_pk_value())
        return query.all()

    def get_path_to_root(self, session=None, order=desc):
        """
        get path to root
        :param session:
        :param order:
        :return:
        """
        return self.path_to_root(session=session, order=order).all()
