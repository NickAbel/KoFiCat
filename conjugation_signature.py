import re, pickle, hashlib, argparse

class CatalanVerb:
    def __init__(self, infinitive):
        self.infinitive = infinitive
        self.details = {}
        self.transformations = {}

    def add_conjugation(self, tense, conjugation):
        self.details[tense] = conjugation
    
    def set_transformations(self, transformations):
        self.transformations = transformations
    
    def get_transformations(self):
        return f"{self.transformations}"

    def __str__(self):
        return f"{self.infinitive}: {self.transformations}"
    
def extract_transformations(word_a, word_b):
    # Initialize variables
    transformations = []
    stem_length = len(word_a) - 2
    max_length = max(len(word_a), len(word_b))
    word_a = word_a.ljust(max_length)  # Pad the shorter word to match lengths
    word_b = word_b.ljust(max_length)

    # Compare characters from the end to the beginning
    for i in range(0, max_length):
        char_a = word_a[i]
        char_b = word_b[i]
        
        # Check if the characters differ
        if char_a != char_b:
            # Record the transformation
            transformations.append((i - stem_length + 1, char_a, char_b))

    # Return the transformations in the order from the beginning of the word to the end
    return list(transformations)

def parse_verb_block(lines):
    verb = None
    for line in lines:
        if 'INFINITIU:' in line:
            infinitive = re.search(r'INFINITIU: (\w+)', line).group(1)
            verb = CatalanVerb(infinitive)
            transformations = {}
        else:
            tense = line.split(':')[0].strip()
            conjugations = line.split(':')[1].strip().split(', ')
            
            if tense not in transformations:
                transformations[tense] = []
                
            for word in conjugations:
                transformations[tense].append(extract_transformations(infinitive, word))
            verb.add_conjugation(tense, conjugations)
    verb.set_transformations(transformations)
    return verb

def parse_verb_file(filename, verbs):
    current_block = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # non-empty line
                current_block.append(line.strip())
                verb = parse_verb_block(current_block)
                verbs[verb.infinitive] = verb
            elif current_block:  # empty line, end of current block
                current_block = []  # reset for next block
        if current_block:  # if file does not end with empty line
            verb = parse_verb_block(current_block)
            verbs[verb.infinitive] = verb
    return verbs

parser = argparse.ArgumentParser("verbs")
parser.add_argument("infile", help="Verbs input file", type=str)
args = parser.parse_args()

# Example usage
verb_dictionary = {}
verb_dictionary = parse_verb_file(args.infile, verb_dictionary)

transformation_classes = {}
for infinitive, verb_obj in verb_dictionary.items():
    if verb_obj.get_transformations() not in transformation_classes:
        transformation_classes[verb_obj.get_transformations()] = [infinitive]
    else:
        transformation_classes[verb_obj.get_transformations()].append(infinitive)

for map, verbs in transformation_classes.items():
    map_signature = pickle.dumps(map)
    map_hash_object = hashlib.sha3_256()
    map_hash_object.update(map_signature)
    map_hash_digest = map_hash_object.hexdigest()
    print("SHA3-256 hash:", map_hash_digest)
    with open('output/verbmap-'+map_hash_digest+'.out', 'a') as file:
        for verb in verbs:
            file.write(verb+'\n')