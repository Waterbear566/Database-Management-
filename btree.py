"""
B-Tree Implementation for Student Database Index
Order: 3 (Minimum degree t=2, maximum 3 keys per node)
Fixed version - no index out of range errors
"""

class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []  # List of keys
        self.children = []  # List of child pointers
        self.leaf = leaf  # True if leaf node
        self.values = []  # List of values (row indices in data table)
    
    def __repr__(self):
        return f"BTreeNode(keys={self.keys}, leaf={self.leaf})"


class BTree:
    def __init__(self, t=2):  # t=2 means order 3
        self.root = BTreeNode(leaf=True)
        self.t = t  # Minimum degree
        self.max_keys = 2 * t - 1  # Maximum keys = 3
        self.min_keys = t - 1  # Minimum keys = 1
    
    def search(self, key, node=None):
        """Search for a key in the B-Tree"""
        if node is None:
            node = self.root
        
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]  # Return the value (row index)
        
        if node.leaf:
            return None
        
        return self.search(key, node.children[i])
    
    def insert(self, key, value):
        """Insert a key-value pair into the B-Tree"""
        root = self.root
        
        if len(root.keys) == self.max_keys:
            # Root is full, split it
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)
    
    def _insert_non_full(self, node, key, value):
        """Insert into a node that is not full"""
        i = len(node.keys) - 1
        
        if node.leaf:
            # Insert in sorted order
            node.keys.append(None)
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            # Find child to insert
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if len(node.children[i].keys) == self.max_keys:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)
    
    def _split_child(self, parent, index):
        """Split a full child node - FIXED VERSION"""
        t = self.t
        full_child = parent.children[index]
        new_child = BTreeNode(leaf=full_child.leaf)
        
        mid_index = t - 1  # For t=2, mid_index = 1
        
        # IMPORTANT: Save the middle key BEFORE modifying the lists
        mid_key = full_child.keys[mid_index]
        mid_value = full_child.values[mid_index]
        
        # Move the second half of keys to new child (keys after middle)
        # For t=2: new_child gets keys[2:] (index 2 onwards)
        new_child.keys = full_child.keys[t:]
        new_child.values = full_child.values[t:]
        
        # Keep only first half in full_child (keys before middle)
        # For t=2: full_child keeps keys[:1] (index 0)
        full_child.keys = full_child.keys[:mid_index]
        full_child.values = full_child.values[:mid_index]
        
        # Move children if not leaf
        if not full_child.leaf:
            new_child.children = full_child.children[t:]
            full_child.children = full_child.children[:t]
        
        # Move middle key up to parent
        parent.keys.insert(index, mid_key)
        parent.values.insert(index, mid_value)
        
        # Add new child to parent
        parent.children.insert(index + 1, new_child)
    
    def delete(self, key):
        """Delete a key from the B-Tree"""
        self._delete_helper(self.root, key)
        
        # If root is empty after deletion, make its only child the new root
        if len(self.root.keys) == 0:
            if not self.root.leaf and len(self.root.children) > 0:
                self.root = self.root.children[0]
    
    def _delete_helper(self, node, key):
        """Helper function for deletion"""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and key == node.keys[i]:
            if node.leaf:
                # Case 1: Key is in leaf node
                node.keys.pop(i)
                node.values.pop(i)
            else:
                # Case 2: Key is in internal node
                self._delete_internal_node(node, key, i)
        elif not node.leaf:
            # Case 3: Key is in subtree
            is_in_subtree = (i == len(node.keys))
            
            if len(node.children[i].keys) < self.t:
                self._fill_child(node, i)
            
            if is_in_subtree and i > len(node.keys):
                self._delete_helper(node.children[i - 1], key)
            else:
                self._delete_helper(node.children[i], key)
    
    def _delete_internal_node(self, node, key, i):
        """Delete key from internal node"""
        if len(node.children[i].keys) >= self.t:
            predecessor = self._get_predecessor(node, i)
            node.keys[i] = predecessor[0]
            node.values[i] = predecessor[1]
            self._delete_helper(node.children[i], predecessor[0])
        elif len(node.children[i + 1].keys) >= self.t:
            successor = self._get_successor(node, i)
            node.keys[i] = successor[0]
            node.values[i] = successor[1]
            self._delete_helper(node.children[i + 1], successor[0])
        else:
            self._merge(node, i)
            self._delete_helper(node.children[i], key)
    
    def _get_predecessor(self, node, i):
        """Get predecessor key from subtree"""
        current = node.children[i]
        while not current.leaf:
            current = current.children[-1]
        return (current.keys[-1], current.values[-1])
    
    def _get_successor(self, node, i):
        """Get successor key from subtree"""
        current = node.children[i + 1]
        while not current.leaf:
            current = current.children[0]
        return (current.keys[0], current.values[0])
    
    def _fill_child(self, node, i):
        """Fill child node if it has fewer than t-1 keys"""
        # Borrow from left sibling
        if i != 0 and len(node.children[i - 1].keys) >= self.t:
            self._borrow_from_left(node, i)
        # Borrow from right sibling
        elif i != len(node.children) - 1 and len(node.children[i + 1].keys) >= self.t:
            self._borrow_from_right(node, i)
        # Merge with sibling
        else:
            if i != len(node.children) - 1:
                self._merge(node, i)
            else:
                self._merge(node, i - 1)
    
    def _borrow_from_left(self, node, child_index):
        """Borrow a key from left sibling"""
        child = node.children[child_index]
        sibling = node.children[child_index - 1]
        
        child.keys.insert(0, node.keys[child_index - 1])
        child.values.insert(0, node.values[child_index - 1])
        
        node.keys[child_index - 1] = sibling.keys.pop()
        node.values[child_index - 1] = sibling.values.pop()
        
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
    
    def _borrow_from_right(self, node, child_index):
        """Borrow a key from right sibling"""
        child = node.children[child_index]
        sibling = node.children[child_index + 1]
        
        child.keys.append(node.keys[child_index])
        child.values.append(node.values[child_index])
        
        node.keys[child_index] = sibling.keys.pop(0)
        node.values[child_index] = sibling.values.pop(0)
        
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
    
    def _merge(self, node, i):
        """Merge child with its sibling"""
        child = node.children[i]
        sibling = node.children[i + 1]
        
        # Pull key from current node and merge with right sibling
        child.keys.append(node.keys[i])
        child.values.append(node.values[i])
        child.keys.extend(sibling.keys)
        child.values.extend(sibling.values)
        
        if not child.leaf:
            child.children.extend(sibling.children)
        
        node.keys.pop(i)
        node.values.pop(i)
        node.children.pop(i + 1)
    
    def traverse(self):
        """Traverse and return all keys in sorted order"""
        result = []
        self._traverse_helper(self.root, result)
        return result
    
    def _traverse_helper(self, node, result):
        """Helper function for traversal"""
        i = 0
        for i in range(len(node.keys)):
            if not node.leaf:
                self._traverse_helper(node.children[i], result)
            result.append((node.keys[i], node.values[i]))
        
        if not node.leaf:
            self._traverse_helper(node.children[i + 1], result)
    
    def get_tree_structure(self):
        """Get tree structure for visualization"""
        return self._get_structure_helper(self.root, 0)
    
    def _get_structure_helper(self, node, level):
        """Helper function to get tree structure"""
        structure = []
        structure.append({
            'level': level,
            'keys': node.keys.copy(),
            'leaf': node.leaf,
            'node_id': id(node)
        })
        
        if not node.leaf:
            for child in node.children:
                structure.extend(self._get_structure_helper(child, level + 1))
        
        return structure
