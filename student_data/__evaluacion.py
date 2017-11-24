from student_data.__linkedlist import _Node, _LinkedList


class _EvaluItem(_Node):
    def __init__(self, answer: int = None, comment: str = None):
        super().__init__(1)
        self.__answer = None
        self.answer = answer
        self.__comment = None
        self.comment = comment

    @property
    def answer(self):
        return self.__answer

    @property
    def comment(self):
        return self.__comment

    @answer.setter
    def answer(self, value: int):
        if value is None:
            self.__answer = 0
        elif isinstance(value, int):
            self.__answer = value
        else:
            raise TypeError(f'Unexpected type {value.__class__.__name__}, expected int or None')

    @comment.setter
    def comment(self, value):
        if value is None:
            self.__comment = ''
        elif isinstance(value, str):
            self.__comment = self.deparsed(str(value))
        else:
            raise TypeError(f'Unexpected type {value.__class__.__name__}, expected str or None')

    @answer.deleter
    def answer(self):
        del self.__answer

    @comment.deleter
    def comment(self):
        del self.__comment

    def combo_item(self):
        return f'R{self.value}'

    def deparsed(self, comment):
        return '\n'.join(comment.split('[new_line]'))

    def parsed(self, comment):
        return '[new_line]'.join(comment.splitlines())

    def __str__(self):
        return f'{self.answer};{self.parsed(self.comment)}'

    def __repr__(self):
        return f'<R{self.value} -> ' \
               f'Puntaje={self.answer}, ' \
               f'Comentario ={self.comment}>'


class Evaluacion(_LinkedList):
    def __init__(self):
        super().__init__()
        self.__general_comments = None
        self.general_comments = None

    @property
    def general_comments(self):
        return self.__general_comments

    @general_comments.setter
    def general_comments(self, value: str):
        if value is None:
            self.__general_comments = ''
        elif isinstance(value, str):
            self.__general_comments = value
        else:
            raise TypeError(f'Unexpected type {value.__class__.__name__}, expected str or None')

    def append(self, answer: int = None, comment: str = None):
        item = _EvaluItem(answer, comment)
        super().append(item)
        index = len(self) - 1
        if index != 0:
            self[index].value = self[index - 1].value + 1

    def insert(self, index: int, answer: int = None, comment: str = None):
        item = _EvaluItem(answer, comment)
        super().insert(index, item)
        index = self.index(item)
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
        return [item.answer for item in self]

    def check_comma(self, item):
        if item == ',':
            return '\"\",\"\"'
        elif item == '\"':
            return '\"\"'
        else:
            return str(item)

    def __str__(self):
        string = '"'
        for item in self:
            if len(item.comment) > 0:
                value = ''.join(list(map(self.check_comma, list(str(item.value)))))
                comment = ''.join(list(map(self.check_comma, list(item.comment))))
                string += f'R{value} - {comment}\n'
        general_comments = ''.join(list(map(self.check_comma, list(self.general_comments))))
        string += f'{general_comments}"'
        return string


if __name__ == '__main__':
    eval1 = Evaluacion()
    eval1.append(3, 'TESt')
    eval1.append(3, 'awd')
    print(eval1)
    eval1.pop(1)
    print(eval1)
    eval1.append(2, 'Test')
    print(eval1.get_values())
