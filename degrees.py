import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "small"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        # changed from
        path = [(None, source)] + path
        # to
        # path = path + [(None, target)]
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            # change from
            movie = movies[path[i + 1][0]]["title"]
            # to
            #movie = movies[path[i][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Create fronter for graph node
    fronter = QueueFrontier()
    # Create list to hold explored nodes
    explored = set()
    # Create a list of nodes that currently have connection to parent node
    nodes = set()
 
    # define start node based on user's input source
    start = Node(source, None, people[source]["movies"])
    # goal = Node(target, None, people[target]["movies"])
    # check that start and goal are not the same person
    if start.state == target:
        return None

    # place the start node in the fronter list
    fronter.add(start)
    nodeHasBeenExplored = False
    
    while not fronter.empty():
        parentNode = fronter.remove()
        explored.add(parentNode)
        # get the actions (i.e. movies) that the parentNode has been in
        actions = parentNode.action
        # go through the movie list and identify any other actors that where in the movie
        for movieId in actions:
            connectedStars = movies[movieId]["stars"]
            # go through the list of stars and add to the fronter list.
            for star in connectedStars:
                nodeHasBeenExplored = False
                childNode = Node(star, parentNode, people[star]["movies"])
                #check if the child node is the target goal
                if childNode.state == target:
                    # create an empty list
                    path = []
                    # check if the child node has a parent
                    while childNode.parent != None:
                        # update the path to include next degree
                        movie = set(childNode.parent.action) & set(childNode.action)
                        movieStr = movie.pop()
                        path = path + [(movieStr, childNode.state)]
                        # move to next parent up the shortest path
                        childNode = childNode.parent
                    # reversal of the path list 
                    path.reverse()
                    return path
                for exploredNode in explored:
                    # verify that node has not been explored
                    if childNode.state == exploredNode.state:
                        nodeHasBeenExplored = True
                        break
                    
                if not nodeHasBeenExplored:
                    fronter.add(childNode)

                childNode = None
    # end of actions connect from parent to child nodes.

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
