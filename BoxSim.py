import numpy as np
from enum import Enum


class BoxAlreadyOpened(Exception):
    pass


class Box:

    def __init__(self, hidden_value: int):

        if type(hidden_value) is not int:
            raise ValueError
        self.value = hidden_value
        self.opened = False

    def open_box(self) -> int:
        """
        opens a box, setting its "opened" status to True, and
        revealing the ticket value within.

        :return: the ticket value of the opened box
        """

        self.opened = True

        return self.value

    def reseal_box(self) -> None:

        self.opened = False


class Room:

    def __init__(self):

        self.boxes = [Box(int(number)) for number in np.arange(1, 101)]
        np.random.shuffle(self.boxes)

    def close_boxes(self) -> None:

        for box in self.boxes:
            box.reseal_box()

    def count_boxes_opened(self) -> int:

        counter = 0
        for box in self.boxes:
            if box.opened:
                counter += 1

        return counter

    def get_unopened_boxes(self) -> list:

        open_indices = [index for index, box in zip(np.arange(1, 101), self.boxes) if box.opened is False]
        return open_indices

    def open_box(self, index: int) -> int:
        """
        opens a box determined by the index, and returns the value inside it.

        :param index: value between 1 and 100 to determine the box to open
        :return: ticket number held within the box
        """

        if self.boxes[index-1].opened:
            raise BoxAlreadyOpened(f"Box #{index-1} already opened")
        else:
            return self.boxes[index-1].open_box()


class PrisonerStrategy:

    class Strategy(Enum):
        RANDOM = 0
        FOLLOWER = 1

    def __init__(self,
                 prisoner_strat: Strategy = Strategy.RANDOM
                 ):

        self.strat = (self.random_strategy if prisoner_strat == self.Strategy.RANDOM else
                      self.follower_strategy)

    def random_strategy(self, room: Room, *args) -> int:

        available_boxes = room.get_unopened_boxes()

        return room.open_box(np.random.choice(available_boxes))

    def follower_strategy(self, room: Room, current_value: int) -> int:

        return room.open_box(current_value)


class World:

    def __init__(self, prisoner_strategy: PrisonerStrategy.Strategy):
        self.room = Room()
        self.prisoner_strategy = PrisonerStrategy(prisoner_strategy)

    def reset(self) -> None:
        self.room = Room()

    def run_single_prisoner_instance(self, prisoner_number=24601) -> bool:
        """
        gives a single prisoner his 50 tries to find the right box, using
        the agreed-upon strategy.

        :return: success or failure of the prisoner
        """
        current_value = prisoner_number
        for _ in range(50):
            uncovered_value = self.prisoner_strategy.strat(self.room, current_value)
            if uncovered_value == prisoner_number:
                return True
            current_value = uncovered_value
        return False

    def run_single_strategy_instance(self) -> bool:
        """
        runs a single instance of a strategy to completion, returning True
        if every prisoner attempt is successful, returning False at the first failure
        """

        for index in np.arange(1, 101):
            success = self.run_single_prisoner_instance(prisoner_number=index)
            if not success:
                return False
            self.room.close_boxes()

        return True


def monte_carlo_test(num_samples: int = 1000,
                     strategy: PrisonerStrategy.Strategy = PrisonerStrategy.Strategy.RANDOM
                     ) -> float:

    world = World(prisoner_strategy=strategy)
    results = []
    for _ in range(num_samples):
        world.reset()
        result = world.run_single_strategy_instance()
        results.append(result)

    successes = np.sum(results)
    return successes / len(results)


if __name__ == '__main__':

    success_chance = monte_carlo_test(num_samples=100000,
                                      strategy=PrisonerStrategy.Strategy.FOLLOWER)
    print(f"probability of success: {success_chance*100:.2f}%")
