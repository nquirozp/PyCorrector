from student_data.__linkedlist import _Node, _LinkedList


class _RubrItem(_Node):
    def __init__(self, multiplier: int = None, description: str = None, comment: str = None, objective: str = None):
        super().__init__(1)
        self.__objetive = None
        self.__description = None
        self.__comment = None
        if multiplier:
            self.multiplier = multiplier
        else:
            self.multiplier = 3
        self.comment = comment
        self.description = description
        self.objective = objective

    @property
    def description(self):
        return self.__description

    @property
    def objective(self):
        return self.__objetive

    @property
    def comment(self):
        return self.__comment

    @description.setter
    def description(self, value: str):
        if value is None:
            value = ''
        self.__description = str(value)

    @objective.setter
    def objective(self, value: str):
        if value is None:
            value = ''
        self.__objetive = str(value)

    @comment.setter
    def comment(self, value):
        if value is None:
            value = ''
        self.__comment = str(value)

    @description.deleter
    def description(self):
        del self.__description

    @objective.deleter
    def objective(self):
        del self.__objetive

    @comment.deleter
    def comment(self):
        del self.__comment

    def combo_item(self):
        if not self.value:
            raise EnvironmentError('Value not yet assigned.')
        return f'R{self.value}'

    def __str__(self):
        return f'{self.multiplier};{self.objective};{self.description};{self.comment}'

    def __repr__(self):
        return f'<R{self.value} -> ' \
               f'Descripcion={self.description}, ' \
               f'Comentario ={self.comment}, ' \
               f'Multiplicador ={self.multiplier}' \
               f'Objetivo = {self.objective}>'


class Rubrica(_LinkedList):
    def __init__(self):
        super().__init__()

    def append(self, multiplier: int = None, description: str = None, comment: str = None, objective: str = None):
        item = _RubrItem(multiplier, description, comment, objective)
        super().append(item)
        index = len(self) - 1
        if index != 0:
            self[index].value = self[index - 1].value + 1

    def insert(self, index: int,
               multiplier: int = 1
               , description: str = None,
               comment: str = None,
               objective: str = None):
        item = _RubrItem(multiplier, description, comment, objective)
        super().insert(index, item)
        index = self.index(item)
        if index != 0:
            self[index].value = self[index - 1].value + 1
        for item in self[index + 1:]:
            item.value += 1

    def pop(self, index: int = None):
        if index is None:
            index = len(self)
        object_to_pop = super().pop(index)
        for item in self[index:]:
            item.value -= 1
        return object_to_pop

    def get_values(self):
        return [item.description for item in self]

    def load_from_crubr(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            items = file.read().splitlines()
            for item in items:
                data = item.split(';')
                multiplier = int(data[0])
                objective = data[1]
                description = data[2]
                comment = data[3]
                self.append(multiplier, description, comment, objective)

    def get_multipliers(self):
        return [item.multiplier for item in self]

    def save_to_file(self, path):
        with open(path, 'w', encoding='w')as file:
            file.write(str(self))

    def __str__(self):
        string = ''
        for item in self:
            string += f'{item}\n'
        return string.rstrip()

    def __repr__(self):
        return repr([item for item in self])


if __name__ == '__main__':
    rub1 = Rubrica()
    rub1.append(3, 'b', 'c')
    rub1.append(3, 'b', 'c')
    rub1.append()
    rub1[1].description = 'Bla bla'
    rub1[1].comment = 'S'
