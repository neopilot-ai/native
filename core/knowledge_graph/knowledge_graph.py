from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# --- Conceptual Knowledge Graph Data Model ---

@dataclass
class KGNode:
    """Represents a node (entity) in the knowledge graph."""
    id: str
    type: str  # e.g., "Concept", "Technology", "Pattern", "BestPractice"
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KGRelationship:
    """Represents a relationship (edge) between two nodes."""
    source_id: str
    target_id: str
    type: str  # e.g., "HAS_PROPERTY", "USES", "RELATED_TO", "IMPLIES"
    properties: Dict[str, Any] = field(default_factory=dict)

# --- Conceptual Knowledge Graph Implementation ---

class KnowledgeGraph:
    """Conceptual implementation of a queryable knowledge graph."""

    def __init__(self):
        self._nodes: Dict[str, KGNode] = {}
        self._relationships: List[KGRelationship] = []

    def add_node(self, node: KGNode):
        """Adds a node to the graph."""
        if node.id in self._nodes:
            print(f"[KG] Warning: Node with ID '{node.id}' already exists. Overwriting.")
        self._nodes[node.id] = node
        print(f"[KG] Added node: {node.type} - {node.id}")

    def add_relationship(self, relationship: KGRelationship):
        """Adds a relationship to the graph."""
        if relationship.source_id not in self._nodes:
            print(f"[KG] Warning: Source node '{relationship.source_id}' not found.")
            return
        if relationship.target_id not in self._nodes:
            print(f"[KG] Warning: Target node '{relationship.target_id}' not found.")
            return
        self._relationships.append(relationship)
        print(f"[KG] Added relationship: {relationship.source_id} -[{relationship.type}]-> {relationship.target_id}")

    def get_node(self, node_id: str) -> Optional[KGNode]:
        """Retrieves a node by its ID."""
        return self._nodes.get(node_id)

    def query_related_nodes(self, node_id: str, relationship_type: Optional[str] = None) -> List[KGNode]:
        """Conceptually queries for nodes related to a given node."""
        related_nodes = []
        for rel in self._relationships:
            if rel.source_id == node_id and (relationship_type is None or rel.type == relationship_type):
                target_node = self.get_node(rel.target_id)
                if target_node:
                    related_nodes.append(target_node)
            elif rel.target_id == node_id and (relationship_type is None or rel.type == relationship_type):
                source_node = self.get_node(rel.source_id)
                if source_node:
                    related_nodes.append(source_node)
        print(f"[KG] Querying related nodes for '{node_id}' (type: {relationship_type or 'any'}): Found {len(related_nodes)}.")
        return related_nodes

    def query_by_property(self, prop_name: str, prop_value: Any) -> List[KGNode]:
        """Conceptually queries for nodes with a specific property value."""
        matching_nodes = []
        for node in self._nodes.values():
            if node.properties.get(prop_name) == prop_value:
                matching_nodes.append(node)
        print(f"[KG] Querying nodes by property '{prop_name}'='{prop_value}': Found {len(matching_nodes)}.")
        return matching_nodes

    def conceptual_reasoning_query(self, query_text: str) -> List[Dict[str, Any]]:
        """Simulates a complex reasoning query on the knowledge graph."
        """In a real system, this would involve graph traversal algorithms, logical inference,
        and potentially integration with LLMs for natural language querying.
        """
        print(f"[KG] Performing conceptual reasoning query: '{query_text}'")
        results = []

        if "best practices for" in query_text.lower():
            concept = query_text.lower().split("best practices for ")[-1].strip().replace(" ", "_")
            related = self.query_related_nodes(concept, "HAS_BEST_PRACTICE")
            if related:
                results.append({"query": query_text, "response": f"Found best practices for {concept}: {[n.id for n in related]}"})
            else:
                results.append({"query": query_text, "response": f"No specific best practices found for {concept}."})

        elif "architectural patterns for" in query_text.lower():
            domain = query_text.lower().split("architectural patterns for ")[-1].strip().replace(" ", "_")
            related = self.query_related_nodes(domain, "HAS_PATTERN")
            if related:
                results.append({"query": query_text, "response": f"Found architectural patterns for {domain}: {[n.id for n in related]}"})
            else:
                results.append({"query": query_text, "response": f"No specific architectural patterns found for {domain}."})

        else:
            results.append({"query": query_text, "response": "Conceptual query processed. In a real KG, this would yield more specific results."})

        return results


if __name__ == "__main__":
    # Demo Usage
    kg = KnowledgeGraph()

    # Add nodes
    print("--- Adding Nodes ---")
    kg.add_node(KGNode("Microservice_Architecture", "Pattern", {"description": "Loose coupling, independent deployment"}))
    kg.add_node(KGNode("Authentication", "Concept", {"domain": "Security"}))
    kg.add_node(KGNode("JWT", "Technology", {"related_to": "Authentication"}))
    kg.add_node(KGNode("Rate_Limiting", "BestPractice", {"domain": "Security", "applies_to": "API"}))
    kg.add_node(KGNode("Scalability", "Concept"))
    kg.add_node(KGNode("Event_Sourcing", "Pattern", {"description": "Capture all changes as a sequence of events"}))

    # Add relationships
    print("\n--- Adding Relationships ---")
    kg.add_relationship(KGRelationship("Microservice_Architecture", "Scalability", "IMPLIES"))
    kg.add_relationship(KGRelationship("Authentication", "JWT", "USES"))
    kg.add_relationship(KGRelationship("API", "Rate_Limiting", "HAS_BEST_PRACTICE"))
    kg.add_relationship(KGRelationship("Microservice_Architecture", "Event_Sourcing", "CAN_USE"))

    # Querying the knowledge graph
    print("\n--- Querying Knowledge Graph ---")
    related_to_auth = kg.query_related_nodes("Authentication")
    print(f"Nodes related to Authentication: {[n.id for n in related_to_auth]}")

    security_concepts = kg.query_by_property("domain", "Security")
    print(f"Security-related concepts: {[n.id for n in security_concepts]}")

    # Conceptual reasoning queries
    print("\n--- Conceptual Reasoning Queries ---")
    kg.conceptual_reasoning_query("best practices for API")
    kg.conceptual_reasoning_query("architectural patterns for distributed systems")
    kg.conceptual_reasoning_query("What is JWT?")
