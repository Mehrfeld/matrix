import numpy as np
import random


class RandomWalker():

    def gen_set(self, ranges=(4, 20), start_value=4, delta=0.1, number_of_points=100):
        lower_range = ranges[0]
        upper_range = ranges[1]
        y = np.array([])
        current_value = start_value

        n = 0
        while n < number_of_points:
            if lower_range < current_value < upper_range:
                current_value = current_value + delta * random.choice([-1, 1])
            elif current_value <= lower_range:
                current_value = current_value + delta
            elif current_value >= upper_range:
                current_value = current_value - delta
            else:
                pass
            y = np.append(y, current_value)
            n = n+1
        return y

    current_single_value = round(random.uniform(4, 20), 3)
    
    def get_single_value(self, ranges=(4, 20), delta=0.1):
        lower_range = ranges[0]
        upper_range = ranges[1]
        if lower_range < self.current_single_value < upper_range:
            self.current_single_value = self.current_single_value + delta * random.choice([-1, 1])
        elif self.current_single_value <= lower_range:
            self.current_single_value = self.current_single_value + delta
        elif self.current_single_value >= upper_range:
            self.current_single_value = self.current_single_value - delta
        else:
            pass
        return self.current_single_value




       




