from student_data.__node import _Node


class _LinkedList:
    def __init__(self):
        self.head: _Node = None
        self.tail: _Node = None

    def append(self, node: _Node):
        if not self.head:
            self.head = node
            self.tail = self.head
        else:
            self.tail.after = node
            self.tail = self.tail.after

    def insert(self, index: int, node: _Node):
        if index == 0 and len(self) == 0:
            self.append(node)
            return
        try:
            if index == 0:
                node.after = self.head
                self.head = node
            else:
                node.after = self[index]
        except IndexError:
            if index == 0 and len(self) == 0 or index == len(self) + 1:
                self.append(node)
            else:
                raise IndexError('Index out of range.')
        if index != 0:
            self[index - 1].after = node

    def pop(self, index: int):
        if index == 0:
            to_return = self.head
            self.head = self[1]
            return to_return
        else:
            to_return = self[index]
            self[index - 1].after = self[index].after
            return to_return

    def index(self, item):
        for i in range(len(self)):
            if self[i] is item:
                return i

    def __getitem__(self, index):
        if isinstance(index, int):
            current = self.head
            if current is None:
                raise IndexError(f'{self.__class__.__name__} out of range')
            for _ in range(index):
                try:
                    current = current.after
                except AttributeError:
                    raise IndexError(f'{self.__class__.__name__} out of range')
            return current
        elif isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            iter_lista = []
            for i in range(start, stop, step):
                iter_lista.append(self[i])
            return list(iter_lista)
        else:
            raise TypeError(f'{self.__class__.__name__} indices must be int or slices, not {index.__class__.__name__}')

    def __iter__(self):
        return iter(self[:])

    def __len__(self):
        counter = 0
        current = self.head
        if current:
            while current:
                counter += 1
                current = current.after
            return counter
        else:
            return 0

    def __str__(self):
        return str(list(self))


if __name__ == '__main__':
    lista1 = _LinkedList()
    node1 = _Node(3)
    lista1.append(node1)
