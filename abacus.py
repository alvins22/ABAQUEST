import numpy as np

class Abacus:
    def __init__(self, width):
        self.upper = np.zeros((2, width), np.bool_)
        self.upper[0, :] = True

        self.lower = np.zeros((5, width), np.bool_)
        self.lower[1:, :] = True

        self.value_vector = np.array([[5, 0, 0, 1, 2, 3, 4]]).T
        self.value_arr = np.tile(self.value_vector, (1, width))

        self.width = width

    def set_abacus(self, arr):
        self.upper = arr[:2]
        self.lower = arr[2:]

    def select(self, pos):
        if pos[0] < 2:
            arr = self.upper
        else:
            arr = self.lower
            pos = (pos[0]-2, pos[1])

        if arr[pos[0], pos[1]]:
            arr[:, pos[1]] = True
            arr[pos[0], pos[1]] = False

    def return_abacus(self):
        return np.concatenate((self.upper, self.lower), axis=0)

    def num_to_abacus(self, num):
        if len(num) > self.width:
            print("Error: Num too big")
            return
        else:
            num = '0'*(self.width - len(num)) + num
            num = np.array(tuple(num), dtype=np.int8)
            num = np.expand_dims(num, axis=0)
            num_arr = np.tile(num, (7, 1))
            num_arr[0] = (num_arr >= 5)[0]
            num_arr[1] = (num_arr < 5)[1]
            num_arr[num_arr>=5] -= 5
            num_arr[2:] = num_arr[2:] == self.value_vector[2:]
            self.set_abacus(np.logical_not(num_arr))

    def abacus_to_num(self):
        val = np.multiply(self.value_arr, np.logical_not(self.return_abacus()))
        col_sum = np.sum(val, axis=0)
        return int(''.join(str(col_sum).strip('[]').split(' ')))
        

    def reset(self):
        self.upper[0, :] = True
        self.upper[1, :] = False
        self.lower[0, :] = False
        self.lower[1:, :] = True

    def print_abacus(self):
        print(self.upper)
        print(self.lower)
        print(" ")
        print(np.logical_not(self.lower))

# a = Abacus(6)
# a.select((0, 5))
# a.print_abacus()
# print(a.abacus_to_num())
# a.num_to_abacus('642920')
