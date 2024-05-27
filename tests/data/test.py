# This python file has only test purposes.

# Path: tests/data/test.py

# write a class which does some mathemathical operations

class MathOperations:
    """
    A class to perform mathematical operations
    """

    def __init__(self, a, b):
        """
        Initialize the class with two numbers
        params: a: The first number
        params: b: The second number
        """

        self.a = a
        self.b = b

    def add(self):
        """
        Add the two numbers
        returns: The sum of the two numbers
        """

        return self.a + self.b

    def subtract(self):
        """
        Subtract the two numbers
        returns: The difference of the two numbers
        """

        return self.a - self.b

    def multiply(self):
        """
        Multiply the two numbers
        returns: The product of the two numbers
        """

        return self.a * self.b

    def divide(self):
        """
        Divide the two numbers
        returns: The quotient of the two numbers
        """

        return self.a / self.b
