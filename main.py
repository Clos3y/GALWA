from gaclass import GeneticAlgorithm
import json

if __name__ == "__main__":
    ga_inputs = json.load(open("ga_inputs.json"))
    max_generation_number = ga_inputs['max_generation_number']
    genetic_algorithm = GeneticAlgorithm(
        MaxGenerationNumber=max_generation_number)
    genetic_algorithm.run()