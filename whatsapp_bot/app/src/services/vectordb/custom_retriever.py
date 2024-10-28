# import QueryBundle
from llama_index.core import QueryBundle

# import NodeWithScore
from llama_index.core.schema import NodeWithScore

# Retrievers
from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    KeywordTableSimpleRetriever,
)

from typing import List

class CustomRetriever(BaseRetriever):
    """Custom retriever that performs both semantic search and hybrid search.
    
    This retriever combines vector-based (semantic) search with keyword-based search
    to provide more accurate and comprehensive search results. It can operate in two modes:
    'AND' mode (intersection of results) or 'OR' mode (union of results).

    Attributes:
        _vector_retriever (VectorIndexRetriever): Retriever for vector-based semantic search
        _keyword_retriever (KeywordTableSimpleRetriever): Retriever for keyword-based search
        _mode (str): Search combination mode, either 'AND' or 'OR'
    """

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        keyword_retriever: KeywordTableSimpleRetriever,
        mode: str = "AND",
    ) -> None:
        """Initialize the CustomRetriever.

        Args:
            vector_retriever (VectorIndexRetriever): Retriever for vector-based semantic search
            keyword_retriever (KeywordTableSimpleRetriever): Retriever for keyword-based search
            mode (str, optional): Combination mode for search results. 
                'AND': Returns intersection of vector and keyword results
                'OR': Returns union of vector and keyword results
                Defaults to "AND".

        Raises:
            ValueError: If mode is not 'AND' or 'OR'
        """
        self._vector_retriever = vector_retriever
        self._keyword_retriever = keyword_retriever
        if mode not in ("AND", "OR"):
            raise ValueError("Invalid mode.")
        self._mode = mode
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes by combining vector and keyword search results.

        Performs both vector-based and keyword-based searches, then combines the results
        based on the specified mode (AND/OR). If no matches are found in combined search,
        falls back to vector search results.

        Args:
            query_bundle (QueryBundle): The query bundle containing the search query

        Returns:
            List[NodeWithScore]: List of retrieved nodes with their relevance scores
        """
        vector_nodes = self._vector_retriever.retrieve(query_bundle)
        for node in vector_nodes:
            print(node.node.node_id)
        keyword_nodes = self._keyword_retriever.retrieve(query_bundle)
        for node in keyword_nodes:
            print(node.node.node_id)

        vector_ids = {n.node.node_id for n in vector_nodes}
        keyword_ids = {n.node.node_id for n in keyword_nodes}

        combined_dict = {n.node.node_id: n for n in vector_nodes}
        combined_dict.update({n.node.node_id: n for n in keyword_nodes})

        if self._mode == "AND":
            retrieve_ids = vector_ids.intersection(keyword_ids)
        else:
            retrieve_ids = vector_ids.union(keyword_ids)
            
        if not retrieve_ids:
            retrieve_ids = vector_ids

        retrieve_nodes = [combined_dict[rid] for rid in retrieve_ids]
        return retrieve_nodes
